"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { ShieldCheck, Fingerprint } from "lucide-react";

import { LoginRequest } from "@/lib/apiContract";

import { useAuthStore } from "@/store/useAuthStore";
import z from "zod";

export default function LoginPage() {
  const router = useRouter();

  const { login, isLoading, clearError } = useAuthStore();

  const [apiError, setApiError] = useState("");

  const loginSchema = z.object({
    nik: z
      .string()
      .trim()
      .min(1, "NIK wajib diisi")
      .length(16, "NIK harus 16 digit")
      .regex(/^\d+$/, "NIK hanya boleh angka"),

    dob: z
      .string()
      .min(1, "Tanggal lahir wajib diisi")
      .refine((value) => !Number.isNaN(Date.parse(value)), {
        message: "Format tanggal lahir tidak valid",
      }),
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginRequest>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      nik: "",
      dob: "",
    },
  });

  const onSubmit = async (data: LoginRequest) => {
    try {
      clearError();
      setApiError("");

      await login(data);

      router.push("/laporan");
    } catch (error: any) {
      setApiError(error?.message || "Login gagal.");
    }
  };

  const disabled = isSubmitting || isLoading;

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <div className="mb-8 text-center">
          <div className="bg-primary/10 mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full">
            <Fingerprint className="text-primary h-8 w-8" />
          </div>

          <h1 className="text-2xl font-bold text-gray-900">Login Warga</h1>

          <p className="mt-2 text-sm text-gray-500">
            Gunakan NIK dan Tanggal Lahir untuk memverifikasi identitas Anda.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Nomor Induk Kependudukan (NIK)
            </label>

            <input
              {...register("nik")}
              placeholder="Masukkan 16 digit NIK"
              maxLength={16}
              className="focus:border-primary focus:ring-primary w-full rounded-lg border border-gray-300 p-3 outline-none focus:ring-1"
            />

            {errors.nik && (
              <p className="text-destructive mt-1 text-xs">
                {errors.nik.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Tanggal Lahir
            </label>

            <input
              type="date"
              {...register("dob")}
              className="focus:border-primary focus:ring-primary w-full rounded-lg border border-gray-300 p-3 outline-none focus:ring-1"
            />

            {errors.dob && (
              <p className="text-destructive mt-1 text-xs">
                {errors.dob.message}
              </p>
            )}
          </div>

          {apiError && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
              {apiError}
            </div>
          )}

          <div className="bg-accent/50 border-accent text-primary flex items-start gap-2 rounded-lg border p-4 text-xs">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0" />

            <p>
              Data Anda dilindungi enkripsi dan hanya digunakan untuk validasi
              laporan sistem Dukcapil.
            </p>
          </div>

          <button
            type="submit"
            disabled={disabled}
            className="bg-primary text-primary-foreground hover:bg-primary/90 w-full rounded-lg px-4 py-3 font-medium disabled:cursor-not-allowed disabled:opacity-70"
          >
            {disabled ? "Memverifikasi..." : "Masuk & Lapor"}
          </button>
        </form>
      </div>
    </div>
  );
}
