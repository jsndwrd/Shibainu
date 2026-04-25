"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";

interface AdminGuardProps {
  children: React.ReactNode;
}

export default function AdminGuard({ children }: AdminGuardProps) {
  const router = useRouter();

  const { hydrateAuth, fetchMe, isAuthenticated, isAdmin, isLoading } =
    useAuthStore();

  useEffect(() => {
    hydrateAuth();

    fetchMe().catch(() => {
      router.replace("/login");
    });
  }, [hydrateAuth, fetchMe, router]);

  useEffect(() => {
    if (!isLoading && isAuthenticated && !isAdmin) {
      router.replace("/laporan");
    }
  }, [isLoading, isAuthenticated, isAdmin, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 text-sm text-gray-500">
        Memuat akses admin...
      </div>
    );
  }

  if (!isAuthenticated || !isAdmin) {
    return null;
  }

  return <>{children}</>;
}
