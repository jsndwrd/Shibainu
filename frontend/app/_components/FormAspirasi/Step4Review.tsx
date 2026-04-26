"use client";

import { useAspirasiStore } from "@/store/useAspirasiStore";
import { Brain, CheckCircle } from "lucide-react";
import { useState } from "react";

const Step4Review = () => {
  const { formData, prevStep, resetForm, submitAspirasi, isSubmitting, error } =
    useAspirasiStore();

  const [result, setResult] = useState<{
    policy_level?: string | null;
    routing_target?: string | null;
    policy_level_confidence?: number | null;
    policy_level_reason?: string | null;
  } | null>(null);

  const handleSubmit = async () => {
    try {
      const response = await submitAspirasi();

      setResult({
        policy_level: response.policy_level,
        routing_target: response.routing_target,
        policy_level_confidence: response.policy_level_confidence,
        policy_level_reason: response.policy_level_reason,
      });

      alert("Laporan berhasil dikirim dan diklasifikasikan oleh sistem.");
    } catch {
      // error sudah masuk ke store
    }
  };

  const handleReset = () => {
    setResult(null);
    resetForm();
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

      {result && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">
          <div className="mb-3 flex items-center gap-2 font-semibold text-emerald-800">
            <Brain className="h-5 w-5" />
            Hasil Klasifikasi Sistem
          </div>

          <div className="space-y-2 text-sm text-emerald-800">
            <p>
              Level Kebijakan:{" "}
              <strong className="uppercase">{result.policy_level}</strong>
            </p>

            <p>
              Routing: <strong>{result.routing_target}</strong>
            </p>

            <p>
              Confidence:{" "}
              <strong>
                {result.policy_level_confidence
                  ? `${Math.round(result.policy_level_confidence * 100)}%`
                  : "-"}
              </strong>
            </p>

            {result.policy_level_reason && (
              <p className="leading-6">{result.policy_level_reason}</p>
            )}
          </div>

          <button
            onClick={handleReset}
            className="mt-4 rounded-lg bg-emerald-700 px-5 py-2 text-sm font-medium text-white hover:bg-emerald-800"
          >
            Buat Laporan Baru
          </button>
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
          <span className="text-gray-500">Kategori</span>
          <span className="col-span-2 font-medium">
            {formData.kategoriAspirasi}
            {/* {formData.instansiTujuan || "Belum ditentukan"} */}
          </span>
        </div>

        <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
          <span className="text-gray-500">Lokasi</span>
          <span className="col-span-2 font-medium">
            {formData.lokasiDetail}, {formData.kota}, {formData.provinsi}
          </span>
        </div>

        <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
          <span className="text-gray-500">Klasifikasi</span>
          <span className="col-span-2 font-medium text-gray-700">
            Ditentukan otomatis oleh sistem sebagai strategic atau operational.
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

      {!result && (
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
              ? "Mengirim & Mengklasifikasikan..."
              : "Kirim Aspirasi Sekarang"}
          </button>
        </div>
      )}
    </div>
  );
};

export default Step4Review;
