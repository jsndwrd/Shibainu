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
} from "lucide-react";

import { useAuthStore } from "@/store/useAuthStore";
import { useAspirasiStore } from "@/store/useAspirasiStore";

type ProfileAspiration = {
  id?: string | null;
  description?: string | null;

  category_user_input?: string | null;
  predicted_category?: string | null;

  policy_level?: string | null;
  policy_level_confidence?: number | null;
  policy_level_reason?: string | null;
  routing_target?: string | null;

  cluster_id?: string | null;
  priority_score?: number | null;

  status?: string | null;
  submitted_at?: string | null;
};

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

  if (Number.isNaN(date.getTime())) {
    return "-";
  }

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

function getCategory(item: ProfileAspiration): string {
  return item.category_user_input || item.predicted_category || "Umum";
}

function getPolicyLevelLabel(policyLevel?: string | null): string {
  if (policyLevel === "strategic") return "Strategic";
  if (policyLevel === "operational") return "Operational";

  return "Belum diklasifikasikan";
}

function parseAspirationContent(item: ProfileAspiration) {
  const description = item.description?.trim();

  if (!description) {
    const category = getCategory(item);
    const policyLevel = getPolicyLevelLabel(item.policy_level);

    return {
      title: `Aspirasi ${category}`,
      body: `Laporan kategori ${category} dengan klasifikasi ${policyLevel}.`,
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
      <span className="flex items-center gap-1.5 rounded-md bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-700">
        <CheckCircle2 className="h-3.5 w-3.5" />
        Selesai
      </span>
    );
  }

  if (normalizedStatus === "in_review") {
    return (
      <span className="flex items-center gap-1.5 rounded-md bg-gray-100 px-3 py-1 text-xs font-bold text-gray-700">
        <Activity className="h-3.5 w-3.5" />
        Dalam Proses
      </span>
    );
  }

  if (normalizedStatus === "rejected") {
    return (
      <span className="flex items-center gap-1.5 rounded-md bg-red-100 px-3 py-1 text-xs font-bold text-red-700">
        <XCircle className="h-3.5 w-3.5" />
        Ditolak
      </span>
    );
  }

  return (
    <span className="flex items-center gap-1.5 rounded-md bg-orange-100 px-3 py-1 text-xs font-bold text-orange-700">
      <Clock className="h-3.5 w-3.5" />
      Menunggu Review
    </span>
  );
}

export default function ProfilePage() {
  const router = useRouter();

  const [isPageLoading, setIsPageLoading] = useState(true);

  const { user, hydrateAuth, fetchMe } = useAuthStore();

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

        await Promise.allSettled([fetchMe(), fetchMyAspirations()]);
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
    () => (aspirations || []) as ProfileAspiration[],
    [aspirations],
  );

  const stats = useMemo(() => {
    return {
      total: safeAspirations.length,
      disetujui: safeAspirations.filter(
        (item) => normalizeStatus(item.status) === "resolved",
      ).length,
      dalamProses: safeAspirations.filter(
        (item) => normalizeStatus(item.status) === "in_review",
      ).length,
      ditolak: safeAspirations.filter(
        (item) => normalizeStatus(item.status) === "rejected",
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

  const userData = user as {
    nik?: string | null;
    province?: string | null;
    regency?: string | null;
    created_at?: string | null;
  } | null;

  if (isPageLoading) {
    return (
      <div className="mx-auto flex max-w-5xl animate-pulse flex-col gap-6 p-6 md:p-10">
        <div className="flex flex-col gap-6 md:flex-row">
          <div className="h-40 flex-1 rounded-xl bg-gray-200" />
          <div className="h-40 w-full rounded-xl bg-gray-200 md:w-1/3" />
        </div>
        <div className="h-24 w-full rounded-xl bg-gray-200" />
        <div className="h-64 w-full rounded-xl bg-gray-200" />
      </div>
    );
  }

  return (
    <div className="mx-auto min-h-screen max-w-6xl space-y-8 p-4 sm:p-6 md:p-10">
      <div className="flex flex-col gap-6 md:flex-row">
        <div className="flex flex-1 flex-col gap-5 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:flex-row sm:items-center">
          <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-full border-4 border-white bg-gray-100 shadow-sm">
            <User className="h-10 w-10 text-gray-400" />
          </div>

          <div className="min-w-0">
            <h1 className="truncate text-2xl font-bold text-gray-900">
              {userData?.nik
                ? `Warga (${userData.nik.slice(0, 6)}***)`
                : "Warga Terverifikasi"}
            </h1>

            <div className="mt-2 flex flex-col gap-1.5 text-sm text-gray-500">
              <span className="flex items-center gap-2">
                <MapPin className="h-4 w-4 shrink-0 text-gray-400" />
                <span className="truncate">
                  {userData?.regency && userData?.province
                    ? `${userData.regency}, ${userData.province}`
                    : userData?.province || "Lokasi belum tersedia"}
                </span>
              </span>

              <span className="flex items-center gap-2">
                <Calendar className="h-4 w-4 shrink-0 text-gray-400" />
                Bergabung sejak {formatDate(userData?.created_at)}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-primary relative flex w-full flex-col justify-center overflow-hidden rounded-2xl p-6 text-white shadow-md md:w-80">
          <div className="absolute -top-10 -right-10 h-32 w-32 rounded-full bg-white/10 blur-2xl" />

          <div className="relative z-10">
            <div className="mb-4 flex items-center gap-2 font-medium text-white/90">
              <FileText className="h-5 w-5" />
              Kuota Aspirasi
            </div>

            <p className="mb-2 text-sm text-white/80">
              Aspirasi Kuota {usedQuota}/{quotaLimit} Digunakan
            </p>

            <div className="mb-1.5 flex items-center justify-between text-xs font-bold">
              <span>Sisa {remainingQuota}</span>
              <span>{quotaPercent}%</span>
            </div>

            <div className="h-2 w-full overflow-hidden rounded-full bg-black/20">
              <div
                className="bg-accent h-full rounded-full transition-all"
                style={{ width: `${quotaPercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 md:gap-6">
        <StatCard title="Total Laporan" value={stats.total} />
        <StatCard title="Disetujui" value={stats.disetujui} tone="success" />
        <StatCard
          title="Dalam Proses"
          value={stats.dalamProses}
          tone="warning"
        />
        <StatCard title="Ditolak" value={stats.ditolak} tone="danger" />
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              Riwayat Aspirasi
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              Daftar laporan dan aspirasi yang pernah Anda kirim.
            </p>
          </div>

          <Link
            href="/laporan"
            className="bg-primary hover:bg-primary/90 inline-flex items-center justify-center rounded-lg px-5 py-2.5 text-sm font-medium text-white transition-colors"
          >
            Buat Laporan Baru
          </Link>
        </div>

        {aspirasiError && (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {aspirasiError}
          </div>
        )}

        {safeAspirations.length === 0 && !isAspirasiLoading ? (
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
            {safeAspirations.map((item, index) => {
              const { title, body } = parseAspirationContent(item);

              return (
                <div
                  key={item.id || index}
                  className="group rounded-xl border border-gray-100 p-5 transition-all hover:border-emerald-500/30 hover:shadow-md"
                >
                  <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
                    <div className="min-w-0 flex-1">
                      <div className="mb-2 flex flex-wrap items-center gap-3">
                        <span className="bg-accent/20 text-primary rounded px-2.5 py-0.5 text-xs font-bold">
                          {getCategory(item)}
                        </span>

                        <span className="text-xs font-medium text-gray-400">
                          {shortId(item.id)} • {formatDate(item.submitted_at)}
                        </span>
                      </div>

                      <h3 className="group-hover:text-primary text-base font-bold text-gray-900 transition-colors">
                        {title}
                      </h3>

                      <p className="mt-1.5 line-clamp-2 text-sm text-gray-500">
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

            {safeAspirations.length >= 3 && (
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
        )}
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  tone = "default",
}: {
  title: string;
  value: number;
  tone?: "default" | "success" | "warning" | "danger";
}) {
  const toneClass = {
    default: "text-gray-900",
    success: "text-emerald-600",
    warning: "text-orange-500",
    danger: "text-red-600",
  }[tone];

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <p className="mb-1 text-xs font-bold tracking-wider text-gray-400 uppercase">
        {title}
      </p>

      <h3 className={`text-3xl font-bold ${toneClass}`}>{value}</h3>
    </div>
  );
}
