"""
clean_pipeline.py
Pipeline cleaning seed_aspirations.csv → sesuai PRD + keputusan dataset

Keputusan schema:
  - legislative_target   : RETAIN as-is (tidak di-remap ke Regency/Provincial/National)
  - asta_cita            : RETAIN (kolom tambahan, valid untuk pipeline)
  - max char description : SKIP (tidak di-enforce, hanya min length yang di-check)
"""

import pandas as pd
import re
import uuid
import json
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────

INPUT_PATH  = "../data/seed_aspirations.csv"
OUTPUT_PATH = "./seed_aspirations_clean.csv"
REPORT_PATH = "./cleaning_report.json"

VALID_CATEGORIES       = ["Infrastruktur","Kesehatan","Pendidikan","Ekonomi","Lingkungan","Keamanan","Sosial"]
VALID_REGISTERS        = ["informal","formal"]
VALID_SCOPES           = ["Individual","Community","Regional","National"]
VALID_URGENCY          = [1, 2, 3, 4, 5]
VALID_LEGISLATIVE      = ["DPRD Kab/Kota","DPRD Provinsi","DPR RI"]  # pakai format CSV as-is

DESC_MIN_LEN           = 15   # PRD Section 3.5: global minimum
DESC_MIN_INFORMAL      = 30   # PRD Section 3.4: informal min
DESC_MIN_FORMAL        = 100  # PRD Section 3.4: formal min
# Max char: tidak di-enforce (keputusan user)

# Final column order (ikut CSV + tambahan asta_cita dipertahankan)
FINAL_COL_ORDER = [
    "id", "description", "category", "register", "province",
    "urgency", "asta_cita", "legislative_target", "impact_scope",
    "sub_topic", "source"
]


# ─── UTILITIES ────────────────────────────────────────────────────────────────

def log(msg): print(f"  {msg}")

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except Exception:
        return False


# ─── STEP 0: LOAD ─────────────────────────────────────────────────────────────

def step0_load(path: str) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(path)
    report = {
        "generated_at" : datetime.now().isoformat(),
        "input_path"   : path,
        "input_rows"   : len(df),
        "input_columns": df.columns.tolist(),
        "steps"        : {}
    }
    print(f"[LOAD] {len(df)} rows × {len(df.columns)} columns")
    print(f"       {df.columns.tolist()}")
    return df, report


# ─── STEP 1: DUPLICATE CHECK ──────────────────────────────────────────────────

