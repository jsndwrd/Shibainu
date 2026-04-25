"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/useAuthStore";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import { useRouter } from "next/navigation";
import {
    User,
    MapPin,
    CheckCircle2,
    Clock,
    FileText,
    ChevronRight,
    Loader2,
    PieChart,
    MoreHorizontal,
} from "lucide-react";

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

            const token =
                localStorage.getItem("token") ||
                localStorage.getItem("access_token");

            if (!isAuthenticated && !token) {
                router.push("/login");
                return;
            }

            try {
                await Promise.all([
                    fetchMe().catch(() => {}),
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

    // Format Tanggal Helper (Contoh Output: 12 Okt 2024)
    const formatDate = (dateString?: string) => {
        if (!dateString) return "-";
        try {
            return new Intl.DateTimeFormat("id-ID", {
                day: "2-digit",
                month: "short",
                year: "numeric",
            }).format(new Date(dateString));
        } catch {
            return "-";
        }
    };

    // Format Bulan Tahun (Contoh Output: Jan 2023)
    const formatMonthYear = (dateString?: string) => {
        if (!dateString) return "-";
        try {
            return new Intl.DateTimeFormat("id-ID", {
                month: "short",
                year: "numeric",
            }).format(new Date(dateString));
        } catch {
            return "-";
        }
    };

    const parseAspirationContent = (description: string) => {
        if (!description) return { title: "Aspirasi Tanpa Judul", body: "" };
        const parts = description.split("\n\n");
        const title = parts[0] || "Aspirasi Tanpa Judul";
        const body = parts.slice(1).join("\n\n") || title;
        return { title, body };
    };

    const userInfo = user as Record<string, any> | null;

    const stats = {
        total: aspirations.length,
        disetujui: aspirations.filter(
            (a: any) => a.status === "processed" || a.status === "selesai",
        ).length,
        dalamProses: aspirations.filter(
            (a: any) =>
                a.status === "in_progress" ||
                a.status === "diproses" ||
                a.status === "clustered",
        ).length,
        ditolak: aspirations.filter(
            (a: any) => a.status === "rejected" || a.status === "ditolak",
        ).length,
    };

    const renderStatusBadge = (status?: string) => {
        const s = status?.toLowerCase() || "pending";
        if (s === "processed" || s === "selesai") {
            return (
                <span className="bg-muted text-muted-foreground flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-bold">
                    <CheckCircle2 className="h-4 w-4" /> Selesai
                </span>
            );
        }
        if (s === "in_progress" || s === "diproses" || s === "clustered") {
            return (
                <span className="flex items-center gap-1.5 rounded-full bg-gray-200 px-4 py-1.5 text-sm font-bold text-gray-700">
                    <MoreHorizontal className="h-4 w-4" /> Dalam Proses
                </span>
            );
        }
        if (s === "rejected" || s === "ditolak") {
            return (
                <span className="flex items-center gap-1.5 rounded-full bg-red-100 px-4 py-1.5 text-sm font-bold text-red-700">
                    <XCircle className="h-4 w-4" /> Ditolak
                </span>
            );
        }
        return (
            <span className="flex items-center gap-1.5 rounded-full bg-gray-200 px-4 py-1.5 text-sm font-bold text-gray-700">
                <Clock className="h-4 w-4" /> Menunggu Review
            </span>
        );
    };

    if (!isMounted || isPageLoading) {
        return (
            <div className="mx-auto w-full max-w-[1440px] space-y-8 px-6 pt-10 pb-20 md:px-10">
                <div className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-500">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Memuat data profil warga...
                </div>
            </div>
        );
    }

    return (
        <div className="mx-auto w-full max-w-[1440px] space-y-8 px-6 pt-10 pb-20 md:px-10">
            {/* Profile & Quota Row */}
            <div className="flex flex-col gap-6 lg:flex-row">
                {/* Profile Card */}
                <div className="relative flex flex-1 items-center gap-6 overflow-hidden rounded-2xl border border-gray-100 bg-[#FAFAFA] p-8 shadow-sm">
                    {/* Hiasan latar belakang opsional seperti pada gambar */}
                    <div className="absolute top-0 right-0 h-full w-48 bg-[#F3F5ED] opacity-50"></div>

                    <div className="relative z-10 flex h-28 w-28 shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-gray-200 shadow-sm">
                        <User className="h-16 w-16 text-gray-400" />
                    </div>
                    <div className="relative z-10">
                        <h1 className="text-3xl font-bold text-gray-900">
                            {userInfo?.nik
                                ? `Warga (${String(userInfo.nik).slice(0, 6)}***)`
                                : "Budi Santoso"}
                        </h1>
                        <div className="mt-3 flex flex-col gap-2 text-sm text-gray-600">
                            <span className="flex items-center gap-2">
                                <MapPin className="h-4 w-4 text-gray-400" />
                                {userInfo?.province
                                    ? `${userInfo.regency || "Kota"}, ${userInfo.province}`
                                    : "Jakarta Selatan, DKI Jakarta"}
                            </span>
                            <span className="text-gray-500">
                                Bergabung sejak{" "}
                                {formatMonthYear(
                                    userInfo?.created_at || "2023-01-01",
                                )}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Quota Card */}
                <div className="bg-primary relative flex w-full flex-col justify-center overflow-hidden rounded-2xl p-8 text-white shadow-md lg:w-[450px]">
                    <div className="absolute -top-10 -right-10 h-40 w-40 rounded-full bg-white/5 blur-3xl"></div>
                    <div className="relative z-10">
                        <div className="mb-6 flex items-center gap-2 text-xl font-semibold text-white/90">
                            <PieChart className="h-6 w-6" /> Kuota Aspirasi
                        </div>
                        <p className="mb-8 text-sm text-white/80">
                            Aspirasi Kuota: 3/5 Digunakan
                        </p>
                        <div className="mb-2 flex items-center justify-between text-sm font-medium">
                            <span className="text-white/90">Tersisa 2</span>
                            <span className="text-white/90">60%</span>
                        </div>
                        <div className="h-2.5 w-full overflow-hidden rounded-full bg-black/20">
                            <div className="bg-muted h-full w-[60%] rounded-full"></div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4 md:gap-6">
                <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <p className="text-xs font-bold tracking-wider text-gray-600 uppercase">
                        TOTAL LAPORAN
                    </p>
                    <h3 className="mt-4 text-5xl font-bold text-gray-900">
                        {stats.total}
                    </h3>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <p className="text-xs font-bold tracking-wider text-gray-600 uppercase">
                        DISETUJUI
                    </p>
                    <h3 className="text-muted-foreground mt-4 text-5xl font-bold">
                        {stats.disetujui}
                    </h3>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <p className="text-xs font-bold tracking-wider text-gray-600 uppercase">
                        DALAM PROSES
                    </p>
                    <h3 className="mt-4 text-5xl font-bold text-[#7A5A29]">
                        {stats.dalamProses}
                    </h3>
                </div>
                <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <p className="text-xs font-bold tracking-wider text-gray-600 uppercase">
                        DITOLAK
                    </p>
                    <h3 className="mt-4 text-5xl font-bold text-red-600">
                        {stats.ditolak}
                    </h3>
                </div>
            </div>

            {/* Aspirations History */}
            <div>
                <h2 className="mb-6 text-2xl font-bold text-gray-900">
                    Riwayat Aspirasi
                </h2>

                <div className="space-y-4">
                    {aspirations.length === 0 && !isAspirasiLoading ? (
                        <div className="rounded-xl border border-dashed border-gray-200 bg-white p-12 text-center text-sm text-gray-400">
                            <FileText className="mx-auto mb-4 h-10 w-10 text-gray-300" />
                            <p className="mb-6 text-base">
                                Belum ada riwayat aspirasi.
                            </p>
                            <button
                                onClick={() => router.push("/laporan")}
                                className="bg-primary hover:bg-primary/90 inline-block rounded-lg px-6 py-3 font-medium text-white transition-colors"
                            >
                                Buat Laporan Baru
                            </button>
                        </div>
                    ) : (
                        aspirations.map((rawItem) => {
                            const item = rawItem as Record<string, any>;
                            const { title, body } = parseAspirationContent(
                                item.description || "",
                            );

                            return (
                                <div
                                    key={item.id}
                                    className="flex cursor-pointer flex-col justify-between gap-4 rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-colors hover:border-gray-300 hover:shadow-md md:flex-row md:items-center"
                                >
                                    <div className="pr-4">
                                        <div className="mb-3 flex items-center gap-3 text-sm">
                                            <span className="bg-muted text-muted-foreground rounded-md px-2.5 py-1 font-bold">
                                                {item.category_user_input ||
                                                    item.predicted_category ||
                                                    item.category ||
                                                    "Umum"}
                                            </span>
                                            <span className="text-gray-500">
                                                {item.id
                                                    ? `#ASP-${String(item.id)
                                                          .split("-")[0]
                                                          .toUpperCase()}`
                                                    : "#ASP-2024-001"}
                                            </span>
                                            <span className="text-gray-400">
                                                •
                                            </span>
                                            <span className="text-gray-500">
                                                {formatDate(
                                                    item.submitted_at ||
                                                        item.created_at,
                                                )}
                                            </span>
                                        </div>
                                        <h3 className="text-lg font-bold text-gray-900">
                                            {title}
                                        </h3>
                                        <p className="mt-2 line-clamp-1 text-gray-600">
                                            {body}
                                        </p>
                                    </div>
                                    <div className="flex shrink-0 items-center gap-4">
                                        {renderStatusBadge(item.status)}
                                        <ChevronRight className="hidden h-5 w-5 text-gray-400 md:block" />
                                    </div>
                                </div>
                            );
                        })
                    )}

                    {aspirations.length >= 3 && (
                        <div className="pt-6 text-center">
                            <button className="rounded-lg border border-gray-300 bg-white px-8 py-3 text-sm font-medium text-gray-900 transition-colors hover:bg-gray-50">
                                Muat Lebih Banyak
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
