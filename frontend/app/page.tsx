import Image from "next/image";
import Link from "next/link";
import {
    Sparkles,
    MessageSquareText,
    ShieldAlert,
    ShieldCheck,
    Activity,
    FileText,
} from "lucide-react";
import Dukcapil from "@/public/dukcapil.png";
import Bappenas from "@/public/bappenas.png";
import Kominfo from "@/public/kominfo.png";

export default function LandingPage() {
    return (
        <div className="flex w-full flex-col">
            {/* HERO SECTION */}
            <section className="container mx-auto flex flex-col items-center gap-12 px-6 py-16 md:flex-row md:py-24 lg:px-10">
                {/* Left Content */}
                <div className="flex-1 space-y-6">
                    <div className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-4 py-1.5 text-sm font-medium text-gray-700">
                        <Sparkles className="h-4 w-4 text-gray-500" />
                        AI-Powered Policy Platform
                    </div>

                    <h1 className="text-4xl leading-tight font-bold text-gray-900 md:text-5xl">
                        Suara Anda, Kebijakan Kita
                    </h1>

                    <p className="text-lg font-medium text-gray-800">
                        Platform Aspirasi Berbasis AI untuk Transformasi
                        Kebijakan Publik
                    </p>

                    <p className="max-w-lg leading-relaxed text-gray-500">
                        Mendukung partisipasi aktif masyarakat Indonesia melalui
                        analisis data real-time untuk menciptakan kebijakan yang
                        lebih inklusif dan transparan.
                    </p>

                    <div className="flex flex-col gap-4 pt-4 sm:flex-row">
                        <Link
                            href="/laporan"
                            className="bg-primary hover:bg-primary/90 rounded-lg px-6 py-3 text-center font-medium text-white transition-colors"
                        >
                            Sampaikan Aspirasi Sekarang
                        </Link>
                        <Link
                            href="/stats"
                            className="rounded-lg border border-gray-300 px-6 py-3 text-center font-medium text-gray-700 transition-colors hover:bg-gray-50"
                        >
                            Lihat Statistik Nasional
                        </Link>
                    </div>
                </div>

                {/* Right Content (Mockup UI Card) */}
                <div className="w-full max-w-md flex-1 md:max-w-none">
                    <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-[0_8px_30px_rgb(0,0,0,0.08)]">
                        <div className="mb-6 flex items-center justify-between">
                            <h3 className="font-semibold text-gray-800">
                                Aspirasi Terkini
                            </h3>
                            <span className="rounded bg-emerald-100 px-2 py-1 text-xs font-bold text-emerald-800">
                                LIVE
                            </span>
                        </div>

                        <div className="mb-6 space-y-3">
                            <div className="flex items-start gap-3 rounded-xl border border-gray-100 bg-gray-50 p-4">
                                <MessageSquareText className="mt-0.5 h-5 w-5 shrink-0 text-gray-500" />
                                <div>
                                    <h4 className="text-sm font-medium text-gray-900">
                                        Analisis Sentimen: Transportasi Publik
                                    </h4>
                                    <p className="mt-1 text-xs text-gray-500">
                                        87% Warga mendukung perluasan rute MRT
                                        di Jakarta Barat.
                                    </p>
                                </div>
                            </div>
                            <div className="border-accent bg-primary/20 flex items-start gap-3 rounded-xl border p-4">
                                <ShieldAlert className="text-primary/90 mt-0.5 h-5 w-5 shrink-0" />
                                <div>
                                    <h4 className="text-primary text-sm font-medium">
                                        Urgent: Akses Air Bersih
                                    </h4>
                                    <p className="text-primary/90 mt-1 text-xs">
                                        Laporan terverifikasi di 4 wilayah Jawa
                                        Tengah meningkat 15%.
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-start gap-3 rounded-xl border border-gray-100 bg-gray-50 p-4">
                                <MessageSquareText className="mt-0.5 h-5 w-5 shrink-0 text-gray-500" />
                                <div>
                                    <h4 className="text-sm font-medium text-gray-900">
                                        Analisis Sentimen: Transportasi Publik
                                    </h4>
                                    <p className="mt-1 text-xs text-gray-500">
                                        87% Warga mendukung perluasan rute MRT
                                        di Jakarta Barat.
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 rounded-xl border border-gray-100 bg-gray-50 p-4">
                                <MessageSquareText className="mt-0.5 h-5 w-5 shrink-0 text-gray-500" />
                                <div>
                                    <h4 className="text-sm font-medium text-gray-900">
                                        Analisis Sentimen: Transportasi Publik
                                    </h4>
                                    <p className="mt-1 text-xs text-gray-500">
                                        87% Warga mendukung perluasan rute MRT
                                        di Jakarta Barat.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* FEATURES SECTION */}
            <section className="bg-gray-50 px-6 py-20 lg:px-10">
                <div className="container mx-auto mb-16 max-w-3xl text-center">
                    <h2 className="mb-2 text-sm font-bold tracking-wider text-gray-400 uppercase">
                        Inovasi Digital Nasional
                    </h2>
                    <p className="text-2xl leading-relaxed font-medium text-gray-800">
                        Membangun ekosistem demokrasi digital yang aman,
                        transparan, dan dapat ditindaklanjuti secara instan.
                    </p>
                </div>

                <div className="container mx-auto grid grid-cols-1 gap-6 md:grid-cols-3">
                    {/* Feature 1 */}
                    <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
                        <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-lg bg-gray-100">
                            <ShieldCheck className="h-6 w-6 text-gray-700" />
                        </div>
                        <h3 className="mb-3 text-lg font-semibold text-gray-900">
                            1 NIK = 1 Suara
                        </h3>
                        <p className="text-sm leading-relaxed text-gray-500">
                            Integrasi langsung dengan data kependudukan Dukcapil
                            memastikan setiap aspirasi sah dan bebas dari
                            manipulasi bot.
                        </p>
                    </div>

                    {/* Feature 2 (Accent / Primary) */}
                    <div className="bg-primary rounded-2xl p-8 shadow-md">
                        <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-lg bg-white/20">
                            <Activity className="h-6 w-6 text-white" />
                        </div>
                        <h3 className="mb-3 text-lg font-semibold text-white">
                            Analisis AI Real-time
                        </h3>
                        <p className="text-sm leading-relaxed text-white/80">
                            Mesin pembelajaran kami mengelompokkan ribuan
                            aspirasi secara otomatis berdasarkan urgensi dan
                            wilayah administratif.
                        </p>
                    </div>

                    {/* Feature 3 */}
                    <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
                        <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-lg bg-gray-100">
                            <FileText className="h-6 w-6 text-gray-700" />
                        </div>
                        <h3 className="mb-3 text-lg font-semibold text-gray-900">
                            Brief Kebijakan Langsung
                        </h3>
                        <p className="text-sm leading-relaxed text-gray-500">
                            Mengonversi data aspirasi menjadi draf rekomendasi
                            kebijakan formal yang siap digunakan oleh para
                            pemangku kepentingan.
                        </p>
                    </div>
                </div>
            </section>

            {/* PARTNERS SECTION */}
            <section className="border-b border-gray-100 bg-white px-6 py-16">
                <div className="container mx-auto text-center">
                    <h3 className="mb-8 text-xs font-bold tracking-widest text-gray-400 uppercase">
                        Kolaborasi Institusi Negara
                    </h3>
                    <div className="flex flex-wrap items-center justify-center gap-8 opacity-60 grayscale transition-all duration-300 hover:grayscale-0 md:gap-16">
                        {/* Ganti div ini dengan <Image /> logo asli nantinya */}
                        <div className="flex items-center gap-2 text-xl font-bold text-gray-800">
                            <Image
                                src={Bappenas}
                                height={100}
                                width={100}
                                alt="bappenas"
                            />
                            BAPPENAS
                        </div>
                        <div className="flex items-center gap-2 text-xl font-bold text-gray-800">
                            <Image
                                src={Kominfo}
                                height={100}
                                width={100}
                                alt="bappenas"
                            />
                            KOMINFO
                        </div>
                        <div className="flex items-center gap-2 text-xl font-bold text-gray-800">
                            <Image
                                src={Dukcapil}
                                height={100}
                                width={100}
                                alt="bappenas"
                            />
                            DUKCAPIL
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA SECTION */}
            <section className="bg-primary px-6 py-20 text-center">
                <div className="container mx-auto max-w-2xl">
                    <h2 className="mb-4 text-3xl font-bold text-white">
                        Mulai Berpartisipasi Sekarang
                    </h2>
                    <p className="text-primary-foreground/80 mb-10 leading-relaxed text-white/80">
                        Jadilah bagian dari perubahan positif. Setiap suara yang
                        terverifikasi adalah kontribusi nyata bagi masa depan
                        Indonesia yang lebih baik.
                    </p>

                    <div className="mb-8 flex flex-col justify-center gap-4 sm:flex-row">
                        <button className="text-primary rounded-lg bg-white px-8 py-3 font-medium transition-colors hover:bg-gray-50">
                            Daftar dengan NIK
                        </button>
                        <button className="rounded-lg border border-white/30 px-8 py-3 font-medium text-white transition-colors hover:bg-white/10">
                            Panduan Pengguna
                        </button>
                    </div>

                    <p className="flex items-center justify-center gap-2 text-xs text-white/50">
                        <ShieldCheck className="h-4 w-4" /> Data dijamin aman
                        dan terenkripsi sesuai standar keamanan siber nasional.
                    </p>
                </div>
            </section>
        </div>
    );
}
