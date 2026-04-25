# ============================================================
# SuaraRakyat AI — train.py V3.2 BASELINE
# Kaggle-ready
#
# Arsitektur:
# IndoBERTweet encoder
# ├── Category head
# ├── Urgency head
# └── Asta Cita head
#
# Loss:
# 0.40 category + 0.40 urgency + 0.20 asta
#
# Tidak pakai:
# - resize_token_embeddings
# - special token
# - Sastrawi/stemming
# - ordinal urgency
# - uncertainty weighting
# - fold
# ============================================================

import os
import re
import json
import random
import warnings
from dataclasses import dataclass, asdict
from typing import Dict, List

import numpy as np
import pandas as pd
import joblib

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    classification_report,
    confusion_matrix
)

from transformers import (
    AutoTokenizer,
    AutoModel,
    get_linear_schedule_with_warmup
)

from tqdm.notebook import tqdm
from IPython.display import display, HTML

warnings.filterwarnings("ignore")


# ============================================================
# 1. CONFIG
# ============================================================

@dataclass
class TrainConfig:
    csv_path: str = "/kaggle/input/datasets/athillazaidan/best-new-last-bangetco/seed_aspirations_augmented.csv"
    output_dir: str = "/kaggle/working/ml/model/v3.2_baseline"

    model_name: str = "indolem/indobertweet-base-uncased"
    max_length: int = 160
    dropout: float = 0.35

    epochs: int = 20
    batch_size: int = 16
    learning_rate: float = 1e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.10
    max_grad_norm: float = 1.0
    seed: int = 42
    patience: int = 5

    category_loss_weight: float = 0.40
    urgency_loss_weight: float = 0.40
    asta_loss_weight: float = 0.20

    category_class_weight_power: float = 1.00
    urgency_class_weight_power: float = 1.20
    asta_class_weight_power: float = 1.00

    val_size: float = 0.15
    test_size: float = 0.10

    enable_weighted_sampler: bool = True

    boost_sosial: float = 1.35
    boost_kesehatan: float = 1.10
    boost_lingkungan: float = 1.35
    boost_keamanan: float = 1.25

    target_category_f1: float = 0.80
    target_urgency_mae: float = 0.70


CFG = TrainConfig()
os.makedirs(CFG.output_dir, exist_ok=True)


# ============================================================
# 2. UI HELPER
# ============================================================

def banner(title, subtitle=""):
    display(HTML(f"""
    <div style="
        padding:18px;
        border-radius:16px;
        background:linear-gradient(90deg,#020617,#0f172a,#1e293b);
        color:white;
        font-family:Arial;
        margin:14px 0;
        box-shadow:0 4px 16px rgba(0,0,0,0.20);
    ">
        <h2 style="margin:0;font-size:24px;">🚀 {title}</h2>
        <p style="margin:8px 0 0 0;color:#cbd5e1;font-size:14px;">{subtitle}</p>
    </div>
    """))


def status_box(title, items):
    html_items = "".join([f"<li style='margin-bottom:4px;'>{item}</li>" for item in items])
    display(HTML(f"""
    <div style="
        padding:14px 16px;
        border-radius:14px;
        background:#f8fafc;
        border:1px solid #e2e8f0;
        font-family:Arial;
        margin:12px 0;
    ">
        <h3 style="margin:0 0 8px 0;color:#0f172a;">{title}</h3>
        <ul style="margin:0;padding-left:20px;color:#334155;font-size:14px;">
            {html_items}
        </ul>
    </div>
    """))


def progress_text(text):
    display(HTML(f"""
    <div style="
        padding:10px 12px;
        background:#020617;
        color:#a7f3d0;
        border-radius:10px;
        font-family:monospace;
        margin:10px 0;
        border:1px solid #1e293b;
    ">
        ⚡ {text}
    </div>
    """))


def metric_card(epoch, train_metrics, val_metrics, composite_score, best_score):
    display(HTML(f"""
    <div style="
        font-family:Arial;
        margin:14px 0;
        padding:14px;
        border-radius:16px;
        background:#ffffff;
        border:1px solid #e2e8f0;
        box-shadow:0 2px 10px rgba(15,23,42,0.08);
    ">
        <h3 style="margin:0 0 12px 0;color:#0f172a;">📊 Epoch {epoch} Summary</h3>

        <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:10px;">
            <div style="padding:12px;border-radius:12px;background:#ecfeff;border:1px solid #67e8f9;">
                <b>Train Loss</b><br>
                <span style="font-size:22px;">{train_metrics['train_loss']:.4f}</span>
            </div>

            <div style="padding:12px;border-radius:12px;background:#f0fdf4;border:1px solid #86efac;">
                <b>Category F1</b><br>
                <span style="font-size:22px;">{val_metrics['val_category_macro_f1']:.4f}</span>
            </div>

            <div style="padding:12px;border-radius:12px;background:#e0f2fe;border:1px solid #7dd3fc;">
                <b>Category Acc</b><br>
                <span style="font-size:22px;">{val_metrics['val_category_accuracy']:.4f}</span>
            </div>

            <div style="padding:12px;border-radius:12px;background:#fff7ed;border:1px solid #fdba74;">
                <b>Urgency MAE</b><br>
                <span style="font-size:22px;">{val_metrics['val_urgency_mae']:.4f}</span>
            </div>

            <div style="padding:12px;border-radius:12px;background:#f5f3ff;border:1px solid #c4b5fd;">
                <b>Urgency F1</b><br>
                <span style="font-size:22px;">{val_metrics['val_urgency_weighted_f1']:.4f}</span>
            </div>

            <div style="padding:12px;border-radius:12px;background:#fef2f2;border:1px solid #fca5a5;">
                <b>Asta F1</b><br>
                <span style="font-size:22px;">{val_metrics['val_asta_macro_f1']:.4f}</span>
            </div>
        </div>

        <div style="
            margin-top:12px;
            padding:10px 12px;
            border-radius:12px;
            background:#0f172a;
            color:#e2e8f0;
            font-family:monospace;
        ">
            Composite Score: {composite_score:.4f} | Best Score So Far: {best_score:.4f}
        </div>
    </div>
    """))


