"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
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
    Brain,
    AlertCircle,
    Loader2,
} from "lucide-react";

import { useAuthStore } from "@/store/useAuthStore";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import type { AspirationListItem } from "@/lib/apiContract";

function getStoredToken(): string | null {
    if (typeof window === "undefined") return null;

    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token") ||
        null
    );
}

function formatDate(dateString?: string | null): string {
    if (!dateString) return "-";

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) return "-";

    return new Intl.DateTimeFormat("id-ID", {
        day: "numeric",
        month: "short",
        year: "numeric",
    }).format(date);
}

function shortId(value?: string | null): string {
    if (!value) return "N/A";
    return value.split("-")[0].toUpperCase();
}

function getCategory(item: AspirationListItem): string {
    return item.category_user_input || item.predicted_category || "Umum";
}

function parseAspirationContent(item: AspirationListItem) {
    const description = item.description?.trim();

    if (!description) {
        const category = getCategory(item);
        return {
            title: `Aspirasi ${category}`,
            body: `Laporan kategori ${category}.`,
        };
    }

    const parts = description.split("\n\n");
    const title = parts[0]?.trim() || "Aspirasi Tanpa Judul";
    const body = parts.slice(1).join("\n\n").trim() || title;

    return { title, body };
}

function normalizeStatus(status?: string | null) {
    const value = status?.toLowerCase();

    if (!value) return "submitted";

    if (["processed", "selesai", "resolved", "done"].includes(value)) {
        return "resolved";
    }

    if (["in_progress", "diproses", "in_review", "review"].includes(value)) {
        return "in_review";
    }

    if (["rejected", "ditolak"].includes(value)) {
        return "rejected";
    }

    return "submitted";
}

function renderStatusBadge(status?: string | null) {
    const normalizedStatus = normalizeStatus(status);

    if (normalizedStatus === "resolved") {
        return (
            <span className="flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Selesai
            </span>
        );
    }

    if (normalizedStatus === "in_review") {
        return (
            <span className="flex items-center gap-1.5 rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">
                <Activity className="h-3.5 w-3.5" />
                Dalam Proses
            </span>
        );
    }

    if (normalizedStatus === "rejected") {
        return (
            <span className="flex items-center gap-1.5 rounded-full bg-red-50 px-3 py-1 text-xs font-bold text-red-700">
                <XCircle className="h-3.5 w-3.5" />
                Ditolak
            </span>
        );
    }

    return (
        <span className="flex items-center gap-1.5 rounded-full bg-orange-50 px-3 py-1 text-xs font-bold text-orange-700">
            <Clock className="h-3.5 w-3.5" />
            Menunggu Review
        </span>
    );
}

