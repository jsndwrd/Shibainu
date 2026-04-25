#!/usr/bin/env python3
"""
seed.py
SuaraRakyat AI — Few-Shot Synthetic Aspiration Generator
Jalankan SETELAH collect_baseline.py
pip install openai pandas python-dotenv
"""

import os, json, uuid, time, random
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Jadi ini
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ─────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────
PROVINCE_POOL = [
    ("Jawa Timur",          0.11),
    ("DKI Jakarta",         0.09),
    ("Jawa Barat",          0.09),
    ("Jawa Tengah",         0.07),
    ("Sumatera Utara",      0.06),
    ("Sulawesi Selatan",    0.06),
    ("Kalimantan Timur",    0.05),
    ("Bali",                0.04),
    ("Papua",               0.07),
    ("NTT",                 0.07),
    ("Maluku",              0.06),
    ("Aceh",                0.05),
    ("Kalimantan Barat",    0.05),
    ("Riau",                0.05),
    ("Sulawesi Tengah",     0.05),
    ("Nusa Tenggara Barat", 0.03),
]

CATEGORY_CONFIG = {
    "Infrastruktur": {
        "n": 40, "urgency_range": (3, 5),
        "target_level": ["Regency", "Provincial"],
        "topics": (
            "jalan berlubang/rusak parah, jembatan retak/roboh, lampu jalan mati bertahun-tahun, "
            "drainase mampet menyebabkan banjir, trotoar rusak, gedung sekolah/puskesmas retak, "
            "akses jalan desa terisolir, irigasi sawah rusak"
        ),
    },
    "Kesehatan": {
        "n": 25, "urgency_range": (3, 5),
        "target_level": ["Regency", "Provincial", "National"],
        "topics": (
            "BPJS ditolak RS/puskesmas, obat habis/langka di faskes, antrian sangat panjang, "
            "dokter tidak pernah ada di puskesmas, ambulans tidak tersedia, "
            "stunting anak tidak ditangani, pelayanan kasar, faskes tutup sembarangan"
        ),
    },
    "Pendidikan": {
        "n": 20, "urgency_range": (2, 4),
        "target_level": ["Regency", "Provincial"],
        "topics": (
            "sekolah rusak/bocor, guru tidak pernah hadir, pungutan liar oleh oknum, "
            "KIP tidak cair, beasiswa tidak tepat sasaran, kekurangan buku/fasilitas, "
            "bullying dibiarkan, jarak sekolah terlalu jauh"
        ),
    },
    "Ekonomi": {
        "n": 20, "urgency_range": (3, 5),
        "target_level": ["Regional", "National"],
        "topics": (
            "harga sembako naik drastis, PHK massal, UMR tidak dibayar pengusaha, "
            "UMKM sulit izin usaha, pupuk langka/mahal, nelayan tidak dapat bantuan, "
            "pasar tradisional sepi karena minimarket, bantuan modal tidak merata"
        ),
    },
    "Lingkungan": {
        "n": 15, "urgency_range": (3, 5),
        "target_level": ["Regency", "Regional"],
        "topics": (
            "banjir tahunan tidak ditangani, sampah menumpuk berbulan-bulan, "
            "polusi udara dari pabrik, sungai tercemar limbah, kekeringan ekstrem, "
            "abrasi pantai mengancam rumah, penebangan liar tidak ditindak"
        ),
    },
    "Keamanan": {
        "n": 15, "urgency_range": (3, 5),
        "target_level": ["Regency", "Provincial"],
        "topics": (
            "rawan begal/copet di area gelap, premanisme di pasar, "
            "tawuran remaja tidak ditindak polisi, jalan gelap tanpa penerangan, "
            "narkoba beredar di lingkungan, respon polisi lambat saat laporan"
        ),
    },
    "Sosial": {
        "n": 10, "urgency_range": (2, 4),
        "target_level": ["Regency", "National"],
        "topics": (
            "bansos tidak merata/salah sasaran, diskriminasi pelayanan, "
            "anak putus sekolah tidak terdata, lansia terlantar, "
            "difabel tidak dapat fasilitas layak, BPNT dipotong oknum"
        ),
    },
}

IMPACT_SCOPE = ["Individual", "Community", "Regional", "National"]


# ─────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────
def load_baseline(kategori):
    fname = f"data/baseline/baseline_{kategori.lower().replace(' ', '_')}.json"
    if os.path.exists(fname):
        with open(fname, encoding='utf-8') as f:
            data = json.load(f)
        samples = [s for s in data.get("samples", []) if len(s) > 20]
        print(f"  → Baseline: {len(samples)} contoh nyata ✅")
        return random.sample(samples, min(6, len(samples)))
    print(f"  → Baseline: tidak ada ⚠️  (cold generation)")
    return []