def final_card(test_metrics):
    cat_f1 = test_metrics["test_category_macro_f1"]
    cat_acc = test_metrics["test_category_accuracy"]
    urg_mae = test_metrics["test_urgency_mae"]
    urg_f1 = test_metrics["test_urgency_weighted_f1"]
    asta_f1 = test_metrics["test_asta_macro_f1"]

    cat_status = "✅ PASS" if cat_f1 >= CFG.target_category_f1 else "⚠️ NEED IMPROVEMENT"
    urg_status = "✅ PASS" if urg_mae <= CFG.target_urgency_mae else "❌ NEED IMPROVEMENT"

    display(HTML(f"""
    <div style="
        padding:18px;
        border-radius:18px;
        background:linear-gradient(90deg,#064e3b,#065f46,#047857);
        color:white;
        font-family:Arial;
        margin:18px 0;
        box-shadow:0 4px 16px rgba(0,0,0,0.20);
    ">
        <h2 style="margin:0 0 12px 0;">🏁 Final Test Result</h2>

        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;">
            <div style="padding:12px;border-radius:12px;background:rgba(255,255,255,0.12);">
                <b>Category F1</b><br>
                <span style="font-size:24px;">{cat_f1:.4f}</span><br>
                <small>{cat_status}</small>
            </div>

            <div style="padding:12px;border-radius:12px;background:rgba(255,255,255,0.12);">
                <b>Category Acc</b><br>
                <span style="font-size:24px;">{cat_acc:.4f}</span>
            </div>

            <div style="padding:12px;border-radius:12px;background:rgba(255,255,255,0.12);">
                <b>Urgency MAE</b><br>
                <span style="font-size:24px;">{urg_mae:.4f}</span><br>
                <small>{urg_status}</small>
            </div>

            <div style="padding:12px;border-radius:12px;background:rgba(255,255,255,0.12);">
                <b>Urgency F1</b><br>
                <span style="font-size:24px;">{urg_f1:.4f}</span>
            </div>

            <div style="padding:12px;border-radius:12px;background:rgba(255,255,255,0.12);">
                <b>Asta F1</b><br>
                <span style="font-size:24px;">{asta_f1:.4f}</span>
            </div>
        </div>
    </div>
    """))


# ============================================================
# 3. SEED & DEVICE
# ============================================================

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = True


set_seed(CFG.seed)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

banner(
    "SuaraRakyat AI Training v3.2 Baseline",
    "IndoBERTweet Multi-Task untuk Category, Urgency, dan Asta Cita."
)

status_box("🧠 Training Setup", [
    f"Device aktif: <b>{DEVICE}</b>",
    f"Base model: <b>{CFG.model_name}</b>",
    f"Epoch: <b>{CFG.epochs}</b>",
    f"Batch size: <b>{CFG.batch_size}</b>",
    f"Learning rate: <b>{CFG.learning_rate}</b>",
    "Asta head: <b>enabled</b>",
    "Asta Cita prefix: <b>enabled</b>",
    "Urgency: <b>CrossEntropy 5-class</b>",
    "Loss: <b>0.40 category + 0.40 urgency + 0.20 asta</b>",
    "Meta-prefix: <b>plain text</b>, tanpa special token dan tanpa resize embedding",
    f"Output directory: <b>{CFG.output_dir}</b>",
])


# ============================================================
# 4. CLEANING TANPA STEMMING
# ============================================================

SLANG_MAP = {
    "gak": "tidak",
    "ga": "tidak",
    "nggak": "tidak",
    "ngga": "tidak",
    "tdk": "tidak",
    "tak": "tidak",
    "blm": "belum",
    "belom": "belum",
    "udh": "sudah",
    "sdh": "sudah",
    "udah": "sudah",
    "bgt": "sangat",
    "banget": "sangat",
    "bngt": "sangat",
    "jln": "jalan",
    "jl": "jalan",
    "yg": "yang",
    "dgn": "dengan",
    "krn": "karena",
    "karna": "karena",
    "utk": "untuk",
    "kpd": "kepada",
    "dr": "dari",
    "sm": "sama",
    "gw": "saya",
    "gue": "saya",
    "gua": "saya",
    "lu": "anda",
    "lo": "anda",
    "rs": "rumah sakit",
    "rsud": "rumah sakit umum daerah",
    "puskes": "puskesmas",
    "pkm": "puskesmas",
    "pskms": "puskesmas",
    "bansos": "bantuan sosial",
    "gmn": "bagaimana",
    "gimana": "bagaimana",
    "knp": "mengapa",
    "parahh": "parah",
    "daruratt": "darurat",
}

