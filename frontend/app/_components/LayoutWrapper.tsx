"use client";

import { usePathname } from "next/navigation";
import Navbar from "./Navbar";
import Footer from "./Footer";

export default function LayoutWrapper({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();

    // Mengecek apakah URL saat ini dimulai dengan "/admin"
    const isAdminRoute = pathname?.startsWith("/admin");

    return (
        <>
            {/* Hanya render Navbar jika BUKAN di halaman admin */}
            {!isAdminRoute && <Navbar />}

            {/* Render konten halaman (children) */}
            {children}

            {/* Hanya render Footer jika BUKAN di halaman admin */}
            {!isAdminRoute && <Footer />}
        </>
    );
}
