"use client";

import { useEffect, useState } from "react";
import AdminGuard from "../_components/AdminGuard";
import { useAuthStore } from "@/store/useAuthStore";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
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
    LogOut,
    Menu,
    X,
    House,
} from "lucide-react";

type MenuItem = {
    name: string;
    icon: React.ElementType;
    href: string;
};

const menuItems: MenuItem[] = [
    {
        name: "Overview",
        icon: LayoutDashboard,
        href: "/admin",
    },
    {
        name: "Wilayah",
        icon: Map,
        href: "/admin/wilayah",
    },
    {
        name: "Laporan Analitik",
        icon: FileBarChart,
        href: "/admin/laporan",
    },
];

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const router = useRouter();

    const { logout, user, isLoading } = useAuthStore();

    const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

    useEffect(() => {
        setIsMobileSidebarOpen(false);
    }, [pathname]);

    const handleLogout = async () => {
        await logout();
        router.replace("/login");
    };

    return (
        <AdminGuard>
            <div className="h-[calc(100dvh-64px)] overflow-hidden bg-gray-50 lg:h-dvh">
                {/* Mobile overlay */}
                {isMobileSidebarOpen && (
                    <button
                        type="button"
                        aria-label="Close sidebar overlay"
                        onClick={() => setIsMobileSidebarOpen(false)}
                        className="fixed inset-0 z-40 bg-black/40 lg:hidden"
                    />
                )}

                {/* Mobile sidebar */}
                <aside
                    className={`fixed top-0 bottom-0 left-0 z-50 flex w-72 flex-col border-r border-gray-200 bg-white transition-transform duration-300 lg:hidden ${
                        isMobileSidebarOpen
                            ? "translate-x-0"
                            : "-translate-x-full"
                    }`}
                >
                    <SidebarContent
                        pathname={pathname}
                        isLoading={isLoading}
                        onLogout={handleLogout}
                        onClose={() => setIsMobileSidebarOpen(false)}
                        showCloseButton
                    />
                </aside>

                <div className="flex h-full min-h-0">
                    {/* Desktop sidebar */}
                    <aside className="hidden h-full w-64 shrink-0 border-r border-gray-200 bg-white lg:flex lg:flex-col">
                        <SidebarContent
                            pathname={pathname}
                            isLoading={isLoading}
                            onLogout={handleLogout}
                        />
                    </aside>

                    {/* Main shell */}
                    <div className="flex min-w-0 flex-1 flex-col">
                        <header className="flex h-16 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4 sm:px-6 lg:px-8">
                            <div className="flex items-center gap-3">
                                <button
                                    type="button"
                                    onClick={() => setIsMobileSidebarOpen(true)}
                                    className="rounded-lg p-2 text-gray-600 hover:bg-gray-100 lg:hidden"
                                    aria-label="Open sidebar"
                                >
                                    <Menu className="h-5 w-5" />
                                </button>
                            </div>

                            <div className="flex items-center gap-3 sm:gap-5">
                                <div className="hidden items-center gap-2 text-sm text-gray-500 md:flex">
                                    <Calendar className="h-4 w-4" />
                                    Live Analysis Period
                                </div>

                                <div className="relative hidden sm:block">
                                    <Search className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-gray-400" />
                                    <input
                                        type="text"
                                        placeholder="Cari isu atau wilayah..."
                                        className="focus:ring-primary w-48 rounded-lg border-none bg-gray-100 py-2 pr-4 pl-9 text-sm outline-none focus:ring-2 lg:w-64"
                                    />
                                </div>

                                <button className="relative p-2 text-gray-400 hover:text-gray-600">
                                    <Bell className="h-5 w-5" />
                                    <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500" />
                                </button>
                            </div>
                        </header>

                        <main className="min-h-0 flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
                            {children}
                        </main>
                    </div>
                </div>
            </div>
        </AdminGuard>
    );
}

function SidebarContent({
    pathname,
    isLoading,
    onLogout,
    onClose,
    showCloseButton = false,
}: {
    pathname: string;
    isLoading: boolean;
    onLogout: () => void;
    onClose?: () => void;
    showCloseButton?: boolean;
}) {
    return (
        <div className="flex h-full min-h-0 flex-col">
            <div className="flex h-16 shrink-0 items-center justify-between border-b border-gray-100 px-6">
                <h1 className="text-xl font-bold text-gray-900">
                    <span className="text-primary">Vokara</span> Admin
                </h1>

                {showCloseButton && (
                    <button
                        type="button"
                        onClick={onClose}
                        className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 lg:hidden"
                        aria-label="Close sidebar"
                    >
                        <X className="h-5 w-5" />
                    </button>
                )}
            </div>

            <nav className="min-h-0 flex-1 space-y-1 overflow-y-auto p-4">
                {menuItems.map((item) => {
                    const isActive =
                        item.href === "/admin"
                            ? pathname === "/admin"
                            : pathname.startsWith(item.href);

                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            onClick={onClose}
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

            <div className="shrink-0 space-y-2 border-t border-gray-100 p-4">
                <Link
                    href="/admin/laporan"
                    onClick={onClose}
                    className="bg-primary hover:bg-primary/90 flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-medium text-white transition-colors"
                >
                    <FileText className="h-4 w-4" />
                    Buat Brief Kebijakan
                </Link>

                <button className="flex w-full items-center gap-3 rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900">
                    <Settings className="h-4 w-4" />
                    Pengaturan
                </button>

                <button className="flex w-full items-center gap-3 rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900">
                    <HelpCircle className="h-4 w-4" />
                    Bantuan
                </button>

                <Link
                    className="flex w-full items-center gap-3 rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                    href="/"
                >
                    <House className="h-4 w-4" />
                    Home
                </Link>

                <button
                    onClick={onLogout}
                    disabled={isLoading}
                    className="flex w-full items-center gap-3 rounded-lg px-4 py-2 text-sm text-red-600 hover:bg-red-50 hover:text-red-700 disabled:opacity-70"
                >
                    <LogOut className="h-4 w-4" />
                    {isLoading ? "Keluar..." : "Keluar"}
                </button>
            </div>
        </div>
    );
}
