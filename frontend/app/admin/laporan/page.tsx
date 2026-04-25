"use client";

import { useAdminStore } from "@/store/useAdminStore";
import {
  FileBarChart,
  Loader2,
  Plus,
  RefreshCcw,
  Sparkles,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function AdminLaporanPage() {
  const {
    clusters,
    briefs,
    error,
    isLoadingClusters,
    isLoadingBriefs,
    isGeneratingBrief,
    fetchClusters,
    fetchBriefs,
    generateBriefs,
  } = useAdminStore();

  const [selectedClusterIds, setSelectedClusterIds] = useState<string[]>([]);

  useEffect(() => {
    fetchClusters().catch(() => {});
    fetchBriefs().catch(() => {});
  }, [fetchClusters, fetchBriefs]);

  const toggleCluster = (clusterId: string) => {
    setSelectedClusterIds((current) => {
      if (current.includes(clusterId)) {
        return current.filter((id) => id !== clusterId);
      }

      return [...current, clusterId];
    });
  };

  const handleGenerateBrief = async () => {
    if (selectedClusterIds.length === 0) return;

    await generateBriefs({
      cluster_ids: selectedClusterIds,
    });

    setSelectedClusterIds([]);
  };

  const isLoading = isLoadingClusters || isLoadingBriefs;

  return (
    <div className="mx-auto max-w-7xl space-y-8 pb-20">
      <div className="flex items-start justify-between gap-6">
        <div>
          <p className="text-primary text-sm font-medium">Laporan Analitik</p>
          <h1 className="mt-1 text-3xl font-bold text-gray-900">
            Policy Brief Generator
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-gray-500">
            Pilih cluster prioritas, lalu buat policy brief dari data backend.
          </p>
        </div>

        <button
          onClick={() => {
            fetchClusters();
            fetchBriefs();
          }}
          disabled={isLoading}
          className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-70"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCcw className="h-4 w-4" />
          )}
          Muat Ulang
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Pilih Cluster</h2>
            <p className="text-sm text-gray-500">
              Cluster terpilih akan dikirim ke endpoint generate brief.
            </p>
          </div>

          <button
            onClick={handleGenerateBrief}
            disabled={selectedClusterIds.length === 0 || isGeneratingBrief}
            className="bg-primary hover:bg-primary/90 flex items-center gap-2 rounded-lg px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isGeneratingBrief ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Plus className="h-4 w-4" />
            )}
            Generate Brief
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {clusters.map((cluster) => {
            const checked = selectedClusterIds.includes(cluster.id);

            return (
              <button
                key={cluster.id}
                type="button"
                onClick={() => toggleCluster(cluster.id)}
                className={`rounded-xl border p-5 text-left transition-colors ${
                  checked
                    ? "border-primary bg-primary/5"
                    : "border-gray-200 hover:bg-gray-50"
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-bold text-gray-900">{cluster.label}</p>
                    <p className="mt-1 text-xs text-gray-500">
                      {cluster.category}
                    </p>
                  </div>

                  <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-bold text-gray-700">
                    {cluster.member_count}
                  </span>
                </div>

                <p className="mt-4 text-sm text-gray-500">
                  {cluster.top_provinces?.join(", ") || "Tidak ada wilayah"}
                </p>

                <p className="text-primary mt-3 text-sm font-bold">
                  Priority {Number(cluster.priority_score || 0).toFixed(2)}
                </p>
              </button>
            );
          })}
        </div>

        {clusters.length === 0 && !isLoading && (
          <div className="rounded-lg border border-dashed border-gray-200 p-8 text-center text-sm text-gray-400">
            Belum ada cluster.
          </div>
        )}
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-5">
          <h2 className="text-lg font-bold text-gray-900">
            Daftar Policy Brief
          </h2>
          <p className="text-sm text-gray-500">
            Brief yang sudah berhasil dibuat.
          </p>
        </div>

        <div className="space-y-3">
          {briefs.map((brief) => (
            <Link
              key={brief.id}
              href={`/admin/laporan/${brief.id}`}
              className="flex items-center justify-between rounded-xl border border-gray-200 p-5 transition-colors hover:bg-gray-50"
            >
              <div className="flex items-start gap-4">
                <div className="bg-primary/10 text-primary flex h-10 w-10 items-center justify-center rounded-lg">
                  <FileBarChart className="h-5 w-5" />
                </div>

                <div>
                  <p className="font-bold text-gray-900">
                    Brief Cluster {brief.cluster_id.slice(0, 8)}
                  </p>
                  <p className="mt-1 line-clamp-2 text-sm text-gray-500">
                    {brief.content}
                  </p>
                </div>
              </div>

              <div className="text-right">
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
                  <Sparkles className="h-3 w-3" />
                  {brief.urgency_classification}
                </span>

                <p className="mt-2 text-xs text-gray-400">
                  {new Date(brief.generated_at).toLocaleDateString("id-ID")}
                </p>
              </div>
            </Link>
          ))}

          {briefs.length === 0 && !isLoading && (
            <div className="rounded-lg border border-dashed border-gray-200 p-8 text-center text-sm text-gray-400">
              Belum ada policy brief.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