PROFANITY_MAP = {
    "anjing": "",
    "bangsat": "",
    "goblok": "",
    "tolol": "",
    "kontol": "",
    "memek": "",
    "babi": "",
}


def normalize_repeated_chars(text: str) -> str:
    return re.sub(r"(.)\1{2,}", r"\1\1", text)


def clean_for_bert(text: str) -> str:
    if pd.isna(text):
        return ""

    text = str(text).strip()
    text = re.sub(r"^[A-Za-z0-9]{6,}\s+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)

    text = text.lower()
    text = normalize_repeated_chars(text)
    text = re.sub(r"([!?.,]){2,}", r"\1", text)
    text = re.sub(r"[^a-zA-Z0-9À-ÿ\s.,!?/-]", " ", text)

    tokens = []
    for tok in text.split():
        tok = tok.strip()
        tok = SLANG_MAP.get(tok, tok)
        tok = PROFANITY_MAP.get(tok, tok)
        if tok:
            tokens.append(tok)

    text = " ".join(tokens)
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ============================================================
# 5. META PREFIX
# ============================================================

def slugify_meta(value: str) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return "unknown"

    value = str(value).lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    if value == "":
        value = "unknown"

    return value


def extract_misi_id(asta_value: str) -> int:
    if pd.isna(asta_value):
        return 0

    text = str(asta_value)

    match = re.search(r"misi\s*(\d+)", text, re.IGNORECASE)
    if match:
        misi_id = int(match.group(1))
        if 1 <= misi_id <= 8:
            return misi_id

    match = re.search(r"\b([1-8])\b", text)
    if match:
        return int(match.group(1))

    return 0


def make_meta_tokens(row: pd.Series) -> str:
    legislative = slugify_meta(row.get("legislative_target", "unknown"))
    impact = slugify_meta(row.get("impact_scope", "unknown"))
    register = slugify_meta(row.get("register", "unknown"))

    misi_id = extract_misi_id(row.get("asta_cita", ""))

    if misi_id > 0:
        misi_text = f"misi {misi_id}"
    else:
        misi_text = "misi unknown"

    return (
        f"legislative target {legislative}. "
        f"asta cita {misi_text}. "
        f"impact scope {impact}. "
        f"register {register}. "
    )


def build_model_input(row: pd.Series) -> str:
    cleaned = clean_for_bert(row["description"])
    meta = make_meta_tokens(row)
    return f"{meta} aspirasi warga: {cleaned}".strip()


# ============================================================
# 6. LOAD DATASET
# ============================================================

def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    progress_text(f"Loading CSV from: {csv_path}")

    df = pd.read_csv(csv_path)

    required_cols = ["description", "category", "urgency"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Kolom wajib tidak ditemukan: {col}")

    before = len(df)
    df = df.dropna(subset=["description", "category", "urgency"]).copy()
    missing_drop = before - len(df)

    df["urgency"] = pd.to_numeric(df["urgency"], errors="coerce")
    df = df.dropna(subset=["urgency"]).copy()
    df["urgency"] = df["urgency"].astype(int)
    df = df[df["urgency"].between(1, 5)].copy()

    before_dup = len(df)
    df = df.drop_duplicates(subset=["description"]).reset_index(drop=True)
    duplicate_drop = before_dup - len(df)

    optional_cols = [
        "register",
        "province",
        "asta_cita",
        "legislative_target",
        "impact_scope",
        "sub_topic",
        "source",
    ]

    for col in optional_cols:
        if col not in df.columns:
            df[col] = "unknown"

    progress_text("Cleaning text and building model input...")

    df["cleaned_description"] = df["description"].apply(clean_for_bert)
    df["misi_id"] = df["asta_cita"].apply(extract_misi_id)
    df["model_input"] = df.apply(build_model_input, axis=1)

    before_clean = len(df)
    df = df[df["cleaned_description"].str.len() >= 10].copy().reset_index(drop=True)
    clean_drop = before_clean - len(df)

    status_box("📦 Dataset Summary", [
        f"Total rows after cleaning: <b>{len(df)}</b>",
        f"Rows dropped because missing critical columns: <b>{missing_drop}</b>",
        f"Duplicate descriptions removed: <b>{duplicate_drop}</b>",
        f"Rows dropped because text too short after cleaning: <b>{clean_drop}</b>",
    ])

    display(HTML("<h3>📌 Category Distribution</h3>"))
    display(df["category"].value_counts().to_frame("count"))

    display(HTML("<h3>📌 Urgency Distribution</h3>"))
    display(df["urgency"].value_counts().sort_index().to_frame("count"))

    display(HTML("<h3>📌 Register Distribution</h3>"))
    display(df["register"].value_counts(dropna=False).to_frame("count"))

    display(HTML("<h3>📌 Misi Distribution</h3>"))
    display(df["misi_id"].value_counts().sort_index().to_frame("count"))

    status_box("🧾 Sample Model Input", [
        df["model_input"].iloc[0]
    ])

    return df


df = load_and_prepare_data(CFG.csv_path)


# ============================================================
# 7. LABEL ENCODING
# ============================================================

progress_text("Encoding labels...")

category_encoder = LabelEncoder()
df["category_label"] = category_encoder.fit_transform(df["category"])

df["urgency_label"] = df["urgency"].astype(int) - 1

df["asta_label"] = df["misi_id"].apply(lambda x: int(x) - 1 if 1 <= int(x) <= 8 else 8)

num_categories = df["category_label"].nunique()
num_urgency = 5
num_asta = 9

category_mapping_items = [
    f"{idx} → {label}" for idx, label in enumerate(category_encoder.classes_)
]

status_box("🏷️ Label Mapping", category_mapping_items + [
    f"num_categories: <b>{num_categories}</b>",
    f"num_urgency: <b>{num_urgency}</b>",
    f"num_asta: <b>{num_asta}</b>",
])


# ============================================================
# 8. TRAIN / VAL / TEST SPLIT
# ============================================================

def make_stratify_key(data: pd.DataFrame) -> pd.Series:
    key = data["category"].astype(str) + "__U" + data["urgency"].astype(str)
    counts = key.value_counts()

    if counts.min() < 2:
        progress_text("Stratify category+urgency terlalu sparse. Fallback ke category.")
        return data["category"]

    return key


progress_text("Splitting dataset into train, validation, and test...")

stratify_key = make_stratify_key(df)

train_df, temp_df = train_test_split(
    df,
    test_size=CFG.val_size + CFG.test_size,
    random_state=CFG.seed,
    stratify=stratify_key
)

relative_test_size = CFG.test_size / (CFG.val_size + CFG.test_size)
temp_stratify_key = make_stratify_key(temp_df)

val_df, test_df = train_test_split(
    temp_df,
    test_size=relative_test_size,
    random_state=CFG.seed,
    stratify=temp_stratify_key
)

train_df = train_df.reset_index(drop=True)
val_df = val_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)

status_box("✂️ Split Size", [
    f"Train: <b>{len(train_df)}</b>",
    f"Validation: <b>{len(val_df)}</b>",
    f"Test: <b>{len(test_df)}</b>",
])


# ============================================================
# 9. TOKENIZER
# ============================================================

progress_text("Loading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(CFG.model_name, use_fast=False)

status_box("🔤 Tokenizer Loaded", [
    "Meta-prefix mode: <b>plain text</b>",
    "Special tokens: <b>disabled</b>",
    "resize_token_embeddings: <b>disabled</b>",
])


# ============================================================
# 10. DATASET CLASS
# ============================================================

class SuaraRakyatDataset(Dataset):
    def __init__(self, data: pd.DataFrame, tokenizer, max_length: int):
        self.data = data.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]

        encoded = self.tokenizer(
            row["model_input"],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        return {
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0),
            "category_label": torch.tensor(row["category_label"], dtype=torch.long),
            "urgency_label": torch.tensor(row["urgency_label"], dtype=torch.long),
            "asta_label": torch.tensor(row["asta_label"], dtype=torch.long),
        }


train_dataset = SuaraRakyatDataset(train_df, tokenizer, CFG.max_length)
val_dataset = SuaraRakyatDataset(val_df, tokenizer, CFG.max_length)
test_dataset = SuaraRakyatDataset(test_df, tokenizer, CFG.max_length)


# ============================================================
# 11. SAMPLER
# ============================================================

def compute_sample_weights(data: pd.DataFrame) -> np.ndarray:
    combo = data["category"].astype(str) + "__U" + data["urgency"].astype(str)
    combo_counts = combo.value_counts().to_dict()

    weights = []

    for _, row in data.iterrows():
        key = str(row["category"]) + "__U" + str(row["urgency"])
        base_w = 1.0 / combo_counts[key]

        category = str(row["category"])
        boost = 1.0

        if category == "Sosial":
            boost *= CFG.boost_sosial
        elif category == "Kesehatan":
            boost *= CFG.boost_kesehatan
        elif category == "Lingkungan":
            boost *= CFG.boost_lingkungan
        elif category == "Keamanan":
            boost *= CFG.boost_keamanan

        if int(row["urgency"]) in [1, 5]:
            boost *= 1.15

        weights.append(base_w * boost)

    weights = np.array(weights, dtype=np.float64)
    weights = weights / weights.sum()

    return weights


progress_text("Preparing DataLoader...")

if CFG.enable_weighted_sampler:
    sample_weights = compute_sample_weights(train_df)

    sampler = WeightedRandomSampler(
        weights=torch.DoubleTensor(sample_weights),
        num_samples=len(sample_weights),
        replacement=True
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=CFG.batch_size,
        sampler=sampler,
        num_workers=2,
        pin_memory=True
    )
else:
    train_loader = DataLoader(
        train_dataset,
        batch_size=CFG.batch_size,
        shuffle=True,
        num_workers=2,
        pin_memory=True
    )

val_loader = DataLoader(
    val_dataset,
    batch_size=CFG.batch_size,
    shuffle=False,
    num_workers=2,
    pin_memory=True
)

test_loader = DataLoader(
    test_dataset,
    batch_size=CFG.batch_size,
    shuffle=False,
    num_workers=2,
    pin_memory=True
)


# ============================================================
# 12. CLASS WEIGHTS
# ============================================================

def make_class_weights(labels: np.ndarray, num_classes: int, power: float = 1.0) -> torch.Tensor:
    counts = np.bincount(labels, minlength=num_classes).astype(np.float32)
    counts = np.maximum(counts, 1.0)

    weights = counts.sum() / (num_classes * counts)
    weights = np.power(weights, power)
    weights = weights / weights.mean()

    return torch.tensor(weights, dtype=torch.float)


category_weights = make_class_weights(
    train_df["category_label"].values,
    num_categories,
    CFG.category_class_weight_power
).to(DEVICE)

urgency_weights = make_class_weights(
    train_df["urgency_label"].values,
    num_urgency,
    CFG.urgency_class_weight_power
).to(DEVICE)

asta_weights = make_class_weights(
    train_df["asta_label"].values,
    num_asta,
    CFG.asta_class_weight_power
).to(DEVICE)

status_box("🏋️ Class Weights Ready", [
    f"Category weights: <code>{np.round(category_weights.detach().cpu().numpy(), 4).tolist()}</code>",
    f"Urgency weights: <code>{np.round(urgency_weights.detach().cpu().numpy(), 4).tolist()}</code>",
    f"Asta weights: <code>{np.round(asta_weights.detach().cpu().numpy(), 4).tolist()}</code>",
])


# ============================================================
# 13. MODEL
# ============================================================

class MultiTaskModel(nn.Module):
    def __init__(
        self,
        model_name: str,
        num_categories: int,
        num_urgency: int = 5,
        num_asta: int = 9,
        dropout: float = 0.35,
    ):
        super().__init__()

        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size

        self.dropout = nn.Dropout(dropout)

        self.category_head = nn.Sequential(
            nn.Linear(hidden_size, 256),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(256, num_categories)
        )

        self.urgency_head = nn.Sequential(
            nn.Linear(hidden_size, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_urgency)
        )

        self.asta_head = nn.Sequential(
            nn.Linear(hidden_size, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_asta)
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )

        cls_embedding = outputs.last_hidden_state[:, 0, :]
        cls_embedding = self.dropout(cls_embedding)

        category_logits = self.category_head(cls_embedding)
        urgency_logits = self.urgency_head(cls_embedding)
        asta_logits = self.asta_head(cls_embedding)

        return {
            "category_logits": category_logits,
            "urgency_logits": urgency_logits,
            "asta_logits": asta_logits,
            "embedding": cls_embedding
        }


progress_text("Loading IndoBERTweet encoder and multi-task heads...")

model = MultiTaskModel(
    model_name=CFG.model_name,
    num_categories=num_categories,
    num_urgency=num_urgency,
    num_asta=num_asta,
    dropout=CFG.dropout,
).to(DEVICE)


# ============================================================
# 14. LOSS, OPTIMIZER, SCHEDULER
# ============================================================

category_criterion = nn.CrossEntropyLoss(weight=category_weights)
urgency_criterion = nn.CrossEntropyLoss(weight=urgency_weights)
asta_criterion = nn.CrossEntropyLoss(weight=asta_weights)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=CFG.learning_rate,
    weight_decay=CFG.weight_decay
)