export default function ProfilePage() {
    const router = useRouter();
    const [isPageLoading, setIsPageLoading] = useState(true);

    const {
        user,
        isAdmin,
        hydrateAuth,
        fetchMe,
        isLoading: isAuthLoading,
    } = useAuthStore();

    const {
        aspirations,
        fetchMyAspirations,
        isLoading: isAspirasiLoading,
        error: aspirasiError,
    } = useAspirasiStore();

    useEffect(() => {
        let isActive = true;

        const loadData = async () => {
            try {
                hydrateAuth();
                const token = getStoredToken();

                if (!token) {
                    router.replace("/login");
                    return;
                }

                await fetchMe();
                // Opsional: biarkan admin masuk atau lempar ke admin dashboard jika diinginkan
                // if (me.role === "admin") { router.replace("/admin"); return; }

                await fetchMyAspirations();
            } catch {
                router.replace("/login");
            } finally {
                if (isActive) {
                    setIsPageLoading(false);
                }
            }
        };

        loadData();

        return () => {
            isActive = false;
        };
    }, [hydrateAuth, fetchMe, fetchMyAspirations, router]);

    const safeAspirations = useMemo(
        () => (aspirations || []) as AspirationListItem[],
        [aspirations],
    );

    const stats = useMemo(() => {
        return {
            total: safeAspirations.length,
            strategic: safeAspirations.filter(
                (item) => item.policy_level === "strategic",
            ).length,
            operational: safeAspirations.filter(
                (item) => item.policy_level === "operational",
            ).length,
            selesai: safeAspirations.filter(
                (item) => normalizeStatus(item.status) === "resolved",
            ).length,
        };
    }, [safeAspirations]);

    const quotaLimit = 5;
    const usedQuota = Math.min(stats.total, quotaLimit);
    const remainingQuota = Math.max(0, quotaLimit - usedQuota);
    const quotaPercent = Math.min(
        100,
        Math.round((usedQuota / quotaLimit) * 100),
    );

    if (isPageLoading || isAuthLoading) {
        return (
            <div className="mx-auto max-w-7xl space-y-8 px-6 pt-10 pb-20">
                <div className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-500">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Memuat data profil warga...
                </div>
            </div>
        );
    }

    return (
        <div className="mx-auto max-w-7xl space-y-8 px-6 pt-10 pb-20">
            {/* Header Layout Mengikuti AdminOverviewPage */}
            <div className="flex items-start justify-between gap-6">
                <div>
                    <p className="text-primary text-sm font-medium">Profile</p>
                    <h1 className="mt-1 text-3xl font-bold text-gray-900">
                        Dashboard Warga
                    </h1>
                    <p className="mt-2 max-w-2xl text-sm text-gray-500">
                        Pantau profil, sisa kuota aspirasi harian, dan pantau
                        riwayat laporan yang telah Anda kirimkan ke sistem.
                    </p>
                </div>
            </div>

            {/* Profile & Quota Section */}
            <div className="flex flex-col gap-6 md:flex-row">
                {/* Profile Card */}
                <div className="flex flex-1 items-center gap-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                    <div className="bg-primary/10 text-primary flex h-16 w-16 shrink-0 items-center justify-center rounded-lg">
                        <User className="h-8 w-8" />
                    </div>

                    <div className="min-w-0">
                        <h2 className="truncate text-xl font-bold text-gray-900">
                            {user?.nik
                                ? `Warga (${user.nik.slice(0, 6)}***)`
                                : "Warga Terverifikasi"}
                        </h2>
                        <div className="mt-1.5 flex flex-col gap-1 text-sm text-gray-500 sm:flex-row sm:items-center sm:gap-4">
                            <span className="flex items-center gap-1.5">
                                <MapPin className="h-3.5 w-3.5 text-gray-400" />
                                {user?.province
                                    ? `${user.regency || "Kota"}, ${user.province}`
                                    : "DKI Jakarta"}
                            </span>
                            <span className="hidden text-gray-300 sm:block">
                                •
                            </span>
                            <span className="flex items-center gap-1.5">
                                <Calendar className="h-3.5 w-3.5 text-gray-400" />
                                Bergabung{" "}
                                {formatDate(
                                    user?.created_at ||
                                        new Date().toISOString(),
                                )}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Quota Card */}
                <div className="bg-primary relative flex w-full flex-col justify-center overflow-hidden rounded-xl p-6 text-white shadow-sm md:w-80">
                    <div className="absolute -top-10 -right-10 h-32 w-32 rounded-full bg-white/10 blur-2xl" />

                    <div className="relative z-10">
                        <div className="mb-4 flex items-center gap-2 font-medium text-white/90">
                            <FileText className="h-5 w-5" />
                            Kuota Aspirasi
                        </div>

                        <p className="mb-2 text-sm text-white/80">
                            Digunakan {usedQuota} dari {quotaLimit} Laporan
                        </p>

                        <div className="mb-1.5 flex items-center justify-between text-xs font-bold">
                            <span>Sisa {remainingQuota}</span>
                            <span>{quotaPercent}%</span>
                        </div>

                        <div className="h-2 w-full overflow-hidden rounded-full bg-black/20">
                            <div
                                className="h-full rounded-full bg-white transition-all"
                                style={{ width: `${quotaPercent}%` }}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats Row Using the Admin StatCard */}
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
                <StatCard
                    title="Total Laporan"
                    value={stats.total}
                    icon={FileText}
                    caption="Seluruh riwayat aspirasi"
                />
                <StatCard
                    title="Isu Strategis"
                    value={stats.strategic}
                    icon={Brain}
                    caption="Klasifikasi makro"
                />
                <StatCard
                    title="Operasional"
                    value={stats.operational}
                    icon={Activity}
                    caption="Keluhan layanan teknis"
                />
                <StatCard
                    title="Terselesaikan"
                    value={stats.selesai}
                    icon={CheckCircle2}
                    caption="Status laporan selesai"
                />
            </div>

            {/* Aspirations History List */}
            <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">
                            Riwayat Aspirasi
                        </h2>
                        <p className="text-sm text-gray-500">
                            Daftar laporan publik yang pernah Anda kirimkan.
                        </p>
                    </div>

                    <Link
                        href="/laporan"
                        className="bg-primary hover:bg-primary/90 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors"
                    >
                        Buat Laporan
                    </Link>
                </div>

                {aspirasiError && (
                    <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                        {aspirasiError}
                    </div>
                )}

                <div className="space-y-3">
                    {safeAspirations.length === 0 && !isAspirasiLoading ? (
                        <EmptyState text="Belum ada riwayat aspirasi yang dikirimkan." />
                    ) : (
                        safeAspirations.map((item, index) => {
                            const { title } = parseAspirationContent(item);

                            return (
                                <Link
                                    key={item.id || index}
                                    href={`#`} // Arahkan ke detail laporan jika nanti Anda punya pagenya
                                    className="flex items-center justify-between rounded-lg border border-gray-100 p-4 transition-colors hover:bg-gray-50"
                                >
                                    <div className="pr-4">
                                        <p className="line-clamp-1 font-semibold text-gray-900">
                                            {title}
                                        </p>

                                        <p className="mt-1 text-xs text-gray-500">
                                            <span className="font-medium text-gray-700">
                                                {getCategory(item)}
                                            </span>{" "}
                                            · {shortId(item.id)} ·{" "}
                                            {formatDate(
                                                item.submitted_at ||
                                                    item.created_at,
                                            )}
                                        </p>
                                    </div>

                                    <div className="flex shrink-0 items-center gap-4">
                                        {renderStatusBadge(item.status)}
                                        <ChevronRight className="hidden h-4 w-4 text-gray-300 md:block" />
                                    </div>
                                </Link>
                            );
                        })
                    )}

                    {safeAspirations.length >= 5 && (
                        <div className="pt-4 text-center">
                            <button
                                type="button"
                                className="rounded-lg border border-gray-300 px-6 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50"
                            >
                                Muat Lebih Banyak
                            </button>
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
}

// Komponen Identik dari AdminOverviewPage
interface StatCardProps {
    title: string;
    value: number;
    caption: string;
    icon: React.ElementType;
}

function StatCard({ title, value, caption, icon: Icon }: StatCardProps) {
    return (
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between">
                <div className="bg-primary/10 text-primary flex h-11 w-11 items-center justify-center rounded-lg">
                    <Icon className="h-5 w-5" />
                </div>
                <AlertCircle className="h-4 w-4 text-gray-300" />
            </div>

            <p className="text-sm font-medium text-gray-500">{title}</p>
            <h3 className="mt-2 text-3xl font-bold text-gray-900">{value}</h3>
            <p className="mt-1 text-xs text-gray-400">{caption}</p>
        </div>
    );
}

// EmptyState dari AdminOverviewPage
function EmptyState({ text }: { text: string }) {
    return (
        <div className="rounded-lg border border-dashed border-gray-200 p-6 text-center text-sm text-gray-400">
            {text}
        </div>
    );
}
