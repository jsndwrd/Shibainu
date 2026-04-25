"""
clean_pipeline.py v2.0 — SuaraRakyat AI
Disesuaikan untuk seed v3.1 (urgency-balanced, asta_cita contextual)

Perubahan dari v1:
  + Step 3b: Normalisasi legislative_target (49 unique → 3 valid)
  + Step 3c: Normalisasi asta_cita (12 unique → 8 format standar)
  + Step 4 : legislative_target di-validate setelah normalisasi (bukan log-only)
  + Step 6 : Urgency threshold ~20% ±5% (bukan count<10)
"""

import pandas as pd
import re, uuid, json
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────

INPUT_PATH  = "../data/seed_aspirations.csv"
OUTPUT_PATH = "./seed_aspirations_clean.csv"
REPORT_PATH = "./cleaning_report.json"

VALID_CATEGORIES  = ["Infrastruktur","Kesehatan","Pendidikan","Ekonomi","Lingkungan","Keamanan","Sosial"]
VALID_REGISTERS   = ["informal","formal"]
VALID_SCOPES      = ["Individual","Community","Regional","National"]
VALID_URGENCY     = [1,2,3,4,5]
VALID_LEGISLATIVE = ["DPRD Kab/Kota","DPRD Provinsi","DPR RI"]

DESC_MIN_LEN      = 15
DESC_MIN_INFORMAL = 30
DESC_MIN_FORMAL   = 100

FINAL_COL_ORDER = [
    "id","description","category","register","province",
    "urgency","asta_cita","legislative_target","impact_scope","sub_topic","source"
]

ASTA_FULL = {
    1:"Misi 1: Ideologi, Demokrasi, dan HAM",
    2:"Misi 2: Swasembada Pangan, Energi, Air, Ekonomi Hijau dan Biru",
    3:"Misi 3: Lapangan Kerja, Kewirausahaan, dan Infrastruktur",
    4:"Misi 4: SDM, Sains, Teknologi, Pendidikan, Kesehatan",
    5:"Misi 5: Hilirisasi dan Industrialisasi",
    6:"Misi 6: Membangun dari Desa dan Kelurahan untuk Pemerataan Ekonomi",
    7:"Misi 7: Reformasi Hukum, Birokrasi, dan Pemberantasan Korupsi/Narkoba",
    8:"Misi 8: Penyelarasan Kehidupan yang Harmonis dengan Alam dan Budaya",
}
ASTA_KEYWORDS = [
    (1,["ideologi","demokrasi","ham"]),
    (2,["swasembada","pangan","energi","ekonomi hijau","ekonomi biru"]),
    (3,["lapangan kerja","kewirausahaan","infrastruktur"]),
    (4,["sdm","sains","teknologi","pendidikan","kesehatan"]),
    (5,["hilirisasi","industrialisasi"]),
    (6,["membangun dari desa","kelurahan","pemerataan ekonomi"]),
    (7,["reformasi hukum","birokrasi","korupsi","narkoba"]),
    (8,["harmonis","alam dan budaya"]),
]

PRD_TARGETS = {
    "Infrastruktur":150,"Kesehatan":100,"Pendidikan":110,
    "Ekonomi":80,"Lingkungan":60,"Keamanan":60,"Sosial":50
}


# ─── NORMALIZERS ───────────────────────────────────────────────

def normalize_asta_cita(val: str) -> str:
    v = str(val).strip()
    if not v or v.lower() == "nan":
        return ""
    # Format "Misi X: ..." atau "Misi X"
    m = re.match(r"^Misi\s+(\d+)", v, re.I)
    if m:
        return ASTA_FULL.get(int(m.group(1)), v)
    # Fallback: cari keyword
    vl = v.lower()
    for num, kws in ASTA_KEYWORDS:
        if any(k in vl for k in kws):
            return ASTA_FULL[num]
    return v


