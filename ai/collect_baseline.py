#!/usr/bin/env python3
"""
collect_baseline.py — Kaggle Notebook Version
SuaraRakyat AI — Baseline Dataset Collector
"""

import os, json, re, time, random
import pandas as pd

# ─────────────────────────────────────────────
# PATH CONFIG (Kaggle)
# ─────────────────────────────────────────────
DISASTER_DIR  = '/kaggle/input/datasets/nicovalerian/4k-disaster-related-indonesian-tweets'
REDDIT_DIR    = '/kaggle/input/datasets/bwandowando/reddit-rindonesia-subreddit-dataset'
DIKNAS_PATH   = '/kaggle/input/datasets/athillazaidan/stream-diknas-selesai/stream_diknas_selesai.csv'  # upload manual
OUTPUT_DIR    = '/kaggle/working/data/baseline'

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────
def clean_tracking_code(text):
    if pd.isna(text): return ""
    cleaned = re.sub(r'^[A-Za-z0-9]{6,}\s+', '', str(text)).strip()
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    return cleaned.strip()

def save_baseline(kategori, samples, source):
    samples = [s for s in samples if isinstance(s, str) and len(s.strip()) > 20]
    data = {"kategori": kategori, "source": source, "count": len(samples), "samples": samples}
    fname = f"{OUTPUT_DIR}/baseline_{kategori.lower().replace(' ', '_')}.json"
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Saved {len(samples)} samples → {fname}")
    return samples

def filter_by_keywords(texts, keywords, n=30):
    pattern = '|'.join(keywords)
    result = []
    for t in texts:
        if isinstance(t, str) and re.search(pattern, t, re.IGNORECASE) and len(t) > 20:
            result.append(t)
        if len(result) >= n:
            break
    return result

def scan_csv(directory):
    """Cari semua CSV di directory, return path file terbesar"""
    csvs = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.csv'):
                fpath = os.path.join(root, f)
                csvs.append((os.path.getsize(fpath), fpath))
    if not csvs:
        return None
    csvs.sort(reverse=True)
    print(f"  → Found: {[p for _, p in csvs]}")
    return csvs[0][1]  # return yang terbesar


# ─────────────────────────────────────────────
# 1. PENDIDIKAN — stream_diknas
# ─────────────────────────────────────────────
def collect_pendidikan():
    print("\n[1/6] Pendidikan — stream_diknas.csv")
    if not os.path.exists(DIKNAS_PATH):
        print(f"  ⚠️  {DIKNAS_PATH} tidak ditemukan")
        print("  → Upload stream_diknas_selesai.csv via 'Add Data' → 'Upload'")
        return []
    df = pd.read_csv(DIKNAS_PATH)
    df['clean'] = df['IsiLaporan'].apply(clean_tracking_code)
    samples = (
        df[df['clean'].str.len() > 30]['clean']
        .dropna().drop_duplicates()
        .sample(min(30, len(df)), random_state=42)
        .tolist()
    )
    return save_baseline("Pendidikan", samples, "lapor.go.id/stream_diknas_2015")


