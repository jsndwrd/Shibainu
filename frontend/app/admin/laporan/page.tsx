import {
    ArrowLeft,
    Sparkles,
    Download,
    Share2,
    CheckCircle,
    ShieldAlert,
    AlertCircle,
} from "lucide-react";
import Link from "next/link";

export default function LaporanAnalitik() {
    return (
        <div className="mx-auto max-w-4xl space-y-6 pb-20">
            {/* Top Navigation */}
            <div className="flex items-center justify-between">
                <Link
                    href="/admin"
                    className="flex items-center gap-2 text-sm font-medium text-gray-500 transition-colors hover:text-gray-900"
                >
                    <ArrowLeft className="h-4 w-4" /> Kembali ke Laporan
                    Analitik
                </Link>
                <div className="flex items-center gap-3">
                    <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800">
                        SEGERA
                    </span>
                    <span className="flex items-center gap-1 text-xs text-gray-400">
                        <Sparkles className="h-3 w-3" /> AI Generated Brief v2.4
                    </span>
                </div>
            </div>

            {/* Document Paper */}
            <div className="rounded-xl border border-gray-200 bg-white p-10 shadow-sm md:p-16">
                {/* Header KOP Surat */}
                <div className="mb-8 border-b-2 border-gray-900 pb-6 text-center">
                    <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-lg bg-gray-200">
                        <ShieldAlert className="h-8 w-8 text-gray-500" />
                    </div>
                    <h2 className="text-xl font-bold tracking-wide text-gray-900 uppercase">
                        Pemerintah Republik Indonesia
                    </h2>
                    <h3 className="text-primary mt-1 text-lg font-bold tracking-wide uppercase">
                        Pusat Analisis Data Aspirasi Publik (NAWA)
                    </h3>
                    <p className="mt-2 text-sm text-gray-500">
                        Sistem Terintegrasi Kebijakan Berbasis Bukti Digital
                    </p>
                </div>

                {/* Title & Meta */}
                <h1 className="border-primary mb-6 border-l-4 pl-4 text-2xl leading-snug font-bold text-gray-900 md:text-3xl">
                    Brief Kebijakan: Kerusakan Infrastruktur Jalan di Jawa Timur
                </h1>

                <div className="mb-10 flex flex-wrap gap-6 text-sm font-medium text-gray-600">
                    <p>Nomor: AI/BRF/2026/JT-091</p>
                    <p>Tanggal: 25 April 2026</p>
                    <p>
                        Sifat:{" "}
                        <span className="font-bold text-red-600">
                            Prioritas Tinggi
                        </span>
                    </p>
                </div>

                {/* Ringkasan Eksekutif */}
                <div className="bg-primary/5 border-primary/20 mb-10 rounded-xl border p-6">
                    <h3 className="text-primary mb-3 flex items-center gap-2 text-lg font-bold">
                        <Sparkles className="h-5 w-5" /> Ringkasan Eksekutif
                    </h3>
                    <p className="text-sm leading-relaxed text-gray-700">
                        Analisis berbasis AI terhadap 12.450 laporan publik
                        dalam 30 hari terakhir mengidentifikasi eskalasi
                        signifikan keluhan infrastruktur di wilayah Jawa Timur
                        bagian barat. Data menunjukkan korelasi 88% antara curah
                        hujan ekstrem dengan percepatan kerusakan jalan provinsi
                        kelas B. Diperlukan intervensi segera guna mencegah
                        gangguan logistik antarwilayah.
                    </p>
                </div>

                {/* Isu Utama Grid */}
                <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-gray-900">
                    <AlertCircle className="h-5 w-5 text-gray-400" /> Isu Utama
                </h3>
                <div className="mb-10 grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div className="rounded-xl border border-gray-200 p-5">
                        <h4 className="text-primary mb-1 text-2xl font-bold">
                            42%
                        </h4>
                        <p className="mb-1 text-sm font-bold text-gray-900">
                            Eskalasi Kerusakan
                        </p>
                        <p className="text-xs text-gray-500">
                            Peningkatan lubang di jalan utama Kab. Madiun dalam
                            dua minggu terakhir.
                        </p>
                    </div>
                    <div className="rounded-xl border border-gray-200 p-5">
                        <h4 className="mb-1 text-2xl font-bold text-gray-900">
                            15.2h
                        </h4>
                        <p className="mb-1 text-sm font-bold text-gray-900">
                            Waktu Respon Publik
                        </p>
                        <p className="text-xs text-gray-500">
                            Rata-rata waktu atensi keluhan dari instansi memicu
                            sentimen negatif (82%).
                        </p>
                    </div>
                    <div className="rounded-xl border border-gray-200 p-5">
                        <h4 className="mb-1 text-2xl font-bold text-gray-900">
                            874
                        </h4>
                        <p className="mb-1 text-sm font-bold text-gray-900">
                            Laporan Terverifikasi
                        </p>
                        <p className="text-xs text-gray-500">
                            Laporan masyarakat dengan bukti foto (geotag)
                            divalidasi oleh AI sistem.
                        </p>
                    </div>
                    <div className="rounded-xl border border-gray-200 p-5">
                        <h4 className="mb-1 text-2xl font-bold text-gray-900">
                            B+
                        </h4>
                        <p className="mb-1 text-sm font-bold text-gray-900">
                            Indeks Kerentanan
                        </p>
                        <p className="text-xs text-gray-500">
                            Wilayah dengan risiko kecelakaan tinggi akibat
                            lubang jalan di malam hari.
                        </p>
                    </div>
                </div>

                {/* Rekomendasi Kebijakan */}
                <h3 className="mb-4 flex items-center gap-2 text-lg font-bold text-gray-900">
                    <CheckCircle className="h-5 w-5 text-gray-400" />{" "}
                    Rekomendasi Kebijakan
                </h3>
                <div className="mb-10 space-y-4">
                    {[
                        {
                            title: "Mobilisasi Tim Sapu Lubang (TSL)",
                            desc: "Pengerahan tim pemeliharaan jalan untuk penambalan darurat di 12 titik prioritas tinggi dalam waktu < 48 jam.",
                        },
                        {
                            title: "Audit Anggaran Pemeliharaan",
                            desc: "Realokasi dana darurat bencana infrastruktur sebesar Rp 4,2 Miliar dari pos anggaran cadangan provinsi.",
                        },
                        {
                            title: "Pemasangan Sensor AI-IoT",
                            desc: "Implementasi sistem monitoring keretakan jalan berbasis sensor getaran pada jalur logistik utama guna deteksi dini.",
                        },
                    ].map((item, idx) => (
                        <div key={idx} className="flex items-start gap-4">
                            <div className="bg-primary/10 text-primary flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold">
                                {idx + 1}
                            </div>
                            <div>
                                <h4 className="text-sm font-bold text-gray-900">
                                    {item.title}
                                </h4>
                                <p className="mt-1 text-sm text-gray-600">
                                    {item.desc}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="flex items-center justify-between border-t border-gray-200 pt-8">
                    <div className="text-xs text-gray-400">
                        Dokumen dicetak pada: 25 April 2026
                    </div>
                    <div className="text-right">
                        <p className="text-sm font-bold text-gray-900">
                            Nawa Analysis Engine
                        </p>
                        <p className="text-xs text-gray-500">
                            Automated Policy Brief Generator
                        </p>
                    </div>
                </div>
            </div>

            {/* Action Bar Bottom */}
            <div className="flex justify-center gap-4">
                <button className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50">
                    <Download className="h-4 w-4" /> Unduh PDF
                </button>
                <button className="flex items-center gap-2 rounded-lg bg-gray-800 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-gray-900">
                    <Share2 className="h-4 w-4" /> Bagikan ke Instansi Terkait
                </button>
                <button className="bg-primary hover:bg-primary/90 flex items-center gap-2 rounded-lg px-6 py-3 text-sm font-medium text-white transition-colors">
                    <CheckCircle className="h-4 w-4" /> Tandai Selesai
                </button>
            </div>
        </div>
    );
}
