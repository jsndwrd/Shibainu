"use client";

import { useAspirasiStore } from "@/store/useAspirasiStore";
import { CheckCircle } from "lucide-react";

const Step4Review = () => {
  const { formData, prevStep, resetForm, submitAspirasi, isSubmitting, error } =
    useAspirasiStore();

  const handleSubmit = async () => {
    try {
      await submitAspirasi();
      alert("Laporan berhasil dikirim ke sistem terpadu!");
      resetForm();
    } catch {}
  };

  return (
    <div className="space-y-6">
      <div className="text-primary mb-4 flex items-center gap-2 font-semibold">
        <CheckCircle className="h-5 w-5" />
        <h3>Review Laporan Anda</h3>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      <div className="space-y-4 rounded-xl border border-gray-200 bg-gray-50 p-6 text-sm">
        <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
          <span className="text-gray-500">Judul</span>
          <span className="col-span-2 font-medium">
            {formData.judulLaporan}
          </span>
        </div>

        <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
          <span className="text-gray-500">Kategori & Instansi</span>
          <span className="col-span-2 font-medium">
            {formData.kategoriAspirasi} - {formData.instansiTujuan || "Daerah"}
          </span>
        </div>

        <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
          <span className="text-gray-500">Lokasi</span>
          <span className="col-span-2 font-medium">
            {formData.lokasiDetail}, {formData.kota}, {formData.provinsi}
          </span>
        </div>

        <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
          <span className="text-gray-500">Tingkat Urgensi</span>
          <span className="col-span-2 font-medium">
            {formData.tingkatUrgensi || 3}
          </span>
        </div>

        <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
          <span className="text-gray-500">Privasi</span>
          <span className="text-primary col-span-2 font-medium">
            {formData.isAnonim ? "Anonim" : "Publik"} &{" "}
            {formData.isRahasia ? "Rahasia" : "Terbuka"}
          </span>
        </div>
      </div>

      <div className="flex justify-between border-t border-gray-100 pt-6">
        <button
          onClick={prevStep}
          disabled={isSubmitting}
          className="rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-700 hover:cursor-pointer hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-70"
        >
          Ubah Data
        </button>

        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="bg-primary hover:bg-primary/90 flex items-center gap-2 rounded-lg px-8 py-3 font-medium text-white hover:cursor-pointer disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSubmitting
            ? "Memproses Enkripsi & Mengirim..."
            : "Kirim Aspirasi Sekarang"}
        </button>
      </div>
    </div>
  );
};

export default Step4Review;
