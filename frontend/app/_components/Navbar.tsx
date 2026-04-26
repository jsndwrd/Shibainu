"use client";

import { useEffect, useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { LogOut, UserCircle, Menu, X } from "lucide-react";

import GreenLogo from "@/public/green-nobg.png";
import Fingerprint from "@/public/fingerprint.svg";

import { useAuthStore } from "@/store/useAuthStore";

type NavbarItem = {
    item: string;
    link: string;
};

const baseNavbarItems: NavbarItem[] = [
<<<<<<< HEAD
    { item: "Beranda", link: "/" },
    { item: "Laporan", link: "/laporan" },
=======
  { item: "Beranda", link: "/" },
  { item: "Laporan", link: "/laporan" },
>>>>>>> main
];

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;

  return (
    localStorage.getItem("access_token") ||
    localStorage.getItem("token") ||
    null
  );
}

const Navbar = () => {
    const pathname = usePathname();
    const router = useRouter();

    const [mobileOpen, setMobileOpen] = useState(false);

<<<<<<< HEAD
    const { user, isAuthenticated, isAdmin, hydrateAuth, logout, isLoading } =
        useAuthStore();

    useEffect(() => {
        hydrateAuth();
    }, [hydrateAuth]);

    const navItems: NavbarItem[] = baseNavbarItems.map((nav) => {
        if (isAuthenticated && isAdmin && nav.item === "Laporan") {
            return {
                item: "Dashboard",
                link: "/admin",
            };
        }

        return nav;
    });
=======
  const {
    user,
    role,
    isAuthenticated,
    isAdmin,
    hydrateAuth,
    fetchMe,
    logout,
    isLoading,
  } = useAuthStore();

  useEffect(() => {
    hydrateAuth();

    const token = getStoredToken();

    if (token) {
      fetchMe().catch(() => {});
    }
  }, [hydrateAuth, fetchMe]);

  useEffect(() => {
    if (isAuthenticated && isAdmin && pathname.startsWith("/laporan")) {
      router.replace("/admin");
    }
  }, [isAuthenticated, isAdmin, pathname, router]);

  const navItems = useMemo(() => {
    return baseNavbarItems.map((nav) => {
      if (isAuthenticated && isAdmin && nav.item === "Laporan") {
        return {
          item: "Dashboard",
          link: "/admin",
        };
      }

      return nav;
    });
  }, [isAuthenticated, isAdmin]);

  const profileHref = isAdmin ? "/admin" : "/profile";

  const displayName = user?.nik
    ? `NIK: ${user.nik.slice(0, 4)}********${user.nik.slice(-4)}`
    : isAdmin || role === "admin"
      ? "Admin"
      : "Warga";
>>>>>>> main

    const handleLogout = async () => {
        await logout();
        setMobileOpen(false);
        router.push("/");
    };

    const closeMobile = () => setMobileOpen(false);

<<<<<<< HEAD
    return (
        <nav className="sticky top-0 z-50 border-b bg-white">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-10">
                {/* LEFT */}
                <div className="flex items-center gap-8">
                    <Link
                        href="/"
                        className="flex items-center gap-2"
                        onClick={closeMobile}
                    >
                        <Image
                            src={GreenLogo}
                            alt="Logo"
                            width={908}
                            height={899}
                            className="w-9"
                        />
                    </Link>

                    {/* Desktop Menu */}
                    <ul className="hidden md:flex md:gap-6">
                        {navItems.map((nav) => {
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
                                                ? "border-primary text-primary border-b-2"
                                                : "text-gray-600"
                                        }`}
                                    >
                                        {nav.item}
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>
                </div>

                {/* RIGHT DESKTOP */}
                <div className="hidden items-center gap-3 md:flex">
                    {isAuthenticated ? (
                        <>
                            <Link
                                className="flex items-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700"
                                href="/profile"
                            >
                                <UserCircle className="text-primary h-5 w-5" />
=======
  return (
    <nav className="sticky top-0 z-50 border-b bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-10">
        <div className="flex items-center gap-8">
          <Link
            href="/"
            className="flex items-center gap-2"
            onClick={closeMobile}
          >
            <Image
              src={GreenLogo}
              alt="Logo"
              width={908}
              height={899}
              className="w-9"
              priority
            />
          </Link>

          <ul className="hidden md:flex md:gap-6">
            {navItems.map((nav) => {
              const isActive =
                nav.link === "/"
                  ? pathname === "/"
                  : pathname.startsWith(nav.link);

              return (
                <li key={nav.link}>
                  <Link
                    href={nav.link}
                    className={`pb-1 text-sm font-medium transition-colors hover:text-green-700 ${
                      isActive
                        ? "border-b-2 border-green-700 text-green-700"
                        : "text-gray-600"
                    }`}
                  >
                    {nav.item}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="hidden items-center gap-3 md:flex">
          {isAuthenticated ? (
            <>
              <Link
                href={profileHref}
                className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition ${
                  pathname.startsWith(profileHref)
                    ? "bg-green-50 text-green-700"
                    : "bg-gray-100 text-gray-700 hover:bg-green-50 hover:text-green-700"
                }`}
              >
                <UserCircle className="h-5 w-5 text-green-700" />
                <span>{displayName}</span>
              </Link>

              <button
                onClick={handleLogout}
                disabled={isLoading}
                className="flex items-center gap-2 rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 transition hover:bg-gray-50 disabled:opacity-60"
              >
                <LogOut className="h-4 w-4" />
                {isLoading ? "Keluar..." : "Keluar"}
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="flex items-center gap-2 rounded-md border border-green-700 px-4 py-2 text-sm font-medium text-green-700 transition hover:bg-green-50"
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
                className="rounded-md bg-green-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-800"
              >
                Lapor Sekarang
              </Link>
            </>
          )}
        </div>

        <button
          onClick={() => setMobileOpen((current) => !current)}
          className="rounded-md p-2 text-gray-700 md:hidden"
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {mobileOpen && (
        <div className="border-t bg-white px-4 py-4 md:hidden">
          <div className="space-y-3">
            {navItems.map((nav) => {
              const isActive =
                nav.link === "/"
                  ? pathname === "/"
                  : pathname.startsWith(nav.link);

              return (
                <Link
                  key={nav.link}
                  href={nav.link}
                  onClick={closeMobile}
                  className={`block rounded-md px-3 py-2 text-sm font-medium ${
                    isActive
                      ? "bg-green-50 text-green-700"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  {nav.item}
                </Link>
              );
            })}

            {isAuthenticated && !isAdmin && (
              <Link
                href="/profile"
                onClick={closeMobile}
                className={`block rounded-md px-3 py-2 text-sm font-medium ${
                  pathname.startsWith("/profile")
                    ? "bg-green-50 text-green-700"
                    : "text-gray-700 hover:bg-gray-50"
                }`}
              >
                Profil Saya
              </Link>
            )}
          </div>

          <div className="mt-5 border-t pt-4">
            {isAuthenticated ? (
              <div className="space-y-3">
                <Link
                  href={profileHref}
                  onClick={closeMobile}
                  className="flex items-center gap-2 rounded-md bg-gray-100 px-3 py-3 text-sm text-gray-700"
                >
                  <UserCircle className="h-5 w-5 text-green-700" />
                  <span>{displayName}</span>
                </Link>

                <button
                  onClick={handleLogout}
                  disabled={isLoading}
                  className="flex w-full items-center justify-center gap-2 rounded-md border border-gray-300 px-4 py-3 text-sm font-medium text-gray-700 disabled:opacity-60"
                >
                  <LogOut className="h-4 w-4" />
                  {isLoading ? "Keluar..." : "Keluar"}
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <Link
                  href="/login"
                  onClick={closeMobile}
                  className="flex w-full items-center justify-center gap-2 rounded-md border border-green-700 px-4 py-3 text-sm font-medium text-green-700"
                >
                  <Image
                    src={Fingerprint}
                    alt="Fingerprint"
                    width={18}
                    height={18}
                  />
                  Login NIK
                </Link>
>>>>>>> main

                                <span>
                                    {user?.nik
                                        ? `NIK: ${user.nik.slice(0, 4)}********${user.nik.slice(-4)}`
                                        : isAdmin
                                          ? "Admin"
                                          : "Warga"}
                                </span>
                            </Link>

                            <button
                                onClick={handleLogout}
                                disabled={isLoading}
                                className="flex items-center gap-2 rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-600 transition hover:bg-gray-50 disabled:opacity-60"
                            >
                                <LogOut className="h-4 w-4" />
                                {isLoading ? "Keluar..." : "Keluar"}
                            </button>
                        </>
                    ) : (
                        <>
                            <Link
                                href="/login"
                                className="border-primary text-primary flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition hover:bg-green-50"
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
                                className="hover:bg-primary/90 bg-primary rounded-md px-4 py-2 text-sm font-medium text-white transition"
                            >
                                Lapor Sekarang
                            </Link>
                        </>
                    )}
                </div>

                {/* MOBILE BUTTON */}
                <button
                    onClick={() => setMobileOpen(!mobileOpen)}
                    className="rounded-md p-2 text-gray-700 md:hidden"
                >
                    {mobileOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* MOBILE MENU */}
            {mobileOpen && (
                <div className="border-t bg-white px-4 py-4 md:hidden">
                    <div className="space-y-3">
                        {navItems.map((nav) => {
                            const isActive =
                                nav.link === "/"
                                    ? pathname === "/"
                                    : pathname.startsWith(nav.link);

                            return (
                                <Link
                                    key={nav.link}
                                    href={nav.link}
                                    onClick={closeMobile}
                                    className={`block rounded-md px-3 py-2 text-sm font-medium ${
                                        isActive
                                            ? "text-primary bg-green-50"
                                            : "text-gray-700 hover:bg-gray-50"
                                    }`}
                                >
                                    {nav.item}
                                </Link>
                            );
                        })}
                    </div>

                    <div className="mt-5 border-t pt-4">
                        {isAuthenticated ? (
                            <Link
                                className="space-y-3 hover:cursor-pointer"
                                href="/profile"
                            >
                                <div className="rounded-md bg-gray-100 px-3 py-3 text-sm text-gray-700">
                                    {user?.nik
                                        ? `NIK: ${user.nik.slice(0, 4)}********${user.nik.slice(-4)}`
                                        : isAdmin
                                          ? "Admin"
                                          : "Warga"}
                                </div>

                                <button
                                    onClick={handleLogout}
                                    disabled={isLoading}
                                    className="flex w-full items-center justify-center gap-2 rounded-md border border-gray-300 px-4 py-3 text-sm font-medium text-gray-700"
                                >
                                    <LogOut className="h-4 w-4" />
                                    {isLoading ? "Keluar..." : "Keluar"}
                                </button>
                            </Link>
                        ) : (
                            <div className="space-y-3">
                                <Link
                                    href="/login"
                                    onClick={closeMobile}
                                    className="border-primary text-primary flex w-full items-center justify-center gap-2 rounded-md border px-4 py-3 text-sm font-medium"
                                >
                                    <Image
                                        src={Fingerprint}
                                        alt="Fingerprint"
                                        width={18}
                                        height={18}
                                    />
                                    Login NIK
                                </Link>

                                <Link
                                    href="/laporan"
                                    onClick={closeMobile}
                                    className="bg-primary block rounded-md px-4 py-3 text-center text-sm font-medium text-white"
                                >
                                    Lapor Sekarang
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
