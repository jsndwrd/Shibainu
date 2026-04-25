import { Users, AlertCircle, TrendingUp, Sparkles, MapPin } from "lucide-react";
import Link from "next/link";

export default function AdminOverview() {
    return (
        <div className="mx-auto max-w-7xl space-y-6">
            {/* Top Stat Cards */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                <div className="flex items-start justify-between rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <div>
                        <p className="mb-1 text-sm font-medium text-gray-500">
                            TOTAL ASPIRASI
                        </p>
                        <h3 className="text-3xl font-bold text-gray-900">
                            1,248,592
                        </h3>
                        <p className="mt-2 flex items-center gap-1 text-sm font-medium text-emerald-600">
                            <TrendingUp className="h-4 w-4" /> +12.4% MoM
                        </p>
                    </div>
                    <div className="rounded-lg bg-gray-50 p-3 text-gray-400">
                        <Users className="h-6 w-6" />
                    </div>
                </div>

                <div className="flex items-start justify-between rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <div>
                        <p className="mb-1 text-sm font-medium text-gray-500">
                            KLUSTER PRIORITAS
                        </p>
                        <h3 className="text-3xl font-bold text-gray-900">24</h3>
                        <p className="mt-2 text-sm text-gray-500">
                            Aktif dalam pemantauan
                        </p>
                    </div>
                    <div className="rounded-lg bg-red-50 p-3 text-red-500">
                        <AlertCircle className="h-6 w-6" />
                    </div>
                </div>

                <div className="flex items-start justify-between rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <div>
                        <p className="mb-1 text-sm font-medium text-gray-500">
                            SKOR URGENSI RATA-RATA
                        </p>
                        <h3 className="text-3xl font-bold text-gray-900">
                            78.4
                            <span className="text-lg font-normal text-gray-400">
                                /100
                            </span>
                        </h3>
                        <p className="mt-2 text-sm font-medium text-orange-500">
                            ⚠ Tingkat Tinggi
                        </p>
                    </div>
                    <div className="bg-primary/10 text-primary rounded-lg p-3">
                        <TrendingUp className="h-6 w-6" />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                {/* Left Column: Isu Prioritas */}
                <div className="space-y-4 lg:col-span-2">
                    <div className="flex items-center justify-between">
                        <h3 className="text-lg font-bold text-gray-900">
                            10 Isu Prioritas Nasional
                        </h3>
                    </div>

                    {/* Card Issue 1 */}
                    <div className="hover:border-primary/50 rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-colors">
                        <div className="mb-4 flex items-start justify-between">
                            <span className="bg-primary/10 text-primary rounded px-2 py-1 text-xs font-bold tracking-wider">
                                INFRASTRUKTUR
                            </span>
                            <div className="text-right">
                                <h4 className="text-primary text-3xl font-bold">
                                    94
                                </h4>
                                <p className="text-[10px] font-bold tracking-wider text-gray-400 uppercase">
                                    Priority Score
                                </p>
                            </div>
                        </div>
                        <h4 className="mb-2 text-xl font-bold text-gray-900">
                            Perbaikan Jalan Lintas Provinsi Jawa Timur
                        </h4>
                        <p className="mb-6 text-sm text-gray-500">
                            Analisis berdasarkan 14,203 laporan masyarakat &
                            petisi daerah.
                        </p>

                        <div className="mb-6 grid grid-cols-3 gap-4 border-t border-gray-100 pt-4">
                            <div>
                                <p className="mb-1 text-xs text-gray-400">
                                    Volume
                                </p>
                                <p className="font-semibold text-gray-900">
                                    14.2k Reports
                                </p>
                            </div>
                            <div>
                                <p className="mb-1 text-xs text-gray-400">
                                    Urgensi
                                </p>
                                <span className="rounded bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
                                    Sangat Tinggi
                                </span>
                            </div>
                            <div>
                                <p className="mb-1 text-xs text-gray-400">
                                    Sentiment AI
                                </p>
                                <p className="font-semibold text-red-600">
                                    Negatif (82%)
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex -space-x-2">
                                <div className="h-8 w-8 rounded-full border-2 border-white bg-gray-300"></div>
                                <div className="h-8 w-8 rounded-full border-2 border-white bg-gray-400"></div>
                                <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-gray-100 text-xs font-medium text-gray-500">
                                    +3
                                </div>
                            </div>
                            <Link
                                href="/admin/laporan"
                                className="text-primary bg-primary/10 hover:bg-primary/20 flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors"
                            >
                                <Sparkles className="h-4 w-4" /> Generate Policy
                                Brief
                            </Link>
                        </div>
                    </div>
                    {/* Add more cards as needed... */}
                </div>

                {/* Right Column: Visualisasi & Insights */}
                <div className="space-y-6">
                    {/* Skor Urgensi Chart */}
                    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                        <h4 className="mb-6 text-sm font-bold text-gray-800">
                            Visualisasi Skor Urgensi
                        </h4>
                        <div className="space-y-4">
                            {[
                                {
                                    label: "Infrastruktur",
                                    score: 94,
                                    color: "bg-primary",
                                },
                                {
                                    label: "Kesehatan",
                                    score: 88,
                                    color: "bg-primary/80",
                                },
                                {
                                    label: "Pendidikan",
                                    score: 82,
                                    color: "bg-primary/60",
                                },
                                {
                                    label: "Keamanan",
                                    score: 76,
                                    color: "bg-primary/40",
                                },
                                {
                                    label: "Lingkungan",
                                    score: 64,
                                    color: "bg-primary/30",
                                },
                            ].map((item) => (
                                <div key={item.label}>
                                    <div className="mb-1 flex justify-between text-sm">
                                        <span className="font-medium text-gray-700">
                                            {item.label}
                                        </span>
                                        <span className="font-bold text-gray-900">
                                            {item.score}
                                        </span>
                                    </div>
                                    <div className="h-2 w-full rounded-full bg-gray-100">
                                        <div
                                            className={`${item.color} h-2 rounded-full`}
                                            style={{ width: `${item.score}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button className="mt-6 w-full rounded-lg border border-gray-300 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
                            Lihat Detail Statistik
                        </button>
                    </div>

                    {/* AI Insight */}
                    <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-6">
                        <div className="text-primary mb-4 flex items-center gap-2 font-semibold">
                            <Sparkles className="h-5 w-5" /> AI Insight Terkini
                        </div>
                        <p className="rounded-lg bg-white p-4 text-sm leading-relaxed text-gray-700 italic shadow-sm">
                            "Terdapat anomali peningkatan sentimen negatif
                            sebesar 30% di wilayah Jawa Timur terkait kelambatan
                            pengerjaan jalan tol dalam 48 jam terakhir.
                            Direkomendasikan evaluasi vendor segera."
                        </p>
                        <p className="mt-3 flex items-center gap-1 text-xs text-gray-500">
                            <TrendingUp className="h-3 w-3" /> Dianalisis 5
                            menit yang lalu
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