def step1_duplicates(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    print("\n[STEP 1] Duplicate check...")
    before = len(df)

    dup_id   = df["id"].duplicated().sum()
    dup_desc = df["description"].duplicated().sum()

    if dup_id > 0:
        log(f"⚠️  {dup_id} duplicate IDs → regenerating UUIDs for duplicates")
        dup_mask = df["id"].duplicated(keep="first")
        df.loc[dup_mask, "id"] = [str(uuid.uuid4()) for _ in range(dup_mask.sum())]
    else:
        log("✅ No duplicate IDs")

    if dup_desc > 0:
        log(f"⚠️  {dup_desc} duplicate descriptions → dropping duplicates (keep first)")
        df = df.drop_duplicates(subset="description", keep="first")
    else:
        log("✅ No duplicate descriptions")

    report["steps"]["step1_duplicates"] = {
        "duplicate_ids_fixed"        : int(dup_id),
        "duplicate_descriptions_dropped": before - len(df),
        "rows_after"                 : len(df)
    }
    return df


# ─── STEP 2: NULL / MISSING HANDLING ─────────────────────────────────────────

def step2_nulls(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    print("\n[STEP 2] Null/missing handling...")
    null_before = df.isnull().sum().to_dict()
    actions = []

    total = sum(null_before.values())
    if total == 0:
        log("✅ No nulls found across all columns")
        actions.append("No nulls found")
    else:
        log(f"Null counts: {null_before}")

        # description null → drop row (unusable for training)
        if null_before.get("description", 0) > 0:
            before = len(df)
            df = df[df["description"].notna() & (df["description"].str.strip() != "")]
            n = before - len(df)
            log(f"🗑️  Dropped {n} rows: null/empty description")
            actions.append(f"Dropped {n} rows with null description")

        # category null → drop row
        if null_before.get("category", 0) > 0:
            before = len(df)
            df = df[df["category"].notna()]
            n = before - len(df)
            log(f"🗑️  Dropped {n} rows: null category")
            actions.append(f"Dropped {n} rows with null category")

        # urgency null → impute median per category
        if null_before.get("urgency", 0) > 0:
            for cat in df["category"].dropna().unique():
                mask = df["urgency"].isnull() & (df["category"] == cat)
                if mask.sum() == 0:
                    continue
                med = df.loc[df["category"] == cat, "urgency"].median()
                fill = int(round(med)) if not pd.isna(med) else 3
                df.loc[mask, "urgency"] = fill
            log("🔧 Imputed null urgency with per-category median")
            actions.append("Imputed null urgency with per-category median")

        # register null → default informal
        if null_before.get("register", 0) > 0:
            df["register"] = df["register"].fillna("informal")
            log("🔧 Filled null register → 'informal'")
            actions.append("Filled null register with 'informal'")

        # province null → flag as 'Unknown'
        if null_before.get("province", 0) > 0:
            df["province"] = df["province"].fillna("Unknown")
            log("🔧 Filled null province → 'Unknown'")
            actions.append("Filled null province with 'Unknown'")

        # impact_scope null → flag as 'Community'
        if null_before.get("impact_scope", 0) > 0:
            df["impact_scope"] = df["impact_scope"].fillna("Community")
            log("🔧 Filled null impact_scope → 'Community'")
            actions.append("Filled null impact_scope with 'Community'")

        # sub_topic / source / asta_cita / legislative_target null → empty string
        for col in ["sub_topic", "source", "asta_cita", "legislative_target"]:
            if col in df.columns and null_before.get(col, 0) > 0:
                df[col] = df[col].fillna("")
                log(f"🔧 Filled null {col} → empty string")
                actions.append(f"Filled null {col} with empty string")

    report["steps"]["step2_nulls"] = {
        "null_counts_before": null_before,
        "actions": actions,
        "rows_after": len(df)
    }
    return df


# ─── STEP 3: TYPE COERCION ────────────────────────────────────────────────────

def step3_types(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    print("\n[STEP 3] Type coercion...")
    actions = []

    # id → string
    df["id"] = df["id"].astype(str).str.strip()
    log("✅ id → str")

    # description → string, strip whitespace
    df["description"] = df["description"].astype(str).str.strip()
    log("✅ description → str, stripped")

    # urgency → int
    df["urgency"] = pd.to_numeric(df["urgency"], errors="coerce").astype("Int64")
    log("✅ urgency → Int64")
    actions.append("urgency cast to Int64")

    # string columns → str + strip
    str_cols = ["category","register","province","impact_scope",
                "legislative_target","sub_topic","source"]
    if "asta_cita" in df.columns:
        str_cols.append("asta_cita")
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    log(f"✅ String columns stripped: {str_cols}")
    actions.append(f"Stripped whitespace on: {str_cols}")

    report["steps"]["step3_types"] = {"actions": actions}
    return df


# ─── STEP 4: ENUM VALIDATION ──────────────────────────────────────────────────

def step4_enums(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    print("\n[STEP 4] Enum validation...")
    issues = []
    drop_mask = pd.Series(False, index=df.index)

    # category — invalid row di-drop (unusable for classifier training)
    inv = ~df["category"].isin(VALID_CATEGORIES)
    if inv.sum():
        log(f"⚠️  {inv.sum()} invalid category → DROP: {df.loc[inv,'category'].unique().tolist()}")
        drop_mask |= inv
        issues.append({"field":"category","invalid_count":int(inv.sum()),"action":"dropped"})
    else:
        log("✅ category — all valid")

    # register — invalid → coerce ke 'informal'
    inv = ~df["register"].isin(VALID_REGISTERS)
    if inv.sum():
        log(f"⚠️  {inv.sum()} invalid register → coerced to 'informal'")
        df.loc[inv, "register"] = "informal"
        issues.append({"field":"register","invalid_count":int(inv.sum()),"action":"coerced to informal"})
    else:
        log("✅ register — all valid")

    # urgency — out-of-range → clamp 1-5
    inv = ~df["urgency"].isin(VALID_URGENCY)
    if inv.sum():
        log(f"⚠️  {inv.sum()} urgency out of range → clamped to 1-5")
        df["urgency"] = df["urgency"].clip(1, 5)
        issues.append({"field":"urgency","invalid_count":int(inv.sum()),"action":"clamped 1-5"})
    else:
        log("✅ urgency — all valid")

    # impact_scope — invalid row di-drop
    inv = ~df["impact_scope"].isin(VALID_SCOPES)
    if inv.sum():
        log(f"⚠️  {inv.sum()} invalid impact_scope → DROP: {df.loc[inv,'impact_scope'].unique().tolist()}")
        drop_mask |= inv
        issues.append({"field":"impact_scope","invalid_count":int(inv.sum()),"action":"dropped"})
    else:
        log("✅ impact_scope — all valid")

    # legislative_target — invalid → log only (format CSV dipertahankan)
    if "legislative_target" in df.columns:
        inv = ~df["legislative_target"].isin(VALID_LEGISLATIVE)
        if inv.sum():
            log(f"⚠️  {inv.sum()} unexpected legislative_target values (logged only): {df.loc[inv,'legislative_target'].unique().tolist()}")
            issues.append({"field":"legislative_target","invalid_count":int(inv.sum()),"action":"logged only"})
        else:
            log("✅ legislative_target — all valid")

    before = len(df)
    df = df[~drop_mask]
    log(f"🗑️  Dropped {before - len(df)} rows from enum violations")

    report["steps"]["step4_enums"] = {"issues": issues, "rows_dropped": before - len(df), "rows_after": len(df)}
    return df


# ─── STEP 5: DESCRIPTION QUALITY FILTER ──────────────────────────────────────
# PRD Section 3.5 validate_row() — hanya enforce MIN length (max diabaikan)

def step5_description_quality(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    print("\n[STEP 5] Description quality filter (min length only)...")
    flags = []
    drop_mask = pd.Series(False, index=df.index)

    # Global minimum: 15 chars (PRD Section 3.5)
    too_short_global = df["description"].str.len() < DESC_MIN_LEN
    if too_short_global.sum():
        log(f"⚠️  {too_short_global.sum()} descriptions < {DESC_MIN_LEN} chars → DROP")
        drop_mask |= too_short_global
        flags.append({"check":"global_min_15","dropped":int(too_short_global.sum())})
    else:
        log(f"✅ All descriptions ≥ {DESC_MIN_LEN} chars")

    # Per-register minimum
    for reg, min_len in [("informal", DESC_MIN_INFORMAL), ("formal", DESC_MIN_FORMAL)]:
        mask = (df["register"] == reg) & (df["description"].str.len() < min_len)
        if mask.sum():
            log(f"⚠️  {mask.sum()} {reg} descriptions < {min_len} chars → DROP")
            drop_mask |= mask
            flags.append({"check":f"{reg}_min_{min_len}","dropped":int(mask.sum())})
        else:
            log(f"✅ All {reg} descriptions ≥ {min_len} chars")

    # No-letter check (PRD Section 3.5)
    no_alpha = ~df["description"].str.contains(r'[a-zA-Z]', regex=True, na=False)
    if no_alpha.sum():
        log(f"⚠️  {no_alpha.sum()} descriptions with no alphabetic chars → DROP")
        drop_mask |= no_alpha
        flags.append({"check":"no_alpha","dropped":int(no_alpha.sum())})
    else:
        log("✅ All descriptions contain alphabetic characters")

    before = len(df)
    df = df[~drop_mask]
    log(f"🗑️  Dropped {before - len(df)} rows from description quality checks")

    report["steps"]["step5_description_quality"] = {
        "checks": flags,
        "total_dropped": before - len(df),
        "rows_after": len(df)
    }
    return df


# ─── STEP 6: URGENCY IMBALANCE FLAG ──────────────────────────────────────────
# PRD Section 5.6: dataset kecil → flag imbalance, tidak auto-fix (biar user decide)

def step6_urgency_imbalance(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    print("\n[STEP 6] Urgency distribution check...")
    dist = df["urgency"].value_counts().sort_index().to_dict()
    total = len(df)
    warnings = []

    for lvl in VALID_URGENCY:
        count = dist.get(lvl, 0)
        pct   = count / total * 100
        label = f"urgency={lvl}: {count} rows ({pct:.1f}%)"
        if count < 10:
            log(f"⚠️  IMBALANCED — {label} → consider augmenting")
            warnings.append({"urgency": lvl, "count": count, "pct": round(pct, 2), "status": "imbalanced"})
        else:
            log(f"   {label}")

    if not warnings:
        log("✅ Urgency distribution looks balanced")

    report["steps"]["step6_urgency_imbalance"] = {
        "distribution": {str(k): int(v) for k, v in dist.items()},
        "warnings": warnings
    }
    return df


# ─── STEP 7: CATEGORY DISTRIBUTION vs PRD TARGET ──────────────────────────────

def step7_category_distribution(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    print("\n[STEP 7] Category distribution vs PRD targets...")
    PRD_TARGETS = {
        "Infrastruktur": 150, "Kesehatan": 100, "Pendidikan": 110,
        "Ekonomi": 80, "Lingkungan": 60, "Keamanan": 60, "Sosial": 50
    }
    actual = df["category"].value_counts().to_dict()
    warnings = []

    for cat, target in PRD_TARGETS.items():
        count = actual.get(cat, 0)
        diff  = count - target
        if diff < 0:
            log(f"⚠️  {cat}: {count}/{target} (SHORT {abs(diff)} rows)")
            warnings.append({"category": cat, "actual": count, "target": target, "diff": diff})
        else:
            log(f"   ✅ {cat}: {count}/{target}")

    # Formal % per category (PRD target: 15–20%)
    print()
    log("Formal % per category (PRD target: 15–20%):")
    formal_warnings = []
    for cat in VALID_CATEGORIES:
        sub    = df[df["category"] == cat]
        if len(sub) == 0:
            continue
        pct    = len(sub[sub["register"] == "formal"]) / len(sub) * 100
        status = "✅" if 15 <= pct <= 25 else "⚠️ "
        log(f"   {status} {cat}: {pct:.1f}% formal")
        if pct < 15 or pct > 25:
            formal_warnings.append({"category": cat, "formal_pct": round(pct, 2)})

    report["steps"]["step7_category_distribution"] = {
        "actual_distribution": {k: int(v) for k, v in actual.items()},
        "prd_targets": PRD_TARGETS,
        "shortfall_warnings": warnings,
        "formal_pct_warnings": formal_warnings
    }
    return df


# ─── STEP 8: FINALIZE & SAVE ──────────────────────────────────────────────────

def step8_finalize(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    print("\n[STEP 8] Finalize...")

    # Reorder columns (ikut urutan CSV asli)
    final_cols = [c for c in FINAL_COL_ORDER if c in df.columns]
    df = df[final_cols]
    log(f"✅ Final columns: {final_cols}")

    # Reset index
    df = df.reset_index(drop=True)

    # Save CSV
    df.to_csv(OUTPUT_PATH, index=False)
    log(f"✅ Saved clean CSV → {OUTPUT_PATH}")

    # Save report
    report["output_rows"]    = len(df)
    report["output_columns"] = df.columns.tolist()
    report["rows_removed"]   = report["input_rows"] - len(df)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log(f"✅ Saved cleaning report → {REPORT_PATH}")

    return df


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def run():
    print("=" * 60)
    print("  seed_aspirations.csv — Cleaning Pipeline")
    print("=" * 60)

    df, report = step0_load(INPUT_PATH)
    df = step1_duplicates(df, report)
    df = step2_nulls(df, report)
    df = step3_types(df, report)
    df = step4_enums(df, report)
    df = step5_description_quality(df, report)
    df = step6_urgency_imbalance(df, report)
    df = step7_category_distribution(df, report)
    df = step8_finalize(df, report)

    print("\n" + "=" * 60)
    print(f"  DONE: {report['input_rows']} → {report['output_rows']} rows")
    print(f"  Removed: {report['rows_removed']} rows")
    print("=" * 60)


if __name__ == "__main__":
    run()