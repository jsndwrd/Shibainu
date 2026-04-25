#!/usr/bin/env python3
"""
seed.py V3.1 — SuaraRakyat AI
Fix: urgency kontekstual per Asta Cita → tiap level punya makna spesifik
     sesuai misi pembangunan yang dirujuk
"""

import os, json, uuid, time, random
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

# ─── ASTA CITA + URGENCY CONTEXT ──────────────────────────────
# Tiap misi punya deskripsi urgency 1-5 yang kontekstual
# Bukan urgency generik, tapi spesifik terhadap isu dalam misi tersebut

ASTA_CITA_CONTEXT = {
    1: {
        "misi": "Ideologi, Demokrasi, dan HAM",
        "urgency": {
            1: "Usulan ringan tentang peningkatan kesadaran Pancasila atau pendidikan civic, belum ada dampak nyata.",
            2: "Keluhan minor tentang proses demokrasi lokal (misalnya kurangnya sosialisasi Pemilu) yang bisa ditangani jangka menengah.",
            3: "Pelanggaran hak warga dalam skala terbatas (diskriminasi di layanan publik) yang perlu perhatian segera.",
            4: "Kasus pembungkaman kebebasan berpendapat atau intimidasi terhadap kelompok minoritas yang berdampak luas.",
            5: "Kekerasan HAM aktif, ancaman terhadap nyawa, atau pelanggaran demokrasi sistematis yang membutuhkan respons darurat.",
        }
    },
    2: {
        "misi": "Swasembada Pangan, Energi, Air, Ekonomi Hijau dan Biru",
        "urgency": {
            1: "Usulan pengembangan pertanian atau energi terbarukan jangka panjang yang belum mendesak.",
            2: "Kendala irigasi kecil atau distribusi pupuk yang mempengaruhi sebagian petani namun masih tertangani.",
            3: "Kelangkaan air bersih atau pangan di wilayah tertentu yang mulai berdampak ke ekonomi warga.",
            4: "Gagal panen luas atau krisis air yang mengancam penghidupan ribuan keluarga di suatu daerah.",
            5: "Bencana pangan atau kekeringan ekstrem yang mengancam kelaparan atau kehilangan mata pencaharian massal.",
        }
    },
    3: {
        "misi": "Lapangan Kerja, Kewirausahaan, dan Infrastruktur",
        "urgency": {
            1: "Usulan penambahan fasilitas publik atau pengembangan UMKM yang bersifat jangka panjang.",
            2: "Infrastruktur rusak ringan (trotoar retak, lampu mati) atau keterbatasan akses modal UMKM skala kecil.",
            3: "Jalan rusak parah yang menghambat mobilitas harian atau angka pengangguran tinggi di suatu kecamatan.",
            4: "Infrastruktur vital (jembatan, jalan utama) yang rusak berat sehingga memotong akses ekonomi ribuan warga.",
            5: "Infrastruktur roboh/nyaris roboh mengancam jiwa, atau pemutusan hubungan kerja massal tanpa pengaman sosial.",
        }
    },
    4: {
        "misi": "SDM, Sains, Teknologi, Pendidikan, Kesehatan",
        "urgency": {
            1: "Usulan peningkatan kualitas kurikulum atau fasilitas lab sekolah jangka panjang.",
            2: "Kekurangan buku teks atau guru di sekolah terpencil yang masih bisa ditoleransi sementara.",
            3: "Puskesmas kelebihan kapasitas, akses dokter spesialis terbatas, atau fasilitas sekolah rusak sebagian.",
            4: "Wabah penyakit lokal, sekolah tidak layak pakai, atau tingginya angka putus sekolah di suatu kabupaten.",
            5: "Krisis kesehatan darurat (KLB penyakit menular), fasilitas pendidikan ambruk, atau tidak ada tenaga medis sama sekali.",
        }
    },
    5: {
        "misi": "Hilirisasi dan Industrialisasi",
        "urgency": {
            1: "Usulan jangka panjang tentang pengembangan industri lokal atau pelatihan vokasi.",
            2: "Kendala perizinan usaha kecil atau akses teknologi yang menghambat UMKM tapi masih bisa ditangani.",
            3: "Industri lokal terhambat regulasi atau persaingan tidak sehat yang merugikan banyak pelaku usaha daerah.",
            4: "Penutupan pabrik atau industri yang menyebabkan pengangguran massal di suatu wilayah.",
            5: "Dampak industri yang mencemari lingkungan dan mengancam kesehatan warga secara langsung dan akut.",
        }
    },
    6: {
        "misi": "Membangun dari Desa dan Kelurahan untuk Pemerataan Ekonomi",
        "urgency": {
            1: "Usulan pengembangan wisata desa atau program BUMDes jangka panjang.",
            2: "Dana desa tidak terserap optimal atau fasilitas desa kurang memadai namun tidak kritis.",
            3: "Ketimpangan layanan antara desa dan kota yang menyulitkan warga mengakses layanan dasar.",
            4: "Desa terisolasi tanpa akses jalan/internet yang menyebabkan kemiskinan struktural parah.",
            5: "Desa terancam bencana (longsor, banjir bandang) atau sama sekali tidak terjangkau layanan darurat.",
        }
    },
    7: {
        "misi": "Reformasi Hukum, Birokrasi, dan Pemberantasan Korupsi/Narkoba",
        "urgency": {
            1: "Usulan reformasi administratif atau digitalisasi layanan publik jangka panjang.",
            2: "Birokrasi lambat atau pungli kecil di layanan publik yang sudah menjadi kebiasaan namun belum kritis.",
            3: "Kasus korupsi dana publik skala menengah atau penyalahgunaan wewenang pejabat lokal yang sudah menyebar.",
            4: "Korupsi proyek infrastruktur besar yang merugikan masyarakat luas atau peredaran narkoba merajalela.",
            5: "Jaringan korupsi sistemik yang melumpuhkan layanan dasar, atau operasi narkoba yang mengancam generasi muda secara masif.",
        }
    },
    8: {
        "misi": "Penyelarasan Kehidupan yang Harmonis dengan Alam dan Budaya",
        "urgency": {
            1: "Usulan pelestarian budaya lokal atau program lingkungan yang bersifat jangka panjang.",
            2: "Pencemaran ringan atau penggerusan nilai budaya lokal yang belum berdampak kritis.",
            3: "Kerusakan lingkungan skala menengah (alih fungsi lahan, polusi sungai) yang merugikan ekonomi warga.",
            4: "Deforestasi masif atau bencana ekologis yang menghancurkan mata pencaharian komunitas lokal.",
            5: "Bencana alam akut (kebakaran hutan, banjir besar) yang mengancam jiwa dan menghancurkan permukiman.",
        }
    }
}

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


# ─── GENERATOR ────────────────────────────────────────────────
def generate_batch(kategori, register, urgency_level, n, asta_ids):
    # Pilih satu asta_cita secara random dari yang tersedia untuk kategori ini
    # → tiap batch fokus ke 1 misi agar konteks urgency lebih kohesif
    asta_id      = random.choice(asta_ids)
    asta_ctx     = ASTA_CITA_CONTEXT[asta_id]
    urg_ctx      = asta_ctx["urgency"][urgency_level]
    misi_label   = f"Misi {asta_id}: {asta_ctx['misi']}"

    if register == "informal":
        style = "Gaya WhatsApp/Twitter/SMS: singkatan ('yg','gak','bgt','jln'), typo wajar, emosional, 60-200 karakter."
        ex    = f"Contoh register informal urgency {urgency_level}: keluhan warga biasa dengan bahasa santai, emosi sesuai tingkat urgensi."
    else:
        style = "Bahasa Indonesia baku, surat resmi, sopan, deskriptif, detail lokasi + dampak, 150-400 karakter."
        ex    = f"Contoh register formal urgency {urgency_level}: laporan resmi dengan data dan dampak yang proporsional dengan tingkat urgensi."

    prompt = f"""Generate tepat {n} aspirasi warga Indonesia UNIK untuk:

KATEGORI   : {kategori}
MISI       : {misi_label}
URGENCY    : {urgency_level}/5
KONTEKS    : {urg_ctx}

GAYA BAHASA: {style}
             {ex}

WAJIB DIPATUHI:
1. ISI aspirasi HARUS mencerminkan tingkat urgensi {urgency_level} sesuai konteks di atas — bukan lebih tinggi, bukan lebih rendah.
2. Kaitkan secara logis dengan {misi_label}.
3. Tambahkan detail spesifik: lokasi anonim, durasi masalah, atau dampak ke warga.
4. Tentukan legislative_target:
   - 'DPR RI'         → isu nasional/strategis lintas provinsi
   - 'DPRD Provinsi'  → isu skala provinsi
   - 'DPRD Kab/Kota'  → isu lokal/desa/kelurahan
5. Nada emosional HARUS proporsional: urgency=1 tenang/usulan biasa, urgency=5 panik/darurat.

Return JSON valid (urgency HARUS = {urgency_level}):
{{"data": [{{"description": "...", "urgency": {urgency_level}, "asta_cita": "{misi_label}", "legislative_target": "...", "sub_topic": "..."}}]}}"""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
                response_format={"type": "json_object"},
                timeout=45
            )
            data = json.loads(resp.choices[0].message.content).get("data", [])
            # Guard: buang kalau LLM override urgency
            data = [d for d in data if int(d.get("urgency", 0)) == urgency_level]
            if data: return data, asta_id
        except Exception as e:
            print(f"    ⚠️ Attempt {attempt+1} gagal: {e}")
            time.sleep(2)
    return [], asta_id