def generate_batch(kategori, province, n, urgency_range, topics, examples):
    if examples:
        few_shot = "\nContoh NYATA pengaduan warga Indonesia — tirukan gaya bahasanya persis:\n"
        few_shot += "\n".join([f'- "{ex[:120]}"' for ex in examples])
    else:
        few_shot = "\nGaya bahasa: informal, campur typo, singkatan, kadang bahasa daerah (seperti WhatsApp/SMS)"

    prompt = f"""Kamu membantu membuat dataset latih untuk sistem AI pengelolaan aspirasi warga pemerintah Indonesia.
{few_shot}

Generate tepat {n} pengaduan warga dengan kriteria:
- Kategori: {kategori}
- Lokasi: {province}
- Topik yang relevan: {topics}
- Urgensi acak antara {urgency_range[0]}–{urgency_range[1]} (1=rendah, 5=kritis)
- Panjang teks: 30–180 karakter
- HARUS BERAGAM — topik, framing, dan kosa kata tidak boleh sama
- Gaya INFORMAL — typo, singkatan, campuran slang/daerah diperbolehkan

Return HANYA valid JSON dengan key "data":
{{"data": [{{"description": "...", "urgency": int, "sub_topic": "..."}}]}}"""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
                response_format={"type": "json_object"},
            )
            raw = json.loads(resp.choices[0].message.content)
            if "data" in raw and isinstance(raw["data"], list):
                return raw["data"]
            for v in raw.values():
                if isinstance(v, list) and len(v) > 0:
                    return v
        except Exception as e:
            print(f"    ⚠️  Attempt {attempt+1} failed: {e}")
            time.sleep(0.8)
    return []


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    if not API_KEY:
        raise ValueError("❌ GEMINI_API_KEY tidak ditemukan. Pastikan file .env sudah ada dan berisi key.")

    random.seed(42)
    os.makedirs('data', exist_ok=True)

    provinces = [p for p, _ in PROVINCE_POOL]
    weights   = [w for _, w in PROVINCE_POOL]
    all_rows  = []

    print("=" * 60)
    print("  SuaraRakyat AI — Synthetic Aspiration Generator")
    print("=" * 60)

    for kategori, cfg in CATEGORY_CONFIG.items():
        print(f"\n[{kategori}] Target: {cfg['n']} entries")
        examples = load_baseline(kategori)

        n_batches     = 5
        n_per_batch   = max(1, cfg['n'] // n_batches)
        sel_provinces = random.choices(provinces, weights=weights, k=n_batches)

        for prov in sel_provinces:
            batch = generate_batch(
                kategori      = kategori,
                province      = prov,
                n             = n_per_batch,
                urgency_range = cfg['urgency_range'],
                topics        = cfg['topics'],
                examples      = examples,
            )
            for item in batch:
                desc = str(item.get("description", "")).strip()
                if len(desc) < 15:
                    continue
                all_rows.append({
                    "id"          : str(uuid.uuid4()),
                    "description" : desc,
                    "category"    : kategori,
                    "province"    : prov,
                    "urgency"     : max(1, min(5, int(item.get("urgency", 3)))),
                    "impact_scope": random.choice(IMPACT_SCOPE),
                    "target_level": random.choice(cfg['target_level']),
                    "sub_topic"   : item.get("sub_topic", ""),
                    "source"      : "synthetic_fewshot",
                })
            time.sleep(0.8)

        count = len([r for r in all_rows if r['category'] == kategori])
        print(f"  → Collected: {count} entries")

    # Append real Pendidikan baseline
    baseline_file = 'data/baseline/baseline_pendidikan.json'
    if os.path.exists(baseline_file):
        with open(baseline_file, encoding='utf-8') as f:
            b = json.load(f)
        for s in b.get("samples", []):
            if len(s) > 20:
                all_rows.append({
                    "id"          : str(uuid.uuid4()),
                    "description" : s,
                    "category"    : "Pendidikan",
                    "province"    : "Nasional",
                    "urgency"     : 3,
                    "impact_scope": "Community",
                    "target_level": "Regency",
                    "sub_topic"   : "KIP/BSM",
                    "source"      : "real_lapor_2015",
                })
        print(f"\n  ✅ Appended {len(b.get('samples', []))} real Pendidikan rows")

    # Save
    df = pd.DataFrame(all_rows)
    df = df[df['description'].str.len() > 15].drop_duplicates(subset='description')
    df.to_csv('data/seed_aspirations.csv', index=False)

    print(f"\n{'=' * 60}")
    print(f"✅ Saved {len(df)} rows → data/seed_aspirations.csv")
    print("\nDistribusi Kategori:")
    print(df['category'].value_counts().to_string())
    print("\nDistribusi Provinsi (Top 8):")
    print(df['province'].value_counts().head(8).to_string())
    print("\nDistribusi Sumber:")
    print(df['source'].value_counts().to_string())


if __name__ == "__main__":
    main()