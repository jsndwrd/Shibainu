"use client";

import { useEffect, useState } from "react";
import { step1Schema } from "@/schemas/aspirasiSchema";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import { useAuthStore } from "@/store/useAuthStore"; // <-- IMPORT AUTH STORE
import { zodResolver } from "@hookform/resolvers/zod";
import { User, AlertCircle } from "lucide-react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import z from "zod";
import Link from "next/link";

const Step1Identitas = () => {
    type Step1FormValues = z.infer<typeof step1Schema>;

    const { formData, updateData, nextStep } = useAspirasiStore();
    const { isAuthenticated, user } = useAuthStore(); // <-- CEK AUTH
    const router = useRouter();

    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    const {
        register,
        handleSubmit,
        setValue,
        formState: { errors },
    } = useForm({
        resolver: zodResolver(step1Schema),
        defaultValues: {
            ...formData,
            nik: user?.nik || formData.nik || "",
            namaLengkap: user ? "Warga Terverifikasi" : "",
        } as Step1FormValues,
    });
    useEffect(() => {
        setIsMounted(true);

        if (user) {
            setValue("nik", user.nik, { shouldValidate: true });
            setValue("namaLengkap", "Warga Terverifikasi", {
                shouldValidate: true,
            });
        }
    }, [user, setValue]);

    if (!isAuthenticated) {
        return (
            <div className="flex flex-col items-center justify-center rounded-xl border border-gray-200 bg-gray-50 py-12 text-center">
                <AlertCircle className="mb-4 h-12 w-12 text-gray-400" />
                <h3 className="mb-2 text-lg font-bold text-gray-900">
                    Autentikasi Diperlukan
                </h3>
                <p className="mb-6 text-sm text-gray-500">
                    Anda harus masuk menggunakan NIK untuk dapat mengirim
                    aspirasi.
                </p>
                <Link
                    href="/login"
                    className="bg-primary hover:bg-primary/90 rounded-lg px-6 py-3 font-medium text-white transition-colors"
                >
                    Login Sekarang
                </Link>
            </div>
        );
    }

    if (!isMounted) {
        return (
            <div className="flex animate-pulse flex-col items-center justify-center rounded-xl border border-gray-200 bg-gray-50 py-12 text-center">
                <div className="mb-4 h-12 w-12 rounded-full bg-gray-200"></div>
                <div className="mb-2 h-6 w-48 rounded bg-gray-200"></div>
                <div className="h-4 w-64 rounded bg-gray-200"></div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <div className="flex flex-col items-center justify-center rounded-xl border border-gray-200 bg-gray-50 py-12 text-center">
                <AlertCircle className="mb-4 h-12 w-12 text-gray-400" />
                <h3 className="mb-2 text-lg font-bold text-gray-900">
                    Autentikasi Diperlukan
                </h3>
                <p className="mb-6 text-sm text-gray-500">
                    Anda harus masuk menggunakan NIK untuk dapat mengirim
                    aspirasi.
                </p>
                <Link
                    href="/login"
                    className="bg-primary hover:bg-primary/90 rounded-lg px-6 py-3 font-medium text-white transition-colors"
                >
                    Login Sekarang
                </Link>
            </div>
        );
    }

    return (
        <form
            onSubmit={handleSubmit((d) => {
                updateData(d);
                nextStep();
            })}
            className="space-y-6"
        >
            <div className="text-primary mb-4 flex items-center gap-2 font-semibold">
                <User className="h-5 w-5" /> <h3>Identitas Pelapor</h3>
            </div>

            {/* Sisa form grid (Nama Lengkap, NIK, Checkboxes) tetap sama seperti sebelumnya */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        Nama Lengkap (Sesuai KTP)
                    </label>
                    <input
                        {...register("namaLengkap")}
                        className="w-full rounded-lg border border-gray-200 bg-gray-100 p-3 text-gray-600 outline-none"
                    />
                </div>
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        NIK (Tersensor)
                    </label>
                    <input
                        {...register("nik")}
                        readOnly
                        className="w-full cursor-not-allowed rounded-lg border border-gray-200 bg-gray-100 p-3 text-gray-600 outline-none"
                    />
                </div>
            </div>

            {/* ... Checkbox IsAnonim & IsRahasia ... */}

            <div className="flex justify-end border-t border-gray-100 pt-6">
                <button
                    type="submit"
                    className="bg-primary hover:bg-primary/80 rounded-lg px-6 py-3 font-medium text-white"
                >
                    Lanjutkan ke Detail
                </button>
            </div>
        </form>
    );
};

export default Step1Identitas;
