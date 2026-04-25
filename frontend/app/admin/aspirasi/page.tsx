"use client";

import { useEffect, useState } from "react";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import OperationalView from "./_components/OperationalView";
import StrategicView from "./_components/StrategicView";

type ViewMode = "operasional" | "strategis";

export default function AdminAspirasiPage() {
    const [viewMode, setViewMode] = useState<ViewMode>("operasional");
    const { fetchAspirations } = useAspirasiStore();

    // Ambil data aspirasi saat admin membuka halaman ini
    useEffect(() => {
        fetchAspirations().catch(console.error);
    }, [fetchAspirations]);

    return (
        <div className="mx-auto max-w-7xl space-y-6 pb-20">
            {/* Header & View Toggle */}
            <div className="flex flex-col justify-between gap-4 border-b border-gray-200 pb-6 md:flex-row md:items-end">
                <div>
                    <div className="mb-1 flex items-center gap-2 text-xs font-bold tracking-widest text-gray-400 uppercase">
                        ASPIRASI <span className="text-gray-300">❯</span>{" "}
                        {viewMode}
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900 capitalize md:text-3xl">
                        {viewMode} Aspirations
                    </h1>
                    <p className="mt-1 max-w-xl text-sm text-gray-500">
                        {viewMode === "operasional"
                            ? "Tactical. Immediate issues reported by citizens requiring prompt attention and routing to specific operational units."
                            : "Strategic. High-level policy focus areas aggregated from AI cluster analysis and Asta Cita alignment."}
                    </p>
                </div>

                {/* Switcher Toggle UI */}
                <div className="inline-flex shrink-0 rounded-lg border border-gray-200 bg-gray-100 p-1">
                    <button
                        onClick={() => setViewMode("operasional")}
                        className={`rounded-md px-5 py-2 text-sm font-bold transition-all ${
                            viewMode === "operasional"
                                ? "bg-white text-gray-900 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        Operasional
                    </button>
                    <button
                        onClick={() => setViewMode("strategis")}
                        className={`rounded-md px-5 py-2 text-sm font-bold transition-all ${
                            viewMode === "strategis"
                                ? "bg-white text-gray-900 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        Strategis
                    </button>
                </div>
            </div>

            {/* Conditional Rendering View */}
            <div className="animate-in fade-in slide-in-from-bottom-2 pt-2 duration-300">
                {viewMode === "operasional" ? (
                    <OperationalView />
                ) : (
                    <StrategicView />
                )}
            </div>
        </div>
    );
}
