"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Map,
    FileBarChart,
    Settings,
    HelpCircle,
    FileText,
    Search,
    Calendar,
    Bell,
} from "lucide-react";

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();

    const menuItems = [
        { name: "Overview", icon: LayoutDashboard, href: "/admin" },
        { name: "Wilayah", icon: Map, href: "/admin/wilayah" },
        {
            name: "Laporan Analitik",
            icon: FileBarChart,
            href: "/admin/laporan",
        },
    ];

    return (
        <div className="flex h-screen overflow-hidden bg-gray-50">
            {/* Sidebar */}
            <aside className="flex w-64 shrink-0 flex-col justify-between border-r border-gray-200 bg-white">
                <div>
                    <div className="flex h-16 items-center border-b border-gray-100 px-6">
                        <h1 className="text-xl font-bold text-gray-900">
                            <span className="text-primary">Dashboard</span>
                        </h1>
                    </div>
                    <nav className="space-y-1 p-4">
                        {menuItems.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                                        isActive
                                            ? "bg-primary/10 text-primary"
                                            : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                    }`}
                                >
                                    <item.icon className="h-5 w-5" />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>
                </div>

                <div className="space-y-2 border-t border-gray-100 p-4">
                    <button className="bg-primary hover:bg-primary/90 flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-medium text-white transition-colors">
                        <FileText className="h-4 w-4" />
                        Buat Brief Kebijakan
                    </button>
                    <button className="flex w-full items-center gap-3 px-4 py-2 text-sm text-gray-600 hover:text-gray-900">
                        <Settings className="h-4 w-4" /> Pengaturan
                    </button>
                    <button className="flex w-full items-center gap-3 px-4 py-2 text-sm text-gray-600 hover:text-gray-900">
                        <HelpCircle className="h-4 w-4" /> Bantuan
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex min-w-0 flex-1 flex-col">
                {/* Header */}
                <header className="flex h-16 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-8">
                    <h2 className="text-sm font-bold tracking-wide text-gray-800 uppercase"></h2>

                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            <Calendar className="h-4 w-4" /> Q4 2024 Analysis
                            Period
                        </div>
                        <div className="relative">
                            <Search className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Cari isu atau wilayah..."
                                className="focus:ring-primary rounded-lg border-none bg-gray-100 py-2 pr-4 pl-9 text-sm outline-none focus:ring-2"
                            />
                        </div>
                        <button className="relative p-2 text-gray-400 hover:text-gray-600">
                            <Bell className="h-5 w-5" />
                            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500"></span>
                        </button>
                        <div className="bg-primary border-primary/20 h-8 w-8 overflow-hidden rounded-full border-2">
                            {/* Avatar placeholder */}
                        </div>
                    </div>
                </header>

                {/* Scrollable Content */}
                <main className="flex-1 overflow-y-auto p-8">{children}</main>
            </div>
        </div>
    );
}