def normalize_legislative(val: str) -> str:
    v = str(val).strip()
    if v in VALID_LEGISLATIVE:
        return v
    vl = v.lower()
    # Multi-target → level tertinggi
    if "," in v or " dan " in vl:
        return "DPR RI"
    # DPR RI
    if re.match(r"dpr\s*ri$", vl) or vl == "dpr":
        return "DPR RI"
    # DPRD Provinsi
    if re.match(r"dprd?\s+(provinsi|prov\b|daerah istimewa|aceh|jatim|jabar|jateng|bali|banten|lampung|riau|jambi|sumut|sulawesi|kalimantan|papua|ntt|ntb)", vl):
        return "DPRD Provinsi"
    if vl == "dpr provinsi":
        return "DPRD Provinsi"
    # DPRD Kab/Kota — semua varian kabupaten & kota
    if re.match(r"dprd\s+(kabupaten|kab\b|kota)\b", vl):
        return "DPRD Kab/Kota"
    # Fallback DPRD generik
    if vl.startswith("dprd"):
        return "DPRD Kab/Kota"
    return "DPRD Kab/Kota"  # ultimate fallback


# ─── UTILITIES ─────────────────────────────────────────────────

def log(msg): print(f"  {msg}")


# ─── STEPS ─────────────────────────────────────────────────────

def step0_load(path):
    df = pd.read_csv(path)
    report = {
        "generated_at" : datetime.now().isoformat(),
        "input_path"   : path,
        "input_rows"   : len(df),
        "input_columns": df.columns.tolist(),
        "steps"        : {}
    }
    print(f"[LOAD] {len(df)} rows × {len(df.columns)} columns")
    return df, report


def step1_duplicates(df, report):
    print("\n[STEP 1] Duplicate check...")
    before  = len(df)
    dup_id  = df["id"].duplicated().sum()
    dup_desc = df["description"].duplicated().sum()

    if dup_id:
        mask = df["id"].duplicated(keep="first")
        df.loc[mask, "id"] = [str(uuid.uuid4()) for _ in range(mask.sum())]
        log(f"⚠️  {dup_id} duplicate IDs → regenerated")
    else:
        log("✅ No duplicate IDs")

    if dup_desc:
        df = df.drop_duplicates(subset="description", keep="first")
        log(f"⚠️  {dup_desc} duplicate descriptions → dropped (keep first)")
    else:
        log("✅ No duplicate descriptions")

    report["steps"]["s1_duplicates"] = {
        "dup_ids_fixed"   : int(dup_id),
        "dup_desc_dropped": before - len(df),
        "rows_after"      : len(df)
    }
    return df


def step2_nulls(df, report):
    print("\n[STEP 2] Null/missing handling...")
    null_c  = df.isnull().sum().to_dict()
    actions = []
    has_null = {k:v for k,v in null_c.items() if v > 0}

    if not has_null:
        log("✅ No nulls found")
        actions.append("No nulls found")
    else:
        log(f"Null counts: {has_null}")
        for col in ["description","category"]:
            if null_c.get(col,0):
                before = len(df)
                df = df[df[col].notna() & (df[col].astype(str).str.strip() != "")]
                log(f"🗑️  Dropped {before-len(df)} rows: null {col}")
                actions.append(f"Dropped null {col}")
        if null_c.get("urgency",0):
            for cat in df["category"].dropna().unique():
                mask = df["urgency"].isnull() & (df["category"]==cat)
                if not mask.sum(): continue
                med  = df.loc[df["category"]==cat,"urgency"].median()
                fill = int(round(med)) if not pd.isna(med) else 3
                df.loc[mask,"urgency"] = fill
            log("🔧 Imputed null urgency → per-category median")
            actions.append("Imputed null urgency")
        for col, fill in [("register","informal"),("province","Unknown"),("impact_scope","Community")]:
            if null_c.get(col,0):
                df[col] = df[col].fillna(fill)
                log(f"🔧 Filled null {col} → '{fill}'")
                actions.append(f"Filled null {col}")
        for col in ["sub_topic","source","asta_cita","legislative_target"]:
            if col in df.columns and null_c.get(col,0):
                df[col] = df[col].fillna("")
                log(f"🔧 Filled null {col} → ''")
                actions.append(f"Filled null {col}")

    report["steps"]["s2_nulls"] = {"null_counts":null_c,"actions":actions,"rows_after":len(df)}
    return df


