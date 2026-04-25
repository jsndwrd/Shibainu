# SHIBAINU @ UC HACKFEST 2026

## Quick Commands

0. Concurrent Running

```bash
(cd frontend && bun dev) & (cd backend && python -m uvicorn main:app --reload)
```

1. Frontend

```bash
bun dev
```

2. Backend

- Dependencies Update:

```bash
pip freeze > requirements.txt
```

- Running the project:

```bash
python -m uvicorn main:app --reload
```

---

## Features

### 1. Autentikasi Pengguna

- Login menggunakan NIK dan tanggal lahir.
- Token autentikasi berbasis bearer token.
- Penyimpanan token di frontend.
- Fetch data user melalui endpoint `/api/auth/me`.
- Logout user.

### 2. Role User dan Admin

- Sistem membedakan role `user` dan `admin`.
- User diarahkan ke halaman aspirasi.
- Admin diarahkan ke dashboard admin.
- Navbar berubah otomatis berdasarkan role.
- Menu `Laporan` berubah menjadi `Dashboard` jika user memiliki role admin.

### 3. Form Aspirasi Multi-Step

- Step 1: Identitas pelapor.
- Step 2: Detail aspirasi.
- Step 3: Lokasi dan level prioritas.
- Step 4: Review dan submit.
- Data form disimpan menggunakan Zustand store.
- Validasi form menggunakan Zod dan React Hook Form.
- Payload frontend disesuaikan dengan schema backend.

### 4. Submit Aspirasi

- User dapat mengirim aspirasi ke backend.
- Aspirasi dikirim ke endpoint `/api/aspirations/`.
- Data dikirim meliputi:
  - Deskripsi aspirasi
  - Kategori
  - Provinsi
  - Kabupaten/Kota
  - Skala dampak / prioritas
  - Target level (operasional/strategis)

### 5. Reference Data

- Data kategori, provinsi, dan kabupaten/kota diambil dari backend.
- Store khusus `useReferenceStore` untuk:
  - Categories
  - Provinces
  - Regencies

### 6. Dashboard Admin

- Menampilkan data dari backend:
  - Total aspirasi
  - Total cluster
  - Aspirasi kritis
  - Jumlah policy brief
  - Daftar aspirasi terbaru
  - Cluster prioritas
  - Top scores
  - Policy brief terbaru

### 7. Cluster Aspirasi

- Clusterisasi berdasarkan similarity embedding.
- Cluster menyimpan:
  - Label
  - Kategori
  - Jumlah anggota
  - Rata-rata prioritas
  - Provinsi dominan
  - Skor prioritas (GDI + PAVI + Asta Cita)
  - Sub-topik
  - Distribusi laporan
  - Asta Cita dominan

### 8. Policy Brief Generation

- Menggunakan local LLM (Ollama) untuk cluster strategis.
- Menghasilkan dokumen formal 7-section policy brief (~10–20 detik per cluster).
- Dokumen sudah aligned dengan prioritas, actionable untuk pemerintah.
- Fallback ke template jika LLM tidak tersedia.
- File disimpan ke database dan sebagai file `.txt`.
- Endpoint download tersedia di `/api/briefs/{id}/download`.

### 9. Context-Based Policy Routing

- Memisahkan laporan operasional vs strategis.
- 2-route transparent decision logic:
  - Operational → ticket langsung
  - Strategic → masuk clustering, scoring, brief generation
- Strategic trigger: ≥10 laporan serupa atau ≥3 wilayah terdampak.
- Rule-based confidence: 65–95%.

### 10. Priority Scoring

- Menggunakan kombinasi:
  - **GDI (35%)**: koreksi sebaran geografis isu
  - **PAVI (35%)**: normalisasi jumlah laporan per 100.000 penduduk
  - **Asta Cita (30%)**: relevansi isu terhadap misi pembangunan nasional
- Macro F1 Asta Cita: 85.19%
- Category Macro F1: 66.88%
- Menyeimbangkan isu secara regional dan populasi.

---

## Technology Stack

- **Frontend:** Next.js, React, Zustand, React Hook Form, Zod
- **Backend:** FastAPI, Python 3.12, SQLAlchemy
- **Database:** PostgreSQL
- **NLP:** IndoBERTweet (multi-task: category, Asta Cita, embedding)
- **LLM:** Ollama local (policy brief generation)
- **Other Tools:** bun, uvicorn, Pydantic, requests

---