total_steps = len(train_loader) * CFG.epochs
warmup_steps = int(total_steps * CFG.warmup_ratio)

scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=warmup_steps,
    num_training_steps=total_steps
)

scaler = torch.cuda.amp.GradScaler(enabled=(DEVICE.type == "cuda"))

status_box("⚙️ Optimizer & Scheduler", [
    "Optimizer: <b>AdamW</b>",
    f"Total steps: <b>{total_steps}</b>",
    f"Warmup steps: <b>{warmup_steps}</b>",
    f"Mixed precision: <b>{DEVICE.type == 'cuda'}</b>",
])


def compute_loss(outputs, batch):
    cat_loss = category_criterion(outputs["category_logits"], batch["category_label"])
    urg_loss = urgency_criterion(outputs["urgency_logits"], batch["urgency_label"])
    asta_loss = asta_criterion(outputs["asta_logits"], batch["asta_label"])

    total_loss = (
        CFG.category_loss_weight * cat_loss +
        CFG.urgency_loss_weight * urg_loss +
        CFG.asta_loss_weight * asta_loss
    )

    return total_loss, cat_loss, urg_loss, asta_loss


# ============================================================
# 15. TRAIN & EVALUATE
# ============================================================

def move_batch_to_device(batch: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
    return {k: v.to(DEVICE) for k, v in batch.items()}


def train_one_epoch(epoch: int):
    model.train()

    total_loss = 0.0
    total_cat_loss = 0.0
    total_urg_loss = 0.0
    total_asta_loss = 0.0

    progress_bar = tqdm(
        train_loader,
        desc=f"🔥 Training Epoch {epoch}/{CFG.epochs}",
        leave=False
    )

    for batch in progress_bar:
        batch = move_batch_to_device(batch)

        optimizer.zero_grad(set_to_none=True)

        with torch.cuda.amp.autocast(enabled=(DEVICE.type == "cuda")):
            outputs = model(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"]
            )

            loss, cat_loss, urg_loss, asta_loss = compute_loss(outputs, batch)

        scaler.scale(loss).backward()

        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), CFG.max_grad_norm)

        scaler.step(optimizer)
        scaler.update()
        scheduler.step()

        total_loss += loss.item()
        total_cat_loss += cat_loss.item()
        total_urg_loss += urg_loss.item()
        total_asta_loss += asta_loss.item()

        progress_bar.set_postfix({
            "loss": f"{loss.item():.4f}",
            "cat": f"{cat_loss.item():.4f}",
            "urg": f"{urg_loss.item():.4f}",
            "asta": f"{asta_loss.item():.4f}",
            "lr": f"{scheduler.get_last_lr()[0]:.2e}"
        })

    n = len(train_loader)

    return {
        "train_loss": total_loss / n,
        "train_category_loss": total_cat_loss / n,
        "train_urgency_loss": total_urg_loss / n,
        "train_asta_loss": total_asta_loss / n,
    }