def step3_types(df, report):
    print("\n[STEP 3] Type coercion...")
    df["id"]          = df["id"].astype(str).str.strip()
    df["description"] = df["description"].astype(str).str.strip()
    df["urgency"]     = pd.to_numeric(df["urgency"], errors="coerce").astype("Int64")
    for col in ["category","register","province","impact_scope",
                "legislative_target","sub_topic","source","asta_cita"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    log("✅ All types coerced and stripped")
    report["steps"]["s3_types"] = {"rows_after": len(df)}
    return df


def step3b_normalize_legislative(df, report):
    print("\n[STEP 3b] Normalize legislative_target...")
    u_before = df["legislative_target"].nunique()
    df["legislative_target"] = df["legislative_target"].apply(normalize_legislative)
    u_after  = df["legislative_target"].nunique()
    dist     = df["legislative_target"].value_counts().to_dict()
    inv      = (~df["legislative_target"].isin(VALID_LEGISLATIVE)).sum()

    log(f"   {u_before} unique → {u_after} unique | remaining_invalid={inv}")
    for k, v in dist.items():
        log(f"   {k}: {v} ({v/len(df)*100:.1f}%)")

    report["steps"]["s3b_legislative"] = {
        "unique_before": u_before, "unique_after": u_after,
        "distribution" : {k:int(v) for k,v in dist.items()},
        "invalid_remaining": int(inv)
    }
    return df


def step3c_normalize_asta_cita(df, report):
    print("\n[STEP 3c] Normalize asta_cita...")
    u_before = df["asta_cita"].nunique()
    df["asta_cita"] = df["asta_cita"].apply(normalize_asta_cita)
    u_after  = df["asta_cita"].nunique()
    dist     = df["asta_cita"].value_counts().to_dict()
    valid_set = set(ASTA_FULL.values())
    inv       = (~df["asta_cita"].isin(valid_set) & (df["asta_cita"] != "")).sum()

    log(f"   {u_before} unique → {u_after} unique | remaining_invalid={inv}")
    for k, v in sorted(dist.items(), key=lambda x: -x[1]):
        log(f"   {v:4d} ({v/len(df)*100:4.1f}%)  {k}")

    report["steps"]["s3c_asta_cita"] = {
        "unique_before": u_before, "unique_after": u_after,
        "distribution" : {k:int(v) for k,v in dist.items()},
        "invalid_remaining": int(inv)
    }
    return df


def step4_enums(df, report):
    print("\n[STEP 4] Enum validation...")
    drop_mask = pd.Series(False, index=df.index)
    issues    = []

    for field, valid in [("category",VALID_CATEGORIES),
                          ("impact_scope",VALID_SCOPES),
                          ("legislative_target",VALID_LEGISLATIVE)]:
        inv = ~df[field].isin(valid)
        if inv.sum():
            log(f"⚠️  {field}: {inv.sum()} invalid → DROP: {df.loc[inv,field].unique().tolist()}")
            drop_mask |= inv
            issues.append({"field":field,"invalid":int(inv.sum()),"action":"dropped"})
        else:
            log(f"✅ {field} — all valid")

    inv_reg = ~df["register"].isin(VALID_REGISTERS)
    if inv_reg.sum():
        df.loc[inv_reg,"register"] = "informal"
        log(f"⚠️  register: {inv_reg.sum()} invalid → coerced to 'informal'")

    inv_urg = ~df["urgency"].isin(VALID_URGENCY)
    if inv_urg.sum():
        df["urgency"] = df["urgency"].clip(1,5)
        log(f"⚠️  urgency: {inv_urg.sum()} clamped to 1-5")
    else:
        log("✅ urgency — all valid")

    before = len(df)
    df = df[~drop_mask]
    log(f"🗑️  Dropped {before-len(df)} rows total")

    report["steps"]["s4_enums"] = {"issues":issues,"dropped":before-len(df),"rows_after":len(df)}
    return df


def step5_description_quality(df, report):
    print("\n[STEP 5] Description quality filter...")
    drop_mask = pd.Series(False, index=df.index)
    flags     = []

    ts = df["description"].str.len() < DESC_MIN_LEN
    if ts.sum(): drop_mask|=ts; flags.append(f"{ts.sum()} rows <{DESC_MIN_LEN} chars global")

    for reg, ml in [("informal",DESC_MIN_INFORMAL),("formal",DESC_MIN_FORMAL)]:
        m = (df["register"]==reg) & (df["description"].str.len()<ml)
        if m.sum(): drop_mask|=m; flags.append(f"{m.sum()} {reg} <{ml} chars")

    na = ~df["description"].str.contains(r'[a-zA-Z]', regex=True, na=False)
    if na.sum(): drop_mask|=na; flags.append(f"{na.sum()} no-alpha rows")

    before = len(df)
    df = df[~drop_mask]

    if flags:
        for f in flags: log(f"⚠️  {f} → dropped")
    else:
        log("✅ All descriptions pass quality checks")
    log(f"🗑️  Dropped {before-len(df)} rows total")

    report["steps"]["s5_description"] = {"flags":flags,"dropped":before-len(df),"rows_after":len(df)}
    return df


def step6_urgency_balance(df, report):
    """v2: threshold ~20% ±5%, bukan count<10."""
    print("\n[STEP 6] Urgency balance check (target ~20% per level)...")
    dist  = df["urgency"].value_counts().sort_index().to_dict()
    total = len(df)
    warnings = []

    for lvl in VALID_URGENCY:
        cnt = dist.get(lvl, 0)
        pct = cnt / total * 100
        bar = "█" * int(pct / 2)
        ok  = 15 <= pct <= 25
        log(f"{'✅' if ok else '⚠️ '} urgency={lvl}: {cnt:4d} ({pct:.1f}%) {bar}")
        if not ok:
            warnings.append({"urgency":lvl,"count":cnt,"pct":round(pct,2),"status":"imbalanced"})

    if not warnings:
        log("✅ Urgency distribution balanced")

    report["steps"]["s6_urgency"] = {
        "distribution": {str(k):int(v) for k,v in dist.items()},
        "warnings": warnings
    }
    return df


def step7_category_distribution(df, report):
    print("\n[STEP 7] Category distribution vs PRD targets...")
    actual = df["category"].value_counts().to_dict()
    shortfalls, formal_warn = [], []

    for cat, tgt in PRD_TARGETS.items():
        cnt  = actual.get(cat, 0)
        diff = cnt - tgt
        log(f"{'✅' if diff>=0 else '⚠️ '} {cat}: {cnt}/{tgt} (diff={diff:+d})")
        if diff < 0:
            shortfalls.append({"category":cat,"actual":cnt,"target":tgt,"shortfall":abs(diff)})

    print()
    log("Formal % per category (target 15–25%):")
    for cat in VALID_CATEGORIES:
        sub = df[df["category"]==cat]
        if not len(sub): continue
        pct = len(sub[sub["register"]=="formal"]) / len(sub) * 100
        ok  = 15 <= pct <= 25
        log(f"   {'✅' if ok else '⚠️ '} {cat}: {pct:.1f}%")
        if not ok:
            formal_warn.append({"category":cat,"formal_pct":round(pct,2)})

    report["steps"]["s7_category"] = {
        "actual"          : {k:int(v) for k,v in actual.items()},
        "targets"         : PRD_TARGETS,
        "shortfalls"      : shortfalls,
        "formal_pct_warnings": formal_warn
    }
    return df


def step8_finalize(df, report):
    print("\n[STEP 8] Finalize & save...")
    final_cols = [c for c in FINAL_COL_ORDER if c in df.columns]
    df = df[final_cols].reset_index(drop=True)

    df.to_csv(OUTPUT_PATH, index=False)
    log(f"✅ Saved → {OUTPUT_PATH}")

    report["output_rows"]    = len(df)
    report["output_columns"] = df.columns.tolist()
    report["rows_removed"]   = report["input_rows"] - len(df)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log(f"✅ Report → {REPORT_PATH}")
    return df


# ─── MAIN ──────────────────────────────────────────────────────

def run():
    print("=" * 60)
    print("  seed_aspirations.csv — Cleaning Pipeline v2.0")
    print("=" * 60)

    df, report = step0_load(INPUT_PATH)
    df = step1_duplicates(df, report)
    df = step2_nulls(df, report)
    df = step3_types(df, report)
    df = step3b_normalize_legislative(df, report)   # NEW
    df = step3c_normalize_asta_cita(df, report)     # NEW
    df = step4_enums(df, report)
    df = step5_description_quality(df, report)
    df = step6_urgency_balance(df, report)          # UPDATED
    df = step7_category_distribution(df, report)
    df = step8_finalize(df, report)

    print("\n" + "=" * 60)
    print(f"  DONE: {report['input_rows']} → {report['output_rows']} rows")
    print(f"  Removed: {report['rows_removed']} rows")
    print("=" * 60)


if __name__ == "__main__":
    run()