#!/usr/bin/env python3
"""
seed.py (V2.2 - Final Strategic Generator)
SuaraRakyat AI — Strategic Synthetic Aspiration Generator
Status: Production-Ready for Training Data Generation
"""

import os, json, uuid, time, random
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ─────────────────────────────────────────────
# 1. DEFINISI STRATEGIS (ASTA CITA)
# ─────────────────────────────────────────────
ASTA_CITA = {
    1: "Ideologi, Demokrasi, dan HAM",
    2: "Swasembada Pangan, Energi, Air, Ekonomi Hijau dan Biru",
    3: "Lapangan Kerja, Kewirausahaan, dan Infrastruktur",
    4: "SDM, Sains, Teknologi, Pendidikan, Kesehatan",
    5: "Hilirisasi dan Industrialisasi",
    6: "Membangun dari Desa dan Kelurahan untuk Pemerataan Ekonomi",
    7: "Reformasi Hukum, Birokrasi, dan Pemberantasan Korupsi/Narkoba",
    8: "Penyelarasan Kehidupan yang Harmonis dengan Alam dan Budaya"
}

# ─────────────────────────────────────────────
# 2. KONFIGURASI DATASET (Target Total: ~610)
# ─────────────────────────────────────────────
CATEGORY_CONFIG = {
    "Infrastruktur": {"total": 150, "asta_cita": [3, 6]},
    "Kesehatan":     {"total": 100, "asta_cita": [4]},
    "Pendidikan":    {"total": 110, "asta_cita": [4]},
    "Ekonomi":       {"total": 80,  "asta_cita": [2, 3, 5, 6]},
    "Lingkungan":    {"total": 60,  "asta_cita": [2, 8]},
    "Keamanan":      {"total": 60,  "asta_cita": [1, 7]},
    "Sosial":        {"total": 50,  "asta_cita": [1, 6]}
}

PROVINCE_POOL = ["Jambi", "Jawa Timur", "Jawa Barat", "Papua", "Sumatera Utara", "Kalimantan Timur", "NTT"]

# ─────────────────────────────────────────────
# 3. GENERATOR ENGINE DENGAN HIGH-CONTEXT PROMPT
# ─────────────────────────────────────────────
def generate_batch(kategori, register, n, asta_ids):
    asta_targets = ", ".join([f"Misi {i}: {ASTA_CITA[i]}" for i in asta_ids])
    
    # Panduan gaya bahasa
    if register == "informal":
        style_desc = "Gaya WhatsApp/Tweet/SMS (singkatan spt 'yg', 'gak', 'jln', typo, emosional). Panjang 50-180 karakter."
        example = "Contoh: 'Jalan di desa kami rusak parah bgt pak, udah 3 thn gak dibenerin kalo ujan jadi kubangan lumpur, kasian anak sekolah lewatnya susah.'"
    else:
        style_desc = "Bahasa Indonesia baku, struktur surat resmi, sopan, deskriptif. Panjang 150-400 karakter."
        example = "Contoh: 'Melaporkan kondisi infrastruktur jalan di Kecamatan X yang mengalami kerusakan berat sepanjang 2km. Hal ini sangat menghambat akses ekonomi petani lokal menuju pasar induk dan perlu penanganan segera.'"

    prompt = f"""Generate {n} aspirasi warga Indonesia UNIK untuk KATEGORI: {kategori}.
GAYA: {style_desc}.
{example}

KRITERIA WAJIB:
1. Hubungkan secara logis dengan salah satu: {asta_targets}.
2. Tentukan legislative_target: 
   - 'DPR RI' (Isu nasional, strategis nasional, atau lintas provinsi).
   - 'DPRD Provinsi' (Isu skala provinsi).
   - 'DPRD Kab/Kota' (Isu lokal/desa/puskesmas/sampah/jalan lingkungan).
3. Urgensi 1-5 (sebagai label latihan model).
4. JANGAN membuat kalimat terlalu pendek. Tambahkan detail lokasi anonim, durasi masalah, atau dampak spesifik ke warga.
5. Gunakan variasi register yang kontras.

Return JSON Valid:
{{"data": [{{"description": "...", "urgency": int, "asta_cita": "Misi X", "legislative_target": "...", "sub_topic": "..."}}]}}"""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85, 
                response_format={"type": "json_object"},
                timeout=45
            )
            data = json.loads(resp.choices[0].message.content).get("data", [])
            if data: return data
        except Exception as e:
            print(f"    ⚠️ Attempt {attempt+1} gagal: {e}")
            time.sleep(2)
    return []

# ─────────────────────────────────────────────
# 4. MAIN EXECUTION (ROBUST QUOTA ENFORCEMENT)
# ─────────────────────────────────────────────
def main():
    print("🚀 Starting Strategic Seed Generation (V2.2 - High Context)...")
    all_rows = []

    for kategori, cfg in CATEGORY_CONFIG.items():
        # Rasio: 80% Informal, 20% Formal
        targets = [("informal", int(cfg['total'] * 0.8)), 
                   ("formal", cfg['total'] - int(cfg['total'] * 0.8))]
        
        for reg, target_n in targets:
            collected_for_reg = 0
            print(f"  → Progress: {kategori} ({reg}) - Target: {target_n}")
            
            # Loop sampai kuota terpenuhi
            while collected_for_reg < target_n:
                needed = min(8, target_n - collected_for_reg) 
                batch = generate_batch(kategori, reg, needed, cfg['asta_cita'])
                
                for item in batch:
                    desc = item.get("description", "").strip()
                    # Filter panjang teks minimal
                    min_char = 45 if reg == "informal" else 120
                    
                    if len(desc) >= min_char:
                        all_rows.append({
                            "id": str(uuid.uuid4()),
                            "description": desc,
                            "category": kategori,
                            "register": reg,
                            "province": random.choice(PROVINCE_POOL),
                            "urgency": item.get("urgency", 3), # Teacher label
                            "asta_cita": item.get("asta_cita"),
                            "legislative_target": item.get("legislative_target"),
                            "impact_scope": random.choice(["Individual", "Community", "Regional", "National"]),
                            "sub_topic": item.get("sub_topic"),
                            "source": "synthetic_strategic_v2.2"
                        })
                        collected_for_reg += 1
                
                print(f"    ✅ Progress: {collected_for_reg}/{target_n}")
                time.sleep(1.5) # Rate limiting

    # Final Post-Processing
    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=['description'])
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/seed_aspirations.csv', index=False)
    
    print(f"\n{'='*40}")
    print(f"✅ SUCCESS: {len(df)} High-Quality rows saved!")
    print(f"{'='*40}")
    print(df.groupby(['category', 'register']).size())

if __name__ == "__main__":
    main()