# ─────────────────────────────────────────────
# 2. LINGKUNGAN — Kaggle Disaster Tweets
# ─────────────────────────────────────────────
def collect_lingkungan():
    print("\n[2/6] Lingkungan — Kaggle Disaster Tweets (JSON)")
    
    # Cari file JSON
    json_files = []
    for root, dirs, files in os.walk(DISASTER_DIR):
        for f in files:
            if f.endswith('.json'):
                json_files.append(os.path.join(root, f))
    
    if not json_files:
        print(f"  ⚠️  Tidak ada JSON di {DISASTER_DIR}")
        return []
    
    fpath = json_files[0]
    print(f"  → File: {fpath} ({len(open(fpath).read()):,} chars)")
    
    with open(fpath, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    print(f"  → Total items: {len(raw)}")
    
    # Ambil kolom text, strip URL t.co
    def clean_tweet(text):
        if not isinstance(text, str): return ""
        text = re.sub(r'http\S+', '', text).strip()  # hapus URL
        text = re.sub(r'\s+', ' ', text).strip()     # normalize whitespace
        return text
    
    texts = [clean_tweet(item.get('text', '')) for item in raw]
    
    keywords = ["banjir", "longsor", "sampah", "polusi", "kekeringan",
                "limbah", "bencana", "pencemaran", "rob", "abrasi", "asap", "gempa"]
    samples = filter_by_keywords(texts, keywords, n=30)
    
    return save_baseline("Lingkungan", samples, "Kaggle: 4k-disaster-indonesian-tweets")


# ─────────────────────────────────────────────
# 3. EKONOMI — Reddit r/Indonesia
# ─────────────────────────────────────────────
def collect_ekonomi():
    print("\n[3/6] Ekonomi — Reddit r/Indonesia")
    fpath = scan_csv(REDDIT_DIR)
    if not fpath:
        print(f"  ⚠️  Tidak ada CSV di {REDDIT_DIR}")
        return []
    df = pd.read_csv(fpath, on_bad_lines='skip', nrows=100000)
    print(f"  → Columns: {df.columns.tolist()}")
    text_col = next(
        (c for c in df.columns if c in ['body', 'selftext', 'text', 'content']),
        df.columns[0]
    )
    print(f"  → Using column: '{text_col}' ({len(df)} rows)")
    keywords = ["sembako", "harga naik", "lapangan kerja", "PHK", "pengangguran",
                "inflasi", "kemiskinan", "UMR", "gaji", "harga beras", "BBM naik"]
    samples = filter_by_keywords(df[text_col].dropna().tolist(), keywords, n=25)
    return save_baseline("Ekonomi", samples, "Kaggle: reddit-rindonesia")


# ─────────────────────────────────────────────
# 4. SOSIAL — Reddit r/Indonesia
# ─────────────────────────────────────────────
def collect_sosial():
    print("\n[4/6] Sosial — Reddit r/Indonesia")
    fpath = scan_csv(REDDIT_DIR)
    if not fpath:
        print(f"  ⚠️  Tidak ada CSV di {REDDIT_DIR}")
        return []
    df = pd.read_csv(fpath, on_bad_lines='skip', nrows=100000)
    text_col = next(
        (c for c in df.columns if c in ['body', 'selftext', 'text', 'content']),
        df.columns[0]
    )
    keywords = ["bansos", "PKH", "diskriminasi", "BLT", "BPNT", "stunting",
                "anak terlantar", "gizi buruk", "tidak merata", "desa terpencil"]
    samples = filter_by_keywords(df[text_col].dropna().tolist(), keywords, n=20)
    return save_baseline("Sosial", samples, "Kaggle: reddit-rindonesia")


def collect_infrastruktur():
    print("\n[5/6] Infrastruktur — Reddit r/Indonesia")
    fpath = scan_csv(REDDIT_DIR)
    if not fpath:
        return []
    df = pd.read_csv(fpath, on_bad_lines='skip', nrows=200000)
    text_col = 'body'
    keywords = ["jalan rusak", "jalan berlubang", "jembatan", "lampu jalan",
                "drainase", "banjir got", "trotoar", "macet", "infrastruktur",
                "fasilitas umum", "gedung rusak", "got mampet"]
    samples = filter_by_keywords(df[text_col].dropna().tolist(), keywords, n=35)
    return save_baseline("Infrastruktur", samples, "Kaggle: reddit-rindonesia")

def collect_keamanan():
    print("\n[6/6] Keamanan — Reddit r/Indonesia")
    fpath = scan_csv(REDDIT_DIR)
    if not fpath:
        return []
    df = pd.read_csv(fpath, on_bad_lines='skip', nrows=200000)
    text_col = 'body'
    keywords = ["begal", "rampok", "maling", "copet", "tidak aman", "rawan",
                "preman", "tawuran", "pencurian", "kriminal", "narkoba",
                "begal motor", "keamanan warga", "polisi lambat"]
    samples = filter_by_keywords(df[text_col].dropna().tolist(), keywords, n=20)
    return save_baseline("Keamanan", samples, "Kaggle: reddit-rindonesia")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  SuaraRakyat AI — Baseline Collector (Kaggle)")
    print("=" * 55)

    results = {
        "Pendidikan"   : collect_pendidikan(),
        "Lingkungan"   : collect_lingkungan(),
        "Ekonomi"      : collect_ekonomi(),
        "Sosial"       : collect_sosial(),
        "Infrastruktur": collect_infrastruktur(),
        "Keamanan"     : collect_keamanan(),
    }

    print("\n" + "=" * 55)
    print("  SUMMARY")
    print("=" * 55)
    total = 0
    for kat, samples in results.items():
        n = len(samples) if samples else 0
        total += n
        status = "✅" if n >= 10 else ("⚠️ " if n > 0 else "❌ cold")
        print(f"  {status} {kat:15s}: {n:3d} samples")
    print(f"\n  Total baseline terkumpul: {total} samples")
    print(f"  Output: {OUTPUT_DIR}/")