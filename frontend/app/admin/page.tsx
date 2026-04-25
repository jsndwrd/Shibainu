"use client";

import { getBriefTitle } from "@/lib/brief";
import { useAdminStore } from "@/store/useAdminStore";
import {
  AlertCircle,
  BarChart3,
  Brain,
  FileText,
  Loader2,
  RefreshCcw,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";

function shortId(value?: string | null, length = 8): string {
  if (!value) return "N/A";
  return value.slice(0, length);
}

function safeDate(value?: string | null): string {
  if (!value) return "Tanggal tidak tersedia";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Tanggal tidak tersedia";
  }

  return date.toLocaleDateString("id-ID");
}

export default function AdminOverviewPage() {
  const {
    stats,
    aspirations,
    clusters,
    topScores,
    briefs,
    error,
    isLoading,
    isRecomputing,
    fetchAdminDashboard,
    recomputeClusters,
    recomputeScores,
  } = useAdminStore();

  useEffect(() => {
    fetchAdminDashboard().catch(() => {
      // error sudah masuk ke store
    });
  }, [fetchAdminDashboard]);

  const handleRecompute = async () => {
    await recomputeClusters();
    await recomputeScores();
    await fetchAdminDashboard();
  };

  return (
    <div className="mx-auto max-w-7xl space-y-8 pb-20">
      <div className="flex items-start justify-between gap-6">
        <div>
          <p className="text-primary text-sm font-medium">Overview</p>
          <h1 className="mt-1 text-3xl font-bold text-gray-900">
            Dashboard Admin Vokara
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-gray-500">
            Pantau aspirasi publik, cluster isu, skor prioritas, dan policy
            brief dari data backend secara langsung.
          </p>
        </div>
        {/* 
        <button
          onClick={handleRecompute}
          disabled={isRecomputing || isLoading}
          className="flex items-center gap-2 rounded-lg bg-gray-900 px-5 py-3 text-sm font-medium text-white hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isRecomputing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCcw className="h-4 w-4" />
          )}
          Recompute Data
        </button> */}
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Aspirasi"
          value={stats.totalAspirations}
          icon={FileText}
          caption="Laporan publik masuk"
        />

        <StatCard
          title="Cluster Isu"
          value={stats.totalClusters}
          icon={Brain}
          caption="Kelompok isu terdeteksi"
        />

        {/* <StatCard
          title="Aspirasi Kritis"
          value={stats.criticalReports}
          icon={ShieldAlert}
          caption="Urgensi tinggi dan kritis"
        /> */}

        <StatCard
          title="Policy Brief"
          value={stats.totalBriefs}
          icon={BarChart3}
          caption="Brief kebijakan dibuat"
        />
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          Memuat data dashboard...
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm xl:col-span-2">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-gray-900">
                Cluster Prioritas
              </h2>
              <p className="text-sm text-gray-500">
                Cluster dengan skor prioritas tertinggi.
              </p>
            </div>

            <Link
              href="/admin/wilayah"
              className="text-primary text-sm font-medium hover:underline"
            >
              Lihat wilayah
            </Link>
          </div>

          <div className="space-y-3">
            {clusters.slice(0, 5).map((cluster) => (
              <div
                key={cluster.id}
                className="flex items-center justify-between rounded-lg border border-gray-100 p-4"
              >
                <div>
                  <p className="font-semibold text-gray-900">{cluster.label}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    {cluster.category} · {cluster.member_count} laporan ·{" "}
                    {cluster.top_provinces?.join(", ") || "Tidak ada wilayah"}
                  </p>
                </div>

                <div className="text-right">
                  <p className="text-primary text-sm font-bold">
                    {Number(cluster.priority_score || 0).toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-400">Priority</p>
                </div>
              </div>
            ))}

            {clusters.length === 0 && !isLoading && (
              <EmptyState text="Belum ada data cluster." />
            )}
          </div>
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <h2 className="text-lg font-bold text-gray-900">Top Scores</h2>
            <p className="text-sm text-gray-500">Skor prioritas terbaru.</p>
          </div>

          <div className="space-y-3">
            {topScores.slice(0, 6).map((score) => (
              <div
                key={score.cluster_id}
                className="rounded-lg border border-gray-100 p-4"
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-gray-900">
                    Cluster {shortId(score.cluster_id)}
                  </p>
                  <TrendingUp className="text-primary h-4 w-4" />
                </div>

                <p className="mt-2 text-2xl font-bold text-gray-900">
                  {Number(score.total_score || 0).toFixed(2)}
                </p>

                <p className="mt-1 text-xs text-gray-500">
                  Volume {score.volume_score} · Urgency {score.urgency_score}
                </p>
              </div>
            ))}

            {topScores.length === 0 && !isLoading && (
              <EmptyState text="Belum ada data score." />
            )}
          </div>
        </section>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-gray-900">
                Aspirasi Terbaru
              </h2>
              <p className="text-sm text-gray-500">
                Laporan publik yang baru masuk.
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {aspirations.slice(0, 6).map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between rounded-lg border border-gray-100 p-4"
              >
                <div>
                  <p className="font-semibold text-gray-900">{item.category}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    Cluster {shortId(item.cluster_id)} ·{" "}
                    {safeDate(item.submitted_at)}
                  </p>
                </div>

                <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-bold text-red-600">
                  Urgency {item.urgency}
                </span>
              </div>
            ))}

            {aspirations.length === 0 && !isLoading && (
              <EmptyState text="Belum ada aspirasi masuk." />
            )}
          </div>
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Policy Brief</h2>
              <p className="text-sm text-gray-500">
                Brief yang sudah dibuat oleh sistem.
              </p>
            </div>

            <Link
              href="/admin/laporan"
              className="text-primary text-sm font-medium hover:underline"
            >
              Lihat laporan
            </Link>
          </div>

          <div className="space-y-3">
            {briefs.slice(0, 6).map((brief) => (
              <Link
                key={brief.id}
                href={`/admin/laporan/${brief.id}`}
                className="block rounded-lg border border-gray-100 p-4 transition-colors hover:bg-gray-50"
              >
                <p className="font-semibold text-gray-900">
                  Brief Cluster {getBriefTitle(brief.content)}
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  {brief.urgency_classification} ·{" "}
                  {new Date(brief.generated_at).toLocaleDateString("id-ID")}
                </p>
              </Link>
            ))}

            {briefs.length === 0 && !isLoading && (
              <EmptyState text="Belum ada policy brief." />
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

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

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-dashed border-gray-200 p-6 text-center text-sm text-gray-400">
      {text}
    </div>
  );
}
