"use client";

import { useAspirasiStore } from "@/store/useAspirasiStore";
import { Search, Filter, MapPin, ListTree, Activity } from "lucide-react";

// Helper untuk memisahkan judul dan deskripsi (sesuai format payload Anda)
const parseAspirationContent = (description: string) => {
    if (!description) return { title: "Tanpa Judul", body: "" };
    const parts = description.split("\n\n");
    const title = parts[0] || "Tanpa Judul";
    const body = parts.slice(1).join("\n\n") || title;
    return { title, body };
};

// Helper untuk Badge Status
const StatusBadge = ({ status }: { status: string }) => {
    const s = status?.toLowerCase();
    if (s === "processed" || s === "selesai") {
        return (
            <span className="rounded bg-emerald-100 px-2 py-0.5 text-[10px] font-bold tracking-wider text-emerald-800 uppercase">
                ● PROCESSED
            </span>
        );
    }
    if (s === "clustered") {
        return (
            <span className="rounded bg-blue-100 px-2 py-0.5 text-[10px] font-bold tracking-wider text-blue-800 uppercase">
                ● CLUSTERED
            </span>
        );
    }
    return (
        <span className="rounded bg-gray-100 px-2 py-0.5 text-[10px] font-bold tracking-wider text-gray-800 uppercase">
            ● {status || "PENDING"}
        </span>
    );
};

export default function OperationalView() {
    const { aspirations, isLoading } = useAspirasiStore();

    // Hitung statistik sederhana dari data yang ada
    const total = aspirations.length || 1;
    const processedCount = aspirations.filter(
        (a) => a.status === "processed" || a.status === "selesai",
    ).length;
    const clusteredCount = aspirations.filter(
        (a) => a.status === "clustered",
    ).length;

    return (
        <div className="flex flex-col gap-8 lg:flex-row">
            {/* Left Sidebar (Stats & Categories) */}
            <div className="w-full shrink-0 space-y-6 lg:w-1/4">
                {/* Status Overview */}
                <div className="rounded-xl border border-gray-100 bg-gray-50 p-5">
                    <h3 className="mb-4 text-xs font-bold tracking-widest text-gray-500 uppercase">
                        Status Overview
                    </h3>
                    <div className="space-y-4">
                        <div>
                            <div className="mb-1.5 flex justify-between text-sm font-medium text-gray-800">
                                <span>Processed</span>
                                <span>{processedCount}</span>
                            </div>
                            <div className="h-1.5 w-full rounded-full bg-gray-200">
                                <div
                                    className="bg-primary h-1.5 rounded-full"
                                    style={{
                                        width: `${(processedCount / total) * 100}%`,
                                    }}
                                ></div>
                            </div>
                        </div>
                        <div>
                            <div className="mb-1.5 flex justify-between text-sm font-medium text-gray-800">
                                <span>Clustered</span>
                                <span>{clusteredCount}</span>
                            </div>
                            <div className="h-1.5 w-full rounded-full bg-gray-200">
                                <div
                                    className="bg-accent h-1.5 rounded-full"
                                    style={{
                                        width: `${(clusteredCount / total) * 100}%`,
                                    }}
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Top Categories */}
                <div className="rounded-xl border border-gray-100 bg-gray-50 p-5">
                    <h3 className="mb-4 text-xs font-bold tracking-widest text-gray-500 uppercase">
                        Top Categories
                    </h3>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between text-sm text-gray-700">
                            <span className="flex items-center gap-2">
                                <ListTree className="h-4 w-4 text-gray-400" />{" "}
                                Infrastruktur
                            </span>
                            <span className="rounded border border-gray-200 bg-white px-2 py-0.5 text-xs font-medium">
                                42%
                            </span>
                        </div>
                        <div className="flex items-center justify-between text-sm text-gray-700">
                            <span className="flex items-center gap-2">
                                <Activity className="h-4 w-4 text-gray-400" />{" "}
                                Utilitas
                            </span>
                            <span className="rounded border border-gray-200 bg-white px-2 py-0.5 text-xs font-medium">
                                31%
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Main Content (Search & List) */}
            <div className="w-full space-y-4 lg:w-3/4">
                {/* Search Bar */}
                <div className="flex gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Cari deskripsi atau judul..."
                            className="focus:ring-primary/20 w-full rounded-lg border border-gray-200 bg-white py-2.5 pr-4 pl-9 text-sm focus:ring-2 focus:outline-none"
                        />
                    </div>
                    <button className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
                        <Filter className="h-4 w-4" /> Filter
                    </button>
                </div>

                {/* List of Aspirations */}
                <div className="divide-y divide-gray-100 rounded-xl border border-gray-100 bg-white shadow-sm">
                    {isLoading ? (
                        <div className="animate-pulse p-8 text-center text-gray-500">
                            Memuat data operasional...
                        </div>
                    ) : aspirations.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">
                            Belum ada aspirasi operasional.
                        </div>
                    ) : (
                        aspirations.map((item) => {
                            const { title, body } = parseAspirationContent(
                                item.description,
                            );

                            return (
                                <div
                                    key={item.id}
                                    className="flex items-start gap-4 p-5 transition-colors hover:bg-gray-50"
                                >
                                    <div className="mt-1 shrink-0 rounded-lg bg-emerald-50 p-2">
                                        <MapPin className="text-primary h-5 w-5" />
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <div className="mb-1 flex items-start justify-between">
                                            <h4 className="truncate pr-4 text-sm font-bold text-gray-900">
                                                {title}
                                            </h4>
                                            <span className="shrink-0 text-xs text-gray-400">
                                                {new Date(
                                                    item.submitted_at ||
                                                        Date.now(),
                                                ).toLocaleDateString("id-ID", {
                                                    day: "numeric",
                                                    month: "short",
                                                    year: "numeric",
                                                })}
                                            </span>
                                        </div>
                                        <p className="mb-3 line-clamp-2 text-sm leading-relaxed text-gray-500">
                                            {body}
                                        </p>
                                        <div className="flex flex-wrap items-center gap-2">
                                            <span className="rounded border border-gray-200 bg-gray-100 px-2 py-0.5 text-[10px] font-bold tracking-wider text-gray-700 uppercase">
                                                {item.predicted_category ||
                                                    item.category ||
                                                    "UMUM"}
                                            </span>
                                            <StatusBadge status={item.status} />
                                        </div>
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>
            </div>
        </div>
    );
}
