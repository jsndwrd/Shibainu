import { z } from "zod";

export const step1Schema = z.object({
  namaLengkap: z.string().min(1, "Nama wajib diisi"),
  nik: z.string().length(16, "NIK harus 16 digit"),
  isAnonim: z.boolean().default(false), // Dari Panduan
  isRahasia: z.boolean().default(false), // Dari Panduan
});

export const step2Schema = z.object({
  kategoriAspirasi: z.string().min(1, "Pilih kategori"),
  judulLaporan: z.string().min(5, "Judul minimal 5 karakter"), // Dari Panduan
  deskripsi: z.string().min(20, "Deskripsi minimal 20 karakter").max(2000),
  tanggalKejadian: z.string().min(1, "Tanggal kejadian wajib diisi"), // Dari Panduan
  lampiran: z.any().optional(), // Dari Panduan
});

export const step3Schema = z.object({
  provinsi: z.string().min(1, "Pilih provinsi"),
  kota: z.string().min(1, "Pilih kota/kabupaten"),
  lokasiDetail: z.string().min(5, "Detail lokasi kejadian wajib diisi"), // Dari Panduan
  instansiTujuan: z.string().optional(), // Dari Panduan (Opsional)
  tingkatUrgensi: z.enum([
    "Sangat Rendah",
    "Rendah",
    "Sedang",
    "Tinggi",
    "Kritis",
  ]),
});

export const finalSchema = step1Schema.merge(step2Schema).merge(step3Schema);
export type AspirasiData = z.infer<typeof finalSchema>;
