"use client";

import { step1Schema } from "@/schemas/aspirasiSchema";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { User } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import z from "zod";

const Step1Identitas = () => {
  const {
    formData,
    updateData,
    nextStep,
    fetchMe,
    hydrateAuthFromStorage,
    user,
    isLoading,
    error,
  } = useAspirasiStore();

  type Step1FormValues = z.input<typeof step1Schema>;

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<Step1FormValues>({
    resolver: zodResolver(step1Schema),
    defaultValues: {
      namaLengkap: formData.namaLengkap ?? "",
      nik: formData.nik ?? "",
      isAnonim: formData.isAnonim ?? false,
      isRahasia: formData.isRahasia ?? false,
    },
  });

  useEffect(() => {
    hydrateAuthFromStorage();

    fetchMe().catch(() => {
      // error sudah disimpan di store
    });
  }, [hydrateAuthFromStorage, fetchMe]);

  useEffect(() => {
    if (!user) return;

    const fullName = user.full_name ?? "Warga Terverifikasi";

    setValue("namaLengkap", fullName);
    setValue("nik", user.nik ?? "");

    updateData({
      namaLengkap: fullName,
      nik: user.nik ?? "",
    } as Partial<Step1FormValues>);
  }, [user, setValue, updateData]);

  return (
    <form
      onSubmit={handleSubmit((data) => {
        updateData(data);
        nextStep();
      })}
      className="space-y-6"
    >
      <div className="text-primary mb-4 flex items-center gap-2 font-semibold">
        <User className="h-5 w-5" />
        <h3>Identitas Pelapor</h3>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Nama Lengkap
          </label>

          <input
            {...register("namaLengkap")}
            readOnly
            className="w-full rounded-lg border border-gray-200 bg-gray-100 p-3 text-gray-600"
          />

          {errors.namaLengkap && (
            <p className="mt-1 text-sm text-red-500">
              {errors.namaLengkap.message}
            </p>
          )}
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">
            NIK
          </label>

          <input
            {...register("nik")}
            readOnly
            className="w-full rounded-lg border border-gray-200 bg-gray-100 p-3 text-gray-600"
          />

          {errors.nik && (
            <p className="mt-1 text-sm text-red-500">{errors.nik.message}</p>
          )}
        </div>
      </div>

      <div className="mt-4 flex gap-6">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            {...register("isAnonim")}
            className="text-primary h-4 w-4 rounded"
          />
          Anonimkan Nama Saya
        </label>

        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            {...register("isRahasia")}
            className="text-primary h-4 w-4 rounded"
          />
          Rahasiakan Laporan Ini
        </label>
      </div>

      <div className="flex justify-end border-t border-gray-100 pt-6">
        <button
          type="submit"
          disabled={isLoading}
          className="bg-primary hover:bg-primary/80 rounded-lg px-6 py-3 font-medium text-white disabled:opacity-70"
        >
          {isLoading ? "Memuat..." : "Lanjutkan ke Detail"}
        </button>
      </div>
    </form>
  );
};

export default Step1Identitas;
