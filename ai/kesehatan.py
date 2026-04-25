import json, os

samples_kesehatan = [
    "BPJS saya aktif tapi ditolak di IGD RS, katanya kuota penuh. ini gimana??",
    "obat di puskesmas selalu habis, disuruh beli sendiri di apotek luar terus",
    "dokter di puskesmas kecamatan kami cuma dateng seminggu sekali, sisanya tutup",
    "antrian puskesmas dari jam 5 pagi tapi dokternya baru dateng jam 10 lebih",
    "mau dirujuk ke RS harus nunggu 2 minggu, padahal kondisi udah gawat",
    "ambulans desa rusak dari tahun lalu ga diperbaiki, warga mau berobat susah",
    "anak gw stunting tapi posyandu tutup terus, kadernya ga pernah ada",
    "pelayanan BPJS dipersulit banget, bolak balik minta surat ini itu capek",
    "puskesmas tutup siang padahal belum jam 12, petugasnya pada kemana?",
    "obat generik selalu kosong, dipaksa beli di apotek sendiri padahal udah ada BPJS",
    "ga ada dokter spesialis di RSUD sini, harus ke kota jauh banget buat periksa",
    "bidan desa udah lama ga aktif, ibu hamil di kampung kami ga ada yang periksa",
    "vaksin anak di posyandu sering telat datengnya, stoknya katanya habis mulu",
    "faskes di desa kami cuma satu, kalau dokternya sakit langsung tutup total",
    "rujukan BPJS ditolak RS swasta, padahal RS pemerintah penuh, kami mau gimana",
]

os.makedirs('data/baseline', exist_ok=True)
data = {
    "kategori": "Kesehatan",
    "source": "manual_curated_lapor_gmaps",
    "count": len(samples_kesehatan),
    "samples": samples_kesehatan
}

with open('data/baseline/baseline_kesehatan.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Saved {len(samples_kesehatan)} samples → data/baseline/baseline_kesehatan.json")