@torch.no_grad()
def evaluate(loader: DataLoader, split_name: str = "val"):
    model.eval()

    losses = []
    cat_losses = []
    urg_losses = []
    asta_losses = []

    all_cat_true = []
    all_cat_pred = []

    all_urg_true = []
    all_urg_pred = []

    all_asta_true = []
    all_asta_pred = []

    progress_bar = tqdm(
        loader,
        desc=f"🔎 Evaluating {split_name}",
        leave=False
    )

    for batch in progress_bar:
        batch = move_batch_to_device(batch)

        outputs = model(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"]
        )

        loss, cat_loss, urg_loss, asta_loss = compute_loss(outputs, batch)

        losses.append(loss.item())
        cat_losses.append(cat_loss.item())
        urg_losses.append(urg_loss.item())
        asta_losses.append(asta_loss.item())

        cat_pred = torch.argmax(outputs["category_logits"], dim=1)
        urg_pred = torch.argmax(outputs["urgency_logits"], dim=1)
        asta_pred = torch.argmax(outputs["asta_logits"], dim=1)

        all_cat_true.extend(batch["category_label"].detach().cpu().numpy().tolist())
        all_cat_pred.extend(cat_pred.detach().cpu().numpy().tolist())

        all_urg_true.extend(batch["urgency_label"].detach().cpu().numpy().tolist())
        all_urg_pred.extend(urg_pred.detach().cpu().numpy().tolist())

        all_asta_true.extend(batch["asta_label"].detach().cpu().numpy().tolist())
        all_asta_pred.extend(asta_pred.detach().cpu().numpy().tolist())

    urg_true_1_5 = np.array(all_urg_true) + 1
    urg_pred_1_5 = np.array(all_urg_pred) + 1

    metrics = {
        f"{split_name}_loss": float(np.mean(losses)),
        f"{split_name}_category_loss": float(np.mean(cat_losses)),
        f"{split_name}_urgency_loss": float(np.mean(urg_losses)),
        f"{split_name}_asta_loss": float(np.mean(asta_losses)),

        f"{split_name}_category_accuracy": accuracy_score(all_cat_true, all_cat_pred),
        f"{split_name}_category_macro_f1": f1_score(all_cat_true, all_cat_pred, average="macro"),
        f"{split_name}_category_weighted_f1": f1_score(all_cat_true, all_cat_pred, average="weighted"),

        f"{split_name}_urgency_accuracy": accuracy_score(all_urg_true, all_urg_pred),
        f"{split_name}_urgency_macro_f1": f1_score(all_urg_true, all_urg_pred, average="macro"),
        f"{split_name}_urgency_weighted_f1": f1_score(all_urg_true, all_urg_pred, average="weighted"),
        f"{split_name}_urgency_mae": mean_absolute_error(urg_true_1_5, urg_pred_1_5),

        f"{split_name}_asta_accuracy": accuracy_score(all_asta_true, all_asta_pred),
        f"{split_name}_asta_macro_f1": f1_score(all_asta_true, all_asta_pred, average="macro"),
        f"{split_name}_asta_weighted_f1": f1_score(all_asta_true, all_asta_pred, average="weighted"),
    }

    raw = {
        "category_true": all_cat_true,
        "category_pred": all_cat_pred,
        "urgency_true": all_urg_true,
        "urgency_pred": all_urg_pred,
        "asta_true": all_asta_true,
        "asta_pred": all_asta_pred,
    }

    return metrics, raw


# ============================================================
# 16. SAVE ARTIFACTS
# ============================================================

def save_artifacts(output_dir: str, epoch: int, metrics: Dict, history: List[Dict]):
    os.makedirs(output_dir, exist_ok=True)

    torch.save(
        model.state_dict(),
        os.path.join(output_dir, "pytorch_model_multitask.bin")
    )

    tokenizer.save_pretrained(output_dir)

    joblib.dump(
        category_encoder,
        os.path.join(output_dir, "label_encoder_category.pkl")
    )

    urgency_mapping = {
        "label_to_id": {str(i): i - 1 for i in range(1, 6)},
        "id_to_label": {str(i - 1): i for i in range(1, 6)}
    }

    with open(os.path.join(output_dir, "label_encoder_urgency.json"), "w", encoding="utf-8") as f:
        json.dump(urgency_mapping, f, ensure_ascii=False, indent=2)

    asta_mapping = {
        "label_to_id": {f"Misi {i}": i - 1 for i in range(1, 9)},
        "id_to_label": {str(i - 1): f"Misi {i}" for i in range(1, 9)},
        "unknown_id": 8
    }

    with open(os.path.join(output_dir, "label_encoder_asta.json"), "w", encoding="utf-8") as f:
        json.dump(asta_mapping, f, ensure_ascii=False, indent=2)

    model_config = {
        "version": "v3.2_baseline",
        "base_model": CFG.model_name,
        "num_categories": num_categories,
        "num_urgency": num_urgency,
        "num_asta": num_asta,
        "max_length": CFG.max_length,
        "dropout": CFG.dropout,
        "category_classes": category_encoder.classes_.tolist(),
        "best_epoch": epoch,
        "best_metrics": metrics,
        "meta_prefix_mode": "plain_text_with_asta_no_special_tokens",
        "checkpoint_file": "pytorch_model_multitask.bin"
    }

    with open(os.path.join(output_dir, "model_config.json"), "w", encoding="utf-8") as f:
        json.dump(model_config, f, ensure_ascii=False, indent=2)

    meta_prefix_config = {
        "format": "legislative target {legislative}. asta cita misi {id}. impact scope {impact}. register {register}. aspirasi warga: {cleaned_description}",
        "asta_cita_in_prefix": True,
        "special_tokens_used": False,
        "tokenizer_resize_used": False
    }

    with open(os.path.join(output_dir, "meta_prefix_config.json"), "w", encoding="utf-8") as f:
        json.dump(meta_prefix_config, f, ensure_ascii=False, indent=2)

    with open(os.path.join(output_dir, "training_history.json"), "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    train_df.to_csv(os.path.join(output_dir, "split_train.csv"), index=False)
    val_df.to_csv(os.path.join(output_dir, "split_val.csv"), index=False)
    test_df.to_csv(os.path.join(output_dir, "split_test.csv"), index=False)

    progress_text(f"Saved best artifacts to: {output_dir}")


# ============================================================
# 17. TRAIN LOOP
# ============================================================

history = []
best_score = -999
best_epoch = 0
best_metrics = None
no_improve = 0

banner(
    "Training Started",
    "Baseline v3.2 dimulai. Checkpoint dipilih berdasarkan composite score asli v3.2."
)

for epoch in range(1, CFG.epochs + 1):
    train_metrics = train_one_epoch(epoch)
    val_metrics, val_raw = evaluate(val_loader, split_name="val")

    composite_score = (
        val_metrics["val_category_macro_f1"] * 0.45
        + val_metrics["val_urgency_weighted_f1"] * 0.35
        - val_metrics["val_urgency_mae"] * 0.20
    )

    epoch_log = {
        "epoch": epoch,
        **train_metrics,
        **val_metrics,
        "composite_score": composite_score,
        "lr": scheduler.get_last_lr()[0],
    }

    history.append(epoch_log)

    metric_card(
        epoch=epoch,
        train_metrics=train_metrics,
        val_metrics=val_metrics,
        composite_score=composite_score,
        best_score=max(best_score, composite_score)
    )

    print("\n" + "-" * 70)
    print(f"Epoch {epoch}/{CFG.epochs}")
    print(f"Train loss       : {train_metrics['train_loss']:.4f}")
    print(f"Val loss         : {val_metrics['val_loss']:.4f}")
    print(f"Val category acc : {val_metrics['val_category_accuracy']:.4f}")
    print(f"Val category F1  : {val_metrics['val_category_macro_f1']:.4f}")
    print(f"Val urgency acc  : {val_metrics['val_urgency_accuracy']:.4f}")
    print(f"Val urgency F1   : {val_metrics['val_urgency_weighted_f1']:.4f}")
    print(f"Val urgency MAE  : {val_metrics['val_urgency_mae']:.4f}")
    print(f"Val asta F1      : {val_metrics['val_asta_macro_f1']:.4f}")
    print(f"Composite score  : {composite_score:.4f}")
    print("-" * 70)

    if composite_score > best_score:
        best_score = composite_score
        best_epoch = epoch
        best_metrics = val_metrics
        no_improve = 0

        save_artifacts(
            output_dir=CFG.output_dir,
            epoch=epoch,
            metrics=val_metrics,
            history=history
        )

        status_box("🏆 New Best Model", [
            f"Best epoch: <b>{epoch}</b>",
            f"Best composite score: <b>{best_score:.4f}</b>",
            f"Val Category F1: <b>{val_metrics['val_category_macro_f1']:.4f}</b>",
            f"Val Urgency MAE: <b>{val_metrics['val_urgency_mae']:.4f}</b>",
            f"Val Asta F1: <b>{val_metrics['val_asta_macro_f1']:.4f}</b>",
        ])
    else:
        no_improve += 1

        status_box("⏳ No Improvement", [
            f"No improvement counter: <b>{no_improve}/{CFG.patience}</b>",
            f"Current composite score: <b>{composite_score:.4f}</b>",
            f"Best composite score: <b>{best_score:.4f}</b>",
        ])

    if no_improve >= CFG.patience:
        banner(
            "Early Stopping Triggered",
            f"Training berhenti di epoch {epoch} karena tidak ada improvement selama {CFG.patience} epoch."
        )
        break


# ============================================================
# 18. FINAL TEST
# ============================================================

banner(
    "Final Evaluation",
    "Loading best checkpoint dan evaluasi pada test set."
)

best_model_path = os.path.join(CFG.output_dir, "pytorch_model_multitask.bin")
model.load_state_dict(torch.load(best_model_path, map_location=DEVICE))
model.to(DEVICE)

test_metrics, test_raw = evaluate(test_loader, split_name="test")

final_card(test_metrics)

print("\n" + "=" * 70)
print("FINAL TEST RESULT")
print("=" * 70)

for k, v in test_metrics.items():
    if isinstance(v, float):
        print(f"{k}: {v:.4f}")
    else:
        print(f"{k}: {v}")

print("\nTARGET CHECK")
cat_f1 = test_metrics["test_category_macro_f1"]
urg_mae = test_metrics["test_urgency_mae"]

print(f"Category Macro F1: {cat_f1:.4f} / target {CFG.target_category_f1}")
print(f"Urgency MAE      : {urg_mae:.4f} / target <= {CFG.target_urgency_mae}")

if cat_f1 >= CFG.target_category_f1:
    print("Category F1: PASS")
else:
    print("Category F1: NEED IMPROVEMENT")

if urg_mae <= CFG.target_urgency_mae:
    print("Urgency MAE: PASS")
else:
    print("Urgency MAE: NEED IMPROVEMENT")


# ============================================================
# 19. REPORTS
# ============================================================

progress_text("Generating reports and error analysis...")

category_names = category_encoder.classes_.tolist()

category_report = classification_report(
    test_raw["category_true"],
    test_raw["category_pred"],
    target_names=category_names,
    output_dict=True,
    zero_division=0
)

urgency_report = classification_report(
    test_raw["urgency_true"],
    test_raw["urgency_pred"],
    target_names=[f"Urgency_{i}" for i in range(1, 6)],
    output_dict=True,
    zero_division=0
)

asta_report = classification_report(
    test_raw["asta_true"],
    test_raw["asta_pred"],
    target_names=[f"Misi_{i}" for i in range(1, 9)] + ["Misi_UNKNOWN"],
    output_dict=True,
    zero_division=0
)

category_cm = confusion_matrix(
    test_raw["category_true"],
    test_raw["category_pred"]
).tolist()

urgency_cm = confusion_matrix(
    test_raw["urgency_true"],
    test_raw["urgency_pred"]
).tolist()

asta_cm = confusion_matrix(
    test_raw["asta_true"],
    test_raw["asta_pred"]
).tolist()

final_results = {
    "config": asdict(CFG),
    "best_epoch": best_epoch,
    "best_val_metrics": best_metrics,
    "test_metrics": test_metrics,
    "category_report": category_report,
    "urgency_report": urgency_report,
    "asta_report": asta_report,
    "category_confusion_matrix": {
        "labels": category_names,
        "matrix": category_cm
    },
    "urgency_confusion_matrix": {
        "labels": [1, 2, 3, 4, 5],
        "matrix": urgency_cm
    },
    "asta_confusion_matrix": {
        "labels": [f"Misi_{i}" for i in range(1, 9)] + ["Misi_UNKNOWN"],
        "matrix": asta_cm
    }
}

with open(os.path.join(CFG.output_dir, "training_results.json"), "w", encoding="utf-8") as f:
    json.dump(final_results, f, ensure_ascii=False, indent=2)

progress_text(f"Saved final training_results.json to {CFG.output_dir}")


# ============================================================
# 20. ERROR ANALYSIS
# ============================================================

def decode_category(label_id: int) -> str:
    return category_encoder.inverse_transform([label_id])[0]


error_rows = []

for i in range(len(test_df)):
    true_cat = test_raw["category_true"][i]
    pred_cat = test_raw["category_pred"][i]

    true_urg = test_raw["urgency_true"][i] + 1
    pred_urg = test_raw["urgency_pred"][i] + 1

    true_asta = test_raw["asta_true"][i]
    pred_asta = test_raw["asta_pred"][i]

    if true_cat != pred_cat or true_urg != pred_urg or true_asta != pred_asta:
        row = test_df.iloc[i]

        error_rows.append({
            "description": row["description"],
            "model_input": row["model_input"],
            "true_category": decode_category(true_cat),
            "pred_category": decode_category(pred_cat),
            "true_urgency": int(true_urg),
            "pred_urgency": int(pred_urg),
            "true_asta": int(true_asta),
            "pred_asta": int(pred_asta),
            "category_error": true_cat != pred_cat,
            "urgency_error": true_urg != pred_urg,
            "asta_error": true_asta != pred_asta,
            "asta_cita": row.get("asta_cita", ""),
            "legislative_target": row.get("legislative_target", ""),
            "impact_scope": row.get("impact_scope", ""),
            "register": row.get("register", ""),
            "source": row.get("source", ""),
        })

error_df = pd.DataFrame(error_rows)

error_path = os.path.join(CFG.output_dir, "error_analysis.csv")
error_df.to_csv(error_path, index=False)

status_box("🧪 Error Analysis Saved", [
    f"Error rows: <b>{len(error_df)}</b>",
    f"Saved to: <b>{error_path}</b>",
])

print("\nTop errors:")
try:
    display(error_df.head(30))
except Exception:
    print(error_df.head(30))


if len(error_df) > 0:
    category_error_pairs = (
        error_df[error_df["category_error"] == True]
        .groupby(["true_category", "pred_category"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    urgency_error_pairs = (
        error_df[error_df["urgency_error"] == True]
        .groupby(["true_urgency", "pred_urgency"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    category_error_pairs.to_csv(
        os.path.join(CFG.output_dir, "category_error_pairs.csv"),
        index=False
    )

    urgency_error_pairs.to_csv(
        os.path.join(CFG.output_dir, "urgency_error_pairs.csv"),
        index=False
    )

    display(HTML("<h3>🔥 Top Category Error Pairs</h3>"))
    display(category_error_pairs.head(20))

    display(HTML("<h3>🔥 Top Urgency Error Pairs</h3>"))
    display(urgency_error_pairs.head(20))


# ============================================================
# 21. FINAL FILE CHECK
# ============================================================

generated_files = []
for root, dirs, files in os.walk(CFG.output_dir):
    for file in files:
        generated_files.append(os.path.join(root, file))

status_box("📁 Generated Artifacts", [
    f"<code>{path}</code>" for path in generated_files
])

banner(
    "Training Pipeline Finished",
    "Ambil folder /kaggle/working/ml/model/v3.2_baseline untuk integrasi ke FastAPI."
)