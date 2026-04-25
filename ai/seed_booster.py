import os, json, uuid, time, random
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

# 1. KONFIGURASI TARGET (BOOSTER)
# Fokus ke kategori yang F1-nya jeblok
BOOSTER_CONFIG = {
    "Kesehatan": {
        "total": 100,
        "asta_cita": [4], # SDM & Kesehatan
        "keywords": ["wabah", "obat habis", "malpraktik", "nyawa melayang", "darurat medis"]
    },
    "Sosial": {
        "total": 100,
        "asta_cita": [1, 6], # HAM & Ekonomi Desa
        "keywords": ["kelaparan", "lansia terlantar", "bansos dikorupsi", "diskriminasi parah", "kekerasan"]
    }
}

PROVINCE_POOL = ["Jambi", "Papua", "NTT", "Kalimantan Timur", "Jawa Barat"]

def generate_booster_batch(kategori, n, asta_ids):
    # Prompt yang memaksa LLM pakai keyword urgensi tinggi
    prompt = f"""Generate {n} aspirasi warga Indonesia UNIK untuk KATEGORI: {kategori}.
    
    KRITERIA KHUSUS:
    1. Untuk Urgensi 5: Gunakan diksi ekstrim seperti 'DARURAT', 'BAHAYA', 'SEGERA', 'NYAWA TERANCAM'.
    2. Untuk Sosial: Fokus pada hak manusia, bantuan sosial, dan keadilan, BUKAN pembangunan fisik.
    3. Untuk Kesehatan: Fokus pada ketersediaan obat, penanganan medis, dan nyawa pasien.
    4. Legislative: Sesuaikan dengan skala (DPR RI/DPRD).
    
    Output JSON:
    {{"data": [
        {{"description": "...", "urgency": 5, "asta_cita": "Misi X", "legislative_target": "...", "sub_topic": "..."}}
    ]}}"""

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9, # Tinggi biar variasi bahasanya banyak
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content).get("data", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    print("🚀 Starting Data Augmentation (Booster Mode)...")
    new_rows = []

    for kategori, cfg in BOOSTER_CONFIG.items():
        collected = 0
        print(f"  → Boosting {kategori}...")
        while collected < cfg['total']:
            batch = generate_booster_batch(kategori, 10, cfg['asta_cita'])
            for item in batch:
                new_rows.append({
                    "id": str(uuid.uuid4()),
                    "description": item.get("description"),
                    "category": kategori,
                    "register": random.choice(["informal", "formal"]),
                    "province": random.choice(PROVINCE_POOL),
                    "urgency": item.get("urgency"),
                    "asta_cita": item.get("asta_cita"),
                    "legislative_target": item.get("legislative_target"),
                    "impact_scope": random.choice(["Community", "Regional", "National"]),
                    "sub_topic": item.get("sub_topic"),
                    "source": "booster_v3.2"
                })
                collected += 1
            print(f"    ✅ {collected}/{cfg['total']}")
            time.sleep(1)

    # Gabung dengan data lama
    old_df = pd.read_csv("data/seed_aspirations_clean.csv")
    new_df = pd.DataFrame(new_rows)
    
    final_df = pd.concat([old_df, new_df], ignore_index=True)
    final_df.to_csv("data/seed_aspirations_augmented.csv", index=False)
    print(f"\n🔥 SUCCESS! Total data sekarang: {len(final_df)} baris.")

if __name__ == "__main__":
    main()