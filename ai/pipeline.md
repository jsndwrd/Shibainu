═══════════════════════════════════════════════════════════════
                    LAYER 0 — INPUT
═══════════════════════════════════════════════════════════════

Citizen submit via form (Next.js)
  ├── description: teks bebas (informal/formal)
  ├── category: dropdown (opsional, bisa kosong)
  ├── urgency: slider 1–5 (opsional, bisa kosong)
  ├── province + regency
  ├── impact_scope
  └── target_level
         ↓

═══════════════════════════════════════════════════════════════
                LAYER 1 — AI CLEANING (Rule-based)
                File: ai_cleaner.py | No API calls
═══════════════════════════════════════════════════════════════

  ├── Normalize slang → Bahasa baku
  │     ("gak" → "tidak", "bgt" → "sangat", "jln" → "jalan")
  ├── Strip profanity + emotional noise
  ├── Hapus tracking code (lapor.go.id prefix)
  └── Output: cleaned_description (teks normal)
         ↓

═══════════════════════════════════════════════════════════════
            LAYER 2 — INDOBERTWEET CLASSIFIER
            Model: indolem/indobertweet-base-uncased
            File: train.py → model/ → embedder.py
            Fine-tuned, offline sepenuhnya
═══════════════════════════════════════════════════════════════

  Input: cleaned_description
         ↓
  [IndoBERTweet Encoder — shared weights]
         ↓
  ┌──────────────────┬─────────────────────────────┐
  │   HEAD 1         │   HEAD 2                    │
  │   Category       │   Urgency                   │
  │   Classifier     │   Predictor                 │
  │                  │                             │
  │   7 kelas:       │   1–5 (ordinal)             │
  │   Infrastruktur  │                             │
  │   Kesehatan      │   Dipakai kalau:            │
  │   Pendidikan     │   - user tidak isi slider   │
  │   Ekonomi        │   - input dari lapor.go.id  │
  │   Lingkungan     │   - API publik tanpa form   │
  │   Keamanan       │                             │
  │   Sosial         │                             │
  └──────────────────┴─────────────────────────────┘
         ↓
  Output:
  ├── predicted_category (override kalau user kosongkan)
  ├── predicted_urgency (override kalau user kosongkan)
  └── embedding_vector [768-dim] → disimpan ke DB (pgvector)
         ↓

═══════════════════════════════════════════════════════════════
              LAYER 3 — CLUSTERING ENGINE
              File: clusterer.py | No model, deterministic
═══════════════════════════════════════════════════════════════

  Setiap submission baru masuk:
  ├── Hitung cosine similarity vs semua embedding di DB
  ├── Similarity > 0.78 → masuk cluster yang ada
  ├── Tidak ada cluster cocok → buat cluster baru
  └── Update cluster metadata:
        ├── member_count
        ├── top_provinces[]
        ├── avg_urgency
        └── label (di-generate 1x saat cluster dibuat)
         ↓

═══════════════════════════════════════════════════════════════
              LAYER 4 — PRIORITY SCORING ENGINE
              File: scorer.py | Formula deterministik
═══════════════════════════════════════════════════════════════

  Per cluster, hitung:

  Priority Score =
    (Normalized Volume    × 0.30) +
    (Average Urgency      × 0.25) +
    (Geographic Spread    × 0.25) +
    (Impact Scope Score   × 0.20)

  Trigger brief jika semua kondisi terpenuhi:
  ├── avg_urgency ≥ 4.0
  ├── member_count ≥ 5
  ├── priority_score ≥ 65/100
  └── province_spread ≥ 2
         ↓

═══════════════════════════════════════════════════════════════
           LAYER 5 — POLICY BRIEF GENERATOR
           Model: llama3.1:8b via Ollama (LOCAL, offline)
           File: brief_generator.py
           ~12 detik/brief | 8GB VRAM GPU
═══════════════════════════════════════════════════════════════

  Input ke LLM:
  ├── cluster label + category
  ├── top 5 deskripsi terpilih
  ├── priority score + avg urgency
  ├── distribusi provinsi
  └── jumlah laporan

  Output (laporan formal DPR-ready):
  ┌─────────────────────────────────────────────┐
  │  LAPORAN ASPIRASI WARGA                     │
  │  ─────────────────────────────────────────  │
  │  1. RINGKASAN EKSEKUTIF (3–4 kalimat)       │
  │  2. ISU UTAMA (bullet + data)               │
  │  3. DISTRIBUSI GEOGRAFIS (peta provinsi)    │
  │  4. REKOMENDASI KEBIJAKAN (3 poin aksi)     │
  │  5. KLASIFIKASI URGENSI:                    │
  │     Segera / Jangka Pendek / Jangka Panjang │
  └─────────────────────────────────────────────┘

  ⚡ Cached di DB — tidak di-regenerate kecuali
     cluster bertambah >20% member baru
         ↓

═══════════════════════════════════════════════════════════════
                    OUTPUT LAYER
═══════════════════════════════════════════════════════════════

  ┌─────────────────┐     ┌──────────────────────┐
  │ Government      │     │ Citizen              │
  │ Dashboard       │     │ View                 │
  │                 │     │                      │
  │ Top 10 isu      │     │ Status submission:   │
  │ Filter province │     │ Received →           │
  │ Priority chart  │     │ Processed →          │
  │ Generate Brief  │     │ Clustered →          │
  │ Download PDF    │     │ Scored               │
  └─────────────────┘     └──────────────────────┘