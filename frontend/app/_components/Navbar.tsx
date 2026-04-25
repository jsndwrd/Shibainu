"use client";

import { useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { LogOut, UserCircle } from "lucide-react";

import GreenLogo from "@/public/green-nobg.png";
import Fingerprint from "@/public/fingerprint.svg";

import { useAuthStore } from "@/store/useAuthStore";

type NavbarItem = {
  item: string;
  link: string;
};

const NavbarItems: NavbarItem[] = [
  {
    item: "Beranda",
    link: "/",
  },
  {
    item: "Laporan",
    link: "/laporan",
  },
  {
    item: "Statistik",
    link: "/stats",
  },
  {
    item: "Peta Aspirasi",
    link: "/peta",
  },
];

const Navbar = () => {
  const pathname = usePathname();

  const router = useRouter();

  const { user, isAuthenticated, hydrateAuth, logout, isLoading } =
    useAuthStore();

  useEffect(() => {
    hydrateAuth();
  }, [hydrateAuth]);

  const handleLogout = async () => {
    await logout();

    router.push("/");
  };

  return (
    <nav className="flex items-center justify-between border-b bg-white px-10 py-4">
      {/* LEFT */}
      <div className="flex items-center gap-8">
        <Link href="/" className="flex items-center gap-2">
          <Image
            src={GreenLogo}
            alt="Logo"
            width={908}
            height={899}
            className="w-9"
          />
        </Link>

        <ul className="flex gap-6">
          {NavbarItems.map((nav) => {
            const isActive =
              nav.link === "/"
                ? pathname === "/"
                : pathname.startsWith(nav.link);

            return (
              <li key={nav.link}>
                <Link
                  href={nav.link}
                  className={`hover:text-primary pb-1 text-sm font-medium transition-colors ${
                    isActive
                      ? "text-primary border-primary border-b-2"
                      : "text-muted-foreground"
                  }`}
                >
                  {nav.item}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      {/* RIGHT */}
      <div className="flex items-center gap-3">
        {isAuthenticated ? (
          <>
            <div className="flex items-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700">
              <UserCircle className="text-primary h-5 w-5" />

              <span>
                {user?.nik
                  ? `NIK: ${user.nik.slice(0, 4)}********${user.nik.slice(-4)}`
                  : "Warga"}
              </span>
            </div>

            <button
              onClick={handleLogout}
              disabled={isLoading}
              className="flex items-center gap-2 rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-60"
            >
              <LogOut className="h-4 w-4" />
              {isLoading ? "Keluar..." : "Keluar"}
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className="border-primary text-primary hover:bg-primary/5 flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition-colors"
            >
              <Image
                src={Fingerprint}
                alt="Fingerprint"
                width={19}
                height={20}
              />

              <span>Login NIK</span>
            </Link>

            <Link
              href="/laporan"
              className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2 text-sm font-medium transition-colors"
            >
              Lapor Sekarang
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
