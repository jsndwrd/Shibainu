"use client";

import { useAspirasiStore } from "@/store/useAspirasiStore";
import { CheckCircle2, ShieldCheck, Cpu } from "lucide-react";

export default function FormLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { step } = useAspirasiStore();

    const steps = [
        { id: 1, title: "Identitas", desc: "Terverifikasi NIK" },
        { id: 2, title: "Detail Aspirasi", desc: "Kategori & Deskripsi" },
        { id: 3, title: "Lokasi & Dampak", desc: "Cakupan wilayah" },
        { id: 4, title: "Review & Kirim", desc: "Finalisasi laporan" },
    ];

    return (
        <div className="mx-auto flex max-w-6xl flex-col items-start gap-8 p-6 md:flex-row">
            <aside className="w-full shrink-0 space-y-6 md:w-80">
                <div className="rounded-xl border border-gray-200 bg-white p-6">
                    <h2 className="mb-2 text-lg font-semibold text-gray-900">
                        Progres Aspirasi
                    </h2>
                    <p className="mb-6 text-sm text-gray-500">
                        Lengkapi 4 langkah berikut
                    </p>

                    <div className="relative space-y-6">
                        {steps.map((s, idx) => {
                            const isActive = step === s.id;
                            const isPast = step > s.id;
                            return (
                                <div
                                    key={s.id}
                                    className="relative z-10 flex gap-4"
                                >
                                    <div
                                        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 ${
                                            isPast
                                                ? "border-primary bg-primary text-white"
                                                : isActive
                                                  ? "border-primary text-primary bg-accent/50"
                                                  : "border-gray-300 text-gray-400"
                                        }`}
                                    >
                                        {isPast ? (
                                            <CheckCircle2 className="h-5 w-5" />
                                        ) : (
                                            <span className="text-sm font-medium">
                                                {s.id}
                                            </span>
                                        )}
                                    </div>
                                    <div>
                                        <p
                                            className={`font-medium ${isActive || isPast ? "text-gray-900" : "text-gray-500"}`}
                                        >
                                            {s.title}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {s.desc}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Info Keamanan Box */}
                <div className="border-accent bg-accent/50 flex gap-3 rounded-xl border p-6">
                    <ShieldCheck className="text-primary/90 h-6 w-6 shrink-0" />
                    <div>
                        <h3 className="text-primary mb-1 text-sm font-semibold">
                            INFO KEAMANAN
                        </h3>
                        <p className="text-primary text-xs leading-relaxed">
                            Data Anda dilindungi enkripsi tingkat negara dan
                            terhubung langsung ke Dashboard Pemerintah
                            (Otentikasi NIK).
                        </p>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <div className="w-full flex-1 space-y-6">
                <div className="rounded-xl border border-gray-200 bg-white p-8">
                    <div className="mb-8 border-b border-gray-100 pb-6">
                        <h1 className="mb-2 text-xl font-semibold text-gray-900">
                            Sampaikan Aspirasi Anda
                        </h1>
                        <p className="text-sm text-gray-500">
                            Gunakan formulir di bawah ini untuk menyampaikan
                            masukan, keluhan, atau ide pembangunan kepada
                            pemerintah secara transparan.
                        </p>
                    </div>
                    {children}
                </div>

                {/* AI Predictive Analytics Box (UI Match) */}
                {step === 2 && (
                    <div className="border-accent flex items-start gap-4 rounded-xl border bg-emerald-50 p-6">
                        <Cpu className="text-primary/90 mt-1 h-6 w-6" />
                        <div>
                            <h4 className="text-primary font-semibold">
                                Analisis Prediktif AI
                            </h4>
                            <p className="text-primary mt-1 text-sm">
                                Berdasarkan kategori Infrastruktur yang Anda
                                pilih, rata-rata waktu respon pemerintah di
                                wilayah Jawa Barat adalah 4-7 hari kerja.
                                Pastikan menyertakan foto lokasi untuk
                                mempercepat verifikasi.
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