# ─── MAIN ─────────────────────────────────────────────────────
def main():
    print("🚀 SuaraRakyat Seed Generator V3.1 — Urgency × Asta Cita Contextual")
    print("   Target: tiap urgency level ≈ 20% per kategori, konteks per misi\n")

    all_rows = []

    for kategori, cfg in CATEGORY_CONFIG.items():
        total_cat    = cfg["total"]
        urg_per_level = total_cat // 5
        leftovers     = total_cat - (urg_per_level * 5)
        urg_targets   = {1: urg_per_level, 2: urg_per_level,
                         3: urg_per_level + leftovers,
                         4: urg_per_level, 5: urg_per_level}

        print(f"\n{'─'*60}")
        print(f"  {kategori} | total={total_cat} | urgency={urg_targets}")
        print(f"  Asta Cita: {[f'Misi {i}' for i in cfg['asta_cita']]}")
        print(f"{'─'*60}")

        for urg_lvl, urg_total in urg_targets.items():
            n_informal = int(urg_total * 0.8)
            n_formal   = urg_total - n_informal

            for register, target_n in [("informal", n_informal), ("formal", n_formal)]:
                if target_n == 0:
                    continue

                collected = 0
                print(f"  → {kategori} | urg={urg_lvl} | {register} | target={target_n}")

                while collected < target_n:
                    needed         = min(6, target_n - collected)
                    batch, asta_id = generate_batch(kategori, register, urg_lvl, needed, cfg["asta_cita"])

                    for item in batch:
                        desc     = item.get("description", "").strip()
                        min_char = 50 if register == "informal" else 120
                        if len(desc) < min_char:
                            continue

                        all_rows.append({
                            "id"                : str(uuid.uuid4()),
                            "description"       : desc,
                            "category"          : kategori,
                            "register"          : register,
                            "province"          : random.choice(PROVINCE_POOL),
                            "urgency"           : urg_lvl,             # hardcode dari loop
                            "asta_cita"         : item.get("asta_cita", f"Misi {asta_id}"),
                            "legislative_target": item.get("legislative_target", ""),
                            "impact_scope"      : random.choice(["Individual","Community","Regional","National"]),
                            "sub_topic"         : item.get("sub_topic", ""),
                            "source"            : "synthetic_v3.1_asta_urgency"
                        })
                        collected += 1
                        if collected >= target_n:
                            break

                    print(f"    ✅ {collected}/{target_n}")
                    time.sleep(1.2)

    # ── Post-processing ────────────────────────────────────────
    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["description"]).reset_index(drop=True)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/seed_aspirations.csv", index=False)

    # ── Report ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"✅ DONE: {len(df)} rows → data/seed_aspirations.csv")
    print(f"{'='*60}")

    print("\n📊 Urgency distribution (target tiap ~20%):")
    urg_dist = df["urgency"].value_counts().sort_index()
    for lvl, cnt in urg_dist.items():
        pct    = cnt / len(df) * 100
        bar    = "█" * int(pct / 2)
        status = "✅" if 15 <= pct <= 25 else "⚠️ "
        print(f"  {status} urgency={lvl}: {cnt:4d} ({pct:.1f}%) {bar}")

    print("\n📊 Category × Urgency (heatmap):")
    pivot = df.groupby(["category","urgency"]).size().unstack(fill_value=0)
    print(pivot.to_string())

    print("\n📊 Asta Cita × Urgency coverage:")
    # Pastikan tiap misi punya representasi di semua urgency level
    asta_urg = df.groupby(["asta_cita","urgency"]).size().unstack(fill_value=0)
    print(asta_urg.to_string())


if __name__ == "__main__":
    main()