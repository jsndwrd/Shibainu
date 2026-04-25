import json
import hashlib
import random
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer


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
            nn.Linear(256, num_categories),
        )

        # Urgency head tetap ada karena checkpoint training punya head ini,
        # tapi output urgency tidak dipakai di sistem final.
        self.urgency_head = nn.Sequential(
            nn.Linear(hidden_size, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_urgency),
        )

        self.asta_head = nn.Sequential(
            nn.Linear(hidden_size, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_asta),
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True,
        )

        cls_embedding = outputs.last_hidden_state[:, 0, :]
        cls_embedding = self.dropout(cls_embedding)

        return {
            "category_logits": self.category_head(cls_embedding),
            "urgency_logits": self.urgency_head(cls_embedding),
            "asta_logits": self.asta_head(cls_embedding),
            "embedding": cls_embedding,
        }


class EmbedderService:
    def __init__(self, db=None):
        self.db = db

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.base_dir = Path(__file__).resolve().parents[1]
        self.model_dir = self.base_dir / "models_ai"
        self.weight_path = self.model_dir / "pytorch_model_multitask.bin"
        self.config_path = self.model_dir / "model_config.json"
        self.category_encoder_path = self.model_dir / "label_encoder_category.pkl"

        self.model = None
        self.tokenizer = None
        self.category_encoder = None
        self.model_config = None
        self.model_loaded = False

        self._try_load_model()

    def _try_load_model(self):
        try:
            if not self.weight_path.exists():
                print("[EmbedderService] pytorch_model_multitask.bin not found. Using fallback mode.")
                return

            if not self.config_path.exists():
                print("[EmbedderService] model_config.json not found. Using fallback mode.")
                return

            with open(self.config_path, "r", encoding="utf-8") as f:
                self.model_config = json.load(f)

            base_model = self.model_config.get(
                "base_model",
                "indolem/indobertweet-base-uncased",
            )

            num_categories = int(self.model_config.get("num_categories", 7))
            num_urgency = int(self.model_config.get("num_urgency", 5))
            num_asta = int(self.model_config.get("num_asta", 9))
            dropout = float(self.model_config.get("dropout", 0.35))

            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_dir),
                use_fast=False,
            )

            self.category_encoder = joblib.load(self.category_encoder_path)

            self.model = MultiTaskModel(
                model_name=base_model,
                num_categories=num_categories,
                num_urgency=num_urgency,
                num_asta=num_asta,
                dropout=dropout,
            )

            state = torch.load(
                self.weight_path,
                map_location=self.device,
            )

            self.model.load_state_dict(state)
            self.model.to(self.device)
            self.model.eval()

            self.model_loaded = True
            print("[EmbedderService] AI model loaded successfully.")

        except Exception as e:
            print(f"[EmbedderService] Failed to load AI model. Using fallback mode. Error: {e}")
            self.model_loaded = False

    def _build_model_input(
        self,
        text: str,
        legislative_target: str = "unknown",
        impact_scope: str = "unknown",
        register: str = "informal",
        asta_cita: str = "misi unknown",
    ) -> str:
        return (
            f"legislative target {legislative_target}. "
            f"asta cita {asta_cita}. "
            f"impact scope {impact_scope}. "
            f"register {register}. "
            f"aspirasi warga: {text}"
        ).strip()

    def _predict_with_model(self, text: str) -> Dict:
        model_input = self._build_model_input(text)

        encoded = self.tokenizer(
            model_input,
            max_length=int(self.model_config.get("max_length", 160)),
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        input_ids = encoded["input_ids"].to(self.device)
        attention_mask = encoded["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )

            category_probs = torch.softmax(outputs["category_logits"], dim=1)
            asta_probs = torch.softmax(outputs["asta_logits"], dim=1)

            category_id = int(torch.argmax(category_probs, dim=1).item())
            asta_id = int(torch.argmax(asta_probs, dim=1).item())

            category_confidence = float(category_probs[0, category_id].item())
            asta_confidence = float(asta_probs[0, asta_id].item())

            category = self.category_encoder.inverse_transform([category_id])[0]

            if 0 <= asta_id <= 7:
                asta_cita = f"Misi {asta_id + 1}"
            else:
                asta_cita = "Misi UNKNOWN"

            embedding = outputs["embedding"][0].detach().cpu().numpy().tolist()

        return {
            "category": category,
            "category_confidence": round(category_confidence, 4),
            "asta_cita": asta_cita,
            "asta_confidence": round(asta_confidence, 4),
            "embedding": [float(x) for x in embedding],
            "model_source": "indobertweet_v3.2",
        }

    def _fallback_category(self, text: str) -> str:
        text = (text or "").lower()

        keyword_map = {
            "Infrastruktur": [
                "jalan", "jembatan", "drainase", "lampu jalan", "trotoar",
                "aspal", "berlubang", "irigasi", "akses desa",
            ],
            "Kesehatan": [
                "rumah sakit", "puskesmas", "dokter", "obat", "bpjs",
                "ambulans", "pasien", "posyandu", "stunting",
            ],
            "Pendidikan": [
                "sekolah", "guru", "siswa", "murid", "kelas", "kampus",
                "kuliah", "buku", "beasiswa",
            ],
            "Lingkungan": [
                "banjir", "sampah", "limbah", "polusi", "pencemaran",
                "sungai", "asap", "hutan",
            ],
            "Ekonomi": [
                "harga", "sembako", "beras", "pasar", "umkm",
                "pengangguran", "lapangan kerja", "pupuk", "bbm",
            ],
            "Keamanan": [
                "begal", "maling", "pencurian", "tawuran", "narkoba",
                "preman", "kriminal", "polisi",
            ],
            "Sosial": [
                "bansos", "bantuan sosial", "pkh", "blt", "lansia",
                "disabilitas", "miskin", "kelaparan",
            ],
        }

        scores = {}

        for category, keywords in keyword_map.items():
            scores[category] = sum(1 for keyword in keywords if keyword in text)

        best_category = max(scores, key=scores.get)

        if scores[best_category] == 0:
            return "Sosial"

        return best_category

    def _fallback_asta(self, text: str, category: str) -> Dict:
        text = (text or "").lower()

        if category in ["Kesehatan", "Pendidikan"]:
            return {"asta_cita": "Misi 4", "asta_confidence": 0.86}

        if category == "Infrastruktur":
            if "desa" in text or "kelurahan" in text:
                return {"asta_cita": "Misi 6", "asta_confidence": 0.84}
            return {"asta_cita": "Misi 3", "asta_confidence": 0.82}

        if category == "Ekonomi":
            if any(k in text for k in ["pangan", "beras", "pupuk", "petani", "nelayan"]):
                return {"asta_cita": "Misi 2", "asta_confidence": 0.84}
            if any(k in text for k in ["industri", "pabrik", "hilirisasi"]):
                return {"asta_cita": "Misi 5", "asta_confidence": 0.80}
            return {"asta_cita": "Misi 3", "asta_confidence": 0.78}

        if category == "Lingkungan":
            return {"asta_cita": "Misi 8", "asta_confidence": 0.82}

        if category == "Keamanan":
            if "narkoba" in text or "korupsi" in text:
                return {"asta_cita": "Misi 7", "asta_confidence": 0.82}
            return {"asta_cita": "Misi 1", "asta_confidence": 0.80}

        if category == "Sosial":
            if any(k in text for k in ["desa", "kelurahan", "bansos", "pkh", "blt"]):
                return {"asta_cita": "Misi 6", "asta_confidence": 0.78}
            return {"asta_cita": "Misi 1", "asta_confidence": 0.76}

        return {"asta_cita": "Misi UNKNOWN", "asta_confidence": 0.30}

    def _fallback_embedding(self, text: str) -> List[float]:
        seed = int(hashlib.md5((text or "").encode("utf-8")).hexdigest(), 16) % 100000
        random.seed(seed)
        return [round(random.random(), 6) for _ in range(768)]

    def _predict_fallback(self, text: str) -> Dict:
        category = self._fallback_category(text)
        asta = self._fallback_asta(text, category)

        return {
            "category": category,
            "category_confidence": 0.70,
            "asta_cita": asta["asta_cita"],
            "asta_confidence": asta["asta_confidence"],
            "embedding": self._fallback_embedding(text),
            "model_source": "fallback_rule_based",
        }

    def predict_all(self, text: str) -> Dict:
        if self.model_loaded:
            return self._predict_with_model(text)

        return self._predict_fallback(text)

    def predictAll(self, text: str) -> Dict:
        return self.predict_all(text)