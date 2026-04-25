"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema, LoginData } from "@/schemas/authSchema";
import { useAuthStore } from "@/store/useAuthStore";
import { useRouter } from "next/navigation";
import { ShieldCheck, Fingerprint } from "lucide-react";

export default function LoginPage() {
    const login = useAuthStore((state) => state.login);
    const router = useRouter();

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<LoginData>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginData) => {
        // Simulasi validasi ke API (Database Citizens)
        await new Promise((resolve) => setTimeout(resolve, 1000));

        login(data.nik, data.dob);
        router.push("/laporan"); // Arahkan ke form setelah login
    };

    return (
        <div className="flex min-h-[80vh] items-center justify-center px-4">
            <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
                <div className="mb-8 text-center">
                    <div className="bg-primary/10 mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full">
                        <Fingerprint className="text-primary h-8 w-8" />
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900">
                        Login Warga
                    </h1>
                    <p className="mt-2 text-sm text-gray-500">
                        Gunakan NIK dan Tanggal Lahir untuk memverifikasi
                        identitas Anda.
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

                    <div className="bg-accent/50 border-accent text-primary flex items-start gap-2 rounded-lg border p-4 text-xs">
                        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0" />
                        <p>
                            Data Anda dilindungi enkripsi dan hanya digunakan
                            untuk validasi laporan sistem Dukcapil.
                        </p>
                    </div>

                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="bg-primary text-primary-foreground hover:bg-primary/90 w-full rounded-lg px-4 py-3 font-medium disabled:opacity-70"
                    >
                        {isSubmitting ? "Memverifikasi..." : "Masuk & Lapor"}
                    </button>
                </form>
            </div>
        </div>
    );
}
