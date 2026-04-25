"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/useAuthStore";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import { useRouter } from "next/navigation";
import {
    User,
    MapPin,
    Calendar,
    CheckCircle2,
    Clock,
    FileText,
    XCircle,
    ChevronRight,
    Activity,
} from "lucide-react";
import Link from "next/link";

export default function ProfilePage() {
    const router = useRouter();
    const [isMounted, setIsMounted] = useState(false);

    // Auth Store
    const { isAuthenticated, user, fetchMe } = useAuthStore();

    // Aspirasi Store
    const {
        aspirations,
        fetchMyAspirations,
        isLoading: isAspirasiLoading,
    } = useAspirasiStore();

    // State untuk loading inisial
    const [isPageLoading, setIsPageLoading] = useState(true);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    // Fetch data saat halaman dimuat
    useEffect(() => {
        const loadData = async () => {
            if (!isMounted) return;

            // Jika belum login (berdasarkan state auth di localStorage), redirect ke login
            if (!isAuthenticated && !localStorage.getItem("access_token")) {
                router.push("/login");
                return;
            }

            try {
                // Ambil data user terbaru dan riwayat aspirasi secara paralel
                await Promise.all([
                    fetchMe().catch(() => {}), // Ignore if already cached/fetched
                    fetchMyAspirations(),
                ]);
            } catch (error) {
                console.error("Gagal memuat data profil", error);
            } finally {
                setIsPageLoading(false);
            }
        };

        loadData();
    }, [isMounted, isAuthenticated, router, fetchMe, fetchMyAspirations]);

    // Format Tanggal
    const formatDate = (dateString?: string) => {
        if (!dateString) return "-";
        return new Intl.DateTimeFormat("id-ID", {
            day: "numeric",
            month: "short",
            year: "numeric",
        }).format(new Date(dateString));
    };

    // Ekstrak Judul dari Deskripsi (Karena format: "Judul\n\nDeskripsi")
    const parseAspirationContent = (description: string) => {
        const parts = description.split("\n\n");
        const title = parts[0] || "Aspirasi Tanpa Judul";
        const body = parts.slice(1).join("\n\n") || title;
        return { title, body };
    };

    // Hitung Statistik
    const stats = {
        total: aspirations.length,
        disetujui: aspirations.filter(
            (a) => a.status === "processed" || a.status === "selesai",
        ).length,
        dalamProses: aspirations.filter(
            (a) => a.status === "in_progress" || a.status === "diproses",
        ).length,
        ditolak: aspirations.filter(
            (a) => a.status === "rejected" || a.status === "ditolak",
        ).length,
    };

    // Render Status Badge
    const renderStatusBadge = (status: string) => {
        const s = status?.toLowerCase() || "pending";
        if (s === "processed" || s === "selesai") {
            return (
                <span className="flex items-center gap-1.5 rounded-md bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-700">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Selesai
                </span>
            );
        }
        if (s === "in_progress" || s === "diproses") {
            return (
                <span className="flex items-center gap-1.5 rounded-md bg-gray-100 px-3 py-1 text-xs font-bold text-gray-700">
                    <Activity className="h-3.5 w-3.5" /> Dalam Proses
                </span>
            );
        }
        if (s === "rejected" || s === "ditolak") {
            return (
                <span className="flex items-center gap-1.5 rounded-md bg-red-100 px-3 py-1 text-xs font-bold text-red-700">
                    <XCircle className="h-3.5 w-3.5" /> Ditolak
                </span>
            );
        }
        return (
            <span className="flex items-center gap-1.5 rounded-md bg-orange-100 px-3 py-1 text-xs font-bold text-orange-700">
                <Clock className="h-3.5 w-3.5" /> Menunggu Review
            </span>
        );
    };

    if (!isMounted || isPageLoading) {
        return (
            <div className="mx-auto flex max-w-5xl animate-pulse flex-col gap-6 p-6 md:p-10">
                <div className="flex gap-6">
                    <div className="h-40 flex-1 rounded-xl bg-gray-200"></div>
                    <div className="h-40 w-1/3 rounded-xl bg-gray-200"></div>
                </div>
                <div className="h-24 w-full rounded-xl bg-gray-200"></div>
                <div className="h-64 w-full rounded-xl bg-gray-200"></div>
            </div>
        );
    }

    return (
        <div className="mx-auto min-h-screen max-w-6xl space-y-8 p-6 md:p-10">
            {/* Header / Profile & Quota Row */}
            <div className="flex flex-col gap-6 md:flex-row">
                {/* Profile Card */}
                <div className="flex flex-1 items-center gap-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                    <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-full border-4 border-white bg-gray-100 shadow-sm">
                        <User className="h-10 w-10 text-gray-400" />
                    </div>
                    <div>
                        {/* Nama bisa diambil dari user?.name jika ada di skema, jika tidak fallback ke NIK */}
                        <h1 className="text-2xl font-bold text-gray-900">
                            {user?.nik
                                ? `Warga (${user.nik.slice(0, 6)}***)`
                                : "Budi Santoso"}
                        </h1>
                        <div className="mt-2 flex flex-col gap-1.5 text-sm text-gray-500">
                            <span className="flex items-center gap-2">
                                <MapPin className="h-4 w-4 text-gray-400" />
                                {user?.province
                                    ? `${user.regency}, ${user.province}`
                                    : "DKI Jakarta"}
                            </span>
                            <span className="flex items-center gap-2">
                                <Calendar className="h-4 w-4 text-gray-400" />
                                Bergabung sejak{" "}
                                {formatDate(user?.created_at || "2023-07-01")}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Quota Card */}
                <div className="bg-primary relative flex w-full flex-col justify-center overflow-hidden rounded-2xl p-6 text-white shadow-md md:w-80">
                    <div className="absolute -top-10 -right-10 h-32 w-32 rounded-full bg-white/10 blur-2xl"></div>
                    <div className="relative z-10">
                        <div className="mb-4 flex items-center gap-2 font-medium text-white/90">
                            <FileText className="h-5 w-5" /> Kuota Aspirasi
                        </div>
                        <p className="mb-2 text-sm text-white/80">
                            Aspirasi Kuota 3/5 Digunakan
                        </p>
                        <div className="mb-1.5 flex items-center justify-between text-xs font-bold">
                            <span>Sisa 2</span>
                            <span>60%</span>
                        </div>
                        <div className="h-2 w-full overflow-hidden rounded-full bg-black/20">
                            <div className="bg-accent h-full w-[60%] rounded-full"></div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4 md:gap-6">
                <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                    <p className="mb-1 text-xs font-bold tracking-wider text-gray-400 uppercase">
                        TOTAL LAPORAN
                    </p>
                    <h3 className="text-3xl font-bold text-gray-900">
                        {stats.total}
                    </h3>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                    <p className="mb-1 text-xs font-bold tracking-wider text-gray-400 uppercase">
                        DISETUJUI
                    </p>
                    <h3 className="text-3xl font-bold text-emerald-600">
                        {stats.disetujui}
                    </h3>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                    <p className="mb-1 text-xs font-bold tracking-wider text-gray-400 uppercase">
                        DALAM PROSES
                    </p>
                    <h3 className="text-3xl font-bold text-orange-500">
                        {stats.dalamProses}
                    </h3>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                    <p className="mb-1 text-xs font-bold tracking-wider text-gray-400 uppercase">
                        DITOLAK
                    </p>
                    <h3 className="text-3xl font-bold text-red-600">
                        {stats.ditolak}
                    </h3>
                </div>
            </div>

            {/* Aspirations History */}
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                <h2 className="mb-6 text-xl font-bold text-gray-900">
                    Riwayat Aspirasi
                </h2>

                {aspirations.length === 0 && !isAspirasiLoading ? (
                    <div className="rounded-xl border border-dashed border-gray-200 bg-gray-50 py-12 text-center">
                        <FileText className="mx-auto mb-3 h-12 w-12 text-gray-300" />
                        <h3 className="font-medium text-gray-900">
                            Belum ada riwayat aspirasi
                        </h3>
                        <p className="mt-1 mb-4 text-sm text-gray-500">
                            Anda belum pernah mengirimkan laporan atau aspirasi.
                        </p>
                        <Link
                            href="/laporan"
                            className="bg-primary hover:bg-primary/90 inline-block rounded-lg px-6 py-2 text-sm font-medium text-white transition-colors"
                        >
                            Buat Laporan Baru
                        </Link>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {aspirations.map((item) => {
                            const { title, body } = parseAspirationContent(
                                item.description,
                            );

                            return (
                                <div
                                    key={item.id}
                                    className="group cursor-pointer rounded-xl border border-gray-100 p-5 transition-all hover:border-emerald-500/30 hover:shadow-md"
                                >
                                    <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
                                        <div className="flex-1">
                                            <div className="mb-2 flex items-center gap-3">
                                                <span className="bg-accent/20 text-primary rounded px-2.5 py-0.5 text-xs font-bold">
                                                    {item.category_user_input ||
                                                        item.predicted_category ||
                                                        "Umum"}
                                                </span>
                                                <span className="text-xs font-medium text-gray-400">
                                                    {/* Fallback ID jika tidak ada properti nomor tiket */}
                                                    {item.id
                                                        .split("-")[0]
                                                        .toUpperCase()}{" "}
                                                    •{" "}
                                                    {formatDate(
                                                        item.submitted_at,
                                                    )}
                                                </span>
                                            </div>
                                            <h3 className="group-hover:text-primary text-base font-bold text-gray-900 transition-colors">
                                                {title}
                                            </h3>
                                            <p className="mt-1.5 line-clamp-1 text-sm text-gray-500">
                                                {body}
                                            </p>
                                        </div>
                                        <div className="flex shrink-0 items-center gap-4">
                                            {renderStatusBadge(item.status)}
                                            <ChevronRight className="group-hover:text-primary hidden h-5 w-5 text-gray-300 transition-colors md:block" />
                                        </div>
                                    </div>
                                </div>
                            );
                        })}

                        {/* Pagination / Load More */}
                        {aspirations.length >= 3 && (
                            <div className="pt-4 text-center">
                                <button className="rounded-lg border border-gray-300 px-6 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50">
                                    Muat Lebih Banyak
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
