"use client";

import { useAspirasiStore } from "@/store/useAspirasiStore";
import { Download, Search, Target } from "lucide-react";

export default function StrategicView() {
    const { aspirations, isLoading } = useAspirasiStore();

    return (
        <div className="space-y-6">
            {/* Top Insight Cards */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                {/* Left Card: Focus Areas (Takes 2 columns) */}
                <div className="rounded-xl border border-gray-100 bg-gray-50 p-6 md:col-span-2">
                    <h3 className="mb-1 text-sm font-bold text-gray-900">
                        Top Policy Focus Areas
                    </h3>
                    <p className="mb-6 text-xs text-gray-500">
                        Aggregated from recent strategic aspiration responses
                        across all regions.
                    </p>

                    <div className="space-y-5">
                        {[
                            { name: "Pemerataan Pendidikan", percent: 42 },
                            { name: "Reformasi Birokrasi", percent: 28 },
                            { name: "Ketahanan Pangan", percent: 16 },
                        ].map((focus) => (
                            <div key={focus.name}>
                                <div className="mb-1.5 flex justify-between text-xs font-bold text-gray-800">
                                    <span>{focus.name}</span>
                                    <span>{focus.percent}%</span>
                                </div>
                                <div className="h-1.5 w-full rounded-full bg-gray-200">
                                    <div
                                        className="bg-primary h-1.5 rounded-full"
                                        style={{ width: `${focus.percent}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right Card: Asta Cita Alignment */}
                <div className="bg-primary border-primary relative flex flex-col justify-between overflow-hidden rounded-xl border p-6 text-white">
                    <div className="absolute -top-6 -right-6 text-white/10">
                        <Target className="h-32 w-32" />
                    </div>
                    <div className="relative z-10">
                        <h3 className="mb-1 text-sm font-bold text-white/90">
                            Asta Cita Alignment
                        </h3>
                        <p className="text-xs text-white/60">
                            System prediction confidence
                        </p>
                    </div>
                    <div className="relative z-10 mt-6">
                        <div className="flex items-baseline gap-1">
                            <span className="text-5xl font-bold">87</span>
                            <span className="text-xl text-white/80">%</span>
                        </div>
                        <p className="mt-2 text-[10px] text-white/60">
                            Average Asta Cita confidence across mapped strategic
                            responses.
                        </p>
                    </div>
                </div>
            </div>

            {/* Table Section */}
            <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
                <div className="flex items-center justify-between border-b border-gray-100 bg-gray-50/50 p-4">
                    <h3 className="text-sm font-bold text-gray-800">
                        Aspiration Response Records
                    </h3>
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <Search className="absolute top-1/2 left-3 h-3.5 w-3.5 -translate-y-1/2 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search keywords..."
                                className="focus:ring-primary/30 rounded-md border border-gray-200 bg-white py-1.5 pr-3 pl-8 text-xs focus:ring-1 focus:outline-none"
                            />
                        </div>
                        <button className="bg-primary hover:bg-primary/90 flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium text-white transition-colors">
                            <Download className="h-3.5 w-3.5" /> Export Data
                        </button>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="border-b border-gray-100 bg-gray-50 text-xs tracking-wider text-gray-500 uppercase">
                            <tr>
                                <th className="px-6 py-3 font-semibold">ID</th>
                                <th className="px-6 py-3 font-semibold">
                                    Strategic Theme
                                </th>
                                <th className="px-6 py-3 font-semibold">
                                    Key Summary
                                </th>
                                <th className="px-6 py-3 font-semibold">
                                    Predicted Asta Cita
                                </th>
                                <th className="px-6 py-3 text-right font-semibold">
                                    Confidence
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {isLoading ? (
                                <tr>
                                    <td
                                        colSpan={5}
                                        className="animate-pulse px-6 py-8 text-center text-gray-500"
                                    >
                                        Memuat data strategis...
                                    </td>
                                </tr>
                            ) : aspirations.length === 0 ? (
                                <tr>
                                    <td
                                        colSpan={5}
                                        className="px-6 py-8 text-center text-gray-500"
                                    >
                                        Belum ada data strategis.
                                    </td>
                                </tr>
                            ) : (
                                aspirations.map((item) => (
                                    <tr
                                        key={item.id}
                                        className="transition-colors hover:bg-gray-50"
                                    >
                                        <td className="px-6 py-4 font-mono text-xs text-gray-500">
                                            {item.id.slice(0, 8).toUpperCase()}
                                        </td>
                                        <td className="px-6 py-4 font-medium text-gray-900">
                                            {item.predicted_category ||
                                                item.category ||
                                                "General Feedback"}
                                        </td>
                                        <td className="max-w-xs truncate px-6 py-4 text-gray-500">
                                            {item.description.split("\n\n")[0]}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="bg-accent/20 text-primary border-accent/30 rounded border px-2 py-1 text-xs font-semibold">
                                                {item.predicted_asta_cita ||
                                                    "Asta Cita Umum"}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right font-semibold text-emerald-600">
                                            {item.asta_confidence
                                                ? `${Math.round(item.asta_confidence * 100)}%`
                                                : "80%"}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
