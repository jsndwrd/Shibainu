"use client";

import { step3Schema } from "@/schemas/aspirasiSchema";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import { useReferenceStore } from "@/store/useReferenceStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { Brain, MapPin } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import z from "zod";

const Step3Lokasi = () => {
  type Step3FormValues = z.infer<typeof step3Schema>;

  const { formData, updateData, nextStep, prevStep } = useAspirasiStore();

  const {
    provinces,
    regencies,
    fetchProvinces,
    fetchRegencies,
    resetRegencies,
    isLoadingProvinces,
    isLoadingRegencies,
    error: referenceError,
  } = useReferenceStore();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<Step3FormValues>({
    resolver: zodResolver(step3Schema),
    defaultValues: formData as Step3FormValues,
  });

  const selectedProvince = watch("provinsi");

  useEffect(() => {
    fetchProvinces().catch(() => {
      // error sudah masuk ke reference store
    });
  }, [fetchProvinces]);

  useEffect(() => {
    if (!selectedProvince) {
      resetRegencies();
      return;
    }

    setValue("kota", "" as never);

    fetchRegencies(selectedProvince).catch(() => {
      // error sudah masuk ke reference store
    });
  }, [selectedProvince, fetchRegencies, resetRegencies, setValue]);

  return (
    <form
      onSubmit={handleSubmit((data) => {
        updateData(data);
        nextStep();
      })}
      className="space-y-6"
    >
      <div className="text-primary mb-4 flex items-center gap-2 font-semibold">
        <MapPin className="h-5 w-5" />
        <h3>Lokasi & Klasifikasi Otomatis</h3>
      </div>

      {referenceError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
          {referenceError}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Provinsi
          </label>

          <select
            {...register("provinsi")}
            disabled={isLoadingProvinces}
            className="focus:ring-accent w-full rounded-lg border border-gray-300 bg-white p-3 outline-none focus:ring-2 disabled:bg-gray-100"
          >
            <option value="">
              {isLoadingProvinces ? "Memuat provinsi..." : "Pilih Provinsi"}
            </option>

            {provinces.map((province) => (
              <option key={province.code} value={province.name}>
                {province.name}
              </option>
            ))}
          </select>

          {errors.provinsi && (
            <p className="mt-1 text-xs text-red-500">
              {errors.provinsi.message as string}
            </p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Kota / Kabupaten
          </label>

          <select
            {...register("kota")}
            disabled={!selectedProvince || isLoadingRegencies}
            className="focus:ring-accent w-full rounded-lg border border-gray-300 bg-white p-3 outline-none focus:ring-2 disabled:bg-gray-100"
          >
            <option value="">
              {isLoadingRegencies
                ? "Memuat kota/kabupaten..."
                : "Pilih Kota/Kabupaten"}
            </option>

            {regencies.map((regency) => (
              <option key={regency.code} value={regency.name}>
                {regency.name}
              </option>
            ))}
          </select>

          {errors.kota && (
            <p className="mt-1 text-xs text-red-500">
              {errors.kota.message as string}
            </p>
          )}
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700">
          Lokasi Kejadian Lengkap
        </label>

        <input
          {...register("lokasiDetail")}
          placeholder="Nama jalan, gedung, atau patokan spesifik"
          className="focus:ring-accent w-full rounded-lg border border-gray-300 p-3 outline-none focus:ring-2"
        />

        {errors.lokasiDetail && (
          <p className="mt-1 text-xs text-red-500">
            {errors.lokasiDetail.message as string}
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 gap-8">
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <div className="mb-2 flex items-center gap-2 font-semibold text-emerald-800">
            <Brain className="h-5 w-5" />
            Klasifikasi Otomatis
          </div>

          <p className="text-sm leading-6 text-emerald-700">
            Anda tidak perlu memilih tingkat urgensi. Sistem akan menentukan
            apakah aspirasi ini bersifat <strong>strategis</strong> atau{" "}
            <strong>operasional</strong> berdasarkan isi laporan, kategori,
            lokasi, dan pola data yang tersedia.
          </p>
        </div>
        <div>
          {/* <label className="mb-2 block text-sm font-medium text-gray-700">
            Instansi Tujuan
          </label> */}

          <input
            type="hidden"
            {...register("instansiTujuan")}
            value="Kementerian PUPR"
          />
        </div>
      </div>

      <div className="flex justify-between border-t border-gray-100 pt-6">
        <button
          type="button"
          className="border-primary text-primary rounded-lg border px-6 py-3 font-medium hover:bg-emerald-50"
        >
          Simpan Draft
        </button>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={prevStep}
            className="rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-700 hover:bg-gray-50"
          >
            Kembali
          </button>

          <button
            type="submit"
            className="bg-primary hover:bg-primary/90 rounded-lg px-6 py-3 font-medium text-white"
          >
            Lanjutkan ke Review
          </button>
        </div>
      </div>
    </form>
  );
};

export default Step3Lokasi;
