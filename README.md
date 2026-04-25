# SHIBAINU @ UC HACKFEST 2026

## Quick Commands

0. Concurrent Running

   ```bash
   (cd frontend && bun dev) & (cd backend && python -m fastapi dev)
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

- Runnning the project:

  ```bash
  fastapi dev
  ```

## Features (Not Detailed Yet)

### 1. Autentikasi Pengguna

- Login menggunakan NIK dan tanggal lahir.
- Token autentikasi berbasis bearer token.
- Penyimpanan token di frontend.
- Fetch data user melalui endpoint `/api/auth/me`.
- Logout user.

### 2. Role User dan Admin

- Sistem dapat membedakan role `user` dan `admin`.
- User diarahkan ke halaman aspirasi.
- Admin diarahkan ke dashboard admin.
- Navbar berubah otomatis berdasarkan role.
- Menu `Laporan` berubah menjadi `Dashboard` jika user memiliki role admin.

### 3. Form Aspirasi Multi-Step

- Step 1: Identitas pelapor.
- Step 2: Detail aspirasi.
- Step 3: Lokasi dan tingkat urgensi.
- Step 4: Review dan submit.
- Data form disimpan menggunakan Zustand store.
- Validasi form menggunakan Zod dan React Hook Form.
- Payload frontend disesuaikan dengan schema backend.

### 4. Submit Aspirasi

- User dapat mengirim aspirasi ke backend.
- Aspirasi dikirim ke endpoint `/api/aspirations/`.
- Sistem mengirim data seperti:
  - deskripsi aspirasi
  - kategori
  - provinsi
  - kabupaten atau kota
  - skala dampak
  - target level

### 5. Reference Data

- Data kategori diambil dari backend.
- Data provinsi diambil dari backend.
- Data kabupaten atau kota diambil berdasarkan provinsi.
- Dibuat store khusus `useReferenceStore` untuk mengelola:
  - categories
  - provinces
  - regencies

### 6. Dashboard Admin

- Dashboard admin mengambil data dari backend.
- Admin dapat melihat:
  - total aspirasi
  - total cluster
  - aspirasi kritis
  - jumlah policy brief
  - daftar aspirasi terbaru
  - cluster prioritas
  - top scores
  - policy brief terbaru

### 7. Cluster Aspirasi

- Aspirasi dapat dikelompokkan ke dalam cluster isu.
- Cluster menyimpan informasi seperti:
  - label
  - kategori
  - jumlah anggota
  - rata-rata urgensi
  - provinsi dominan
  - skor prioritas
  - sub-topik
  - distribusi urgensi
  - Asta Cita dominan

### 8. Policy Brief (Not Yet Integrated with AI)

- Admin dapat membuat policy brief dari cluster tertentu.
- Policy brief berisi ringkasan isu dan rekomendasi awal.
- Policy brief dapat ditampilkan di halaman detail admin.

## Technology Stack

- Next.js
- FastAPI
- PostgreSQL
- NLP

## CROSSCHECK LAGII

2. embedder predict category kurang detail, predict urgency worse masih if-else clause, cek generateEmbedding juga
3. recomputeCluster()
4. generateBrief harus connect ke AI-side nunggu athilluy
