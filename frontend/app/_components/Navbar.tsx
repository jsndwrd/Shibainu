import Image from "next/image";
import Link from "next/link";
import GreenLogo from "@/public/green-nobg.png";
import Fingerprint from "@/public/fingerprint.svg";

type NavbarItem = { item: string; link: string };

const NavbarItems: NavbarItem[] = [
    { item: "Beranda", link: "/" },
    { item: "Laporan", link: "/laporan" },
    { item: "Statistik", link: "/stats" },
    { item: "Peta Aspirasi", link: "/peta" },
];

const Navbar = () => {
    return (
        <nav className="flex items-center justify-between border-b bg-white px-10 py-4">
            {/* Left: Logo & Nav Links */}
            <div className="flex items-center gap-8">
                <Link className="flex items-center gap-2" href="/">
                    <Image
                        src={GreenLogo}
                        alt="Logo"
                        width={908}
                        height={899}
                        className="w-9"
                    />
                    <span className="text-primary text-xl font-bold">NAWA</span>
                </Link>

                <ul className="flex gap-6">
                    {NavbarItems.map((nav) => (
                        <li key={nav.link}>
                            <Link
                                href={nav.link}
                                className={`hover:text-primary text-sm font-medium transition-colors ${
                                    nav.item === "Beranda"
                                        ? "text-primary border-primary border-b-2"
                                        : "text-muted-foreground"
                                }`}
                            >
                                {nav.item}
                            </Link>
                        </li>
                    ))}
                </ul>
            </div>

            {/* Right: Action Buttons */}
            <div className="flex items-center gap-3">
                <button className="border-primary text-primary hover:bg-primary/5 flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium hover:cursor-pointer">
                    <Image
                        src={Fingerprint}
                        alt="Fingerprint"
                        width={19}
                        height={20}
                    />
                    <span>Login NIK</span>
                </button>
                <button className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2 text-sm font-medium hover:cursor-pointer">
                    Lapor Sekarang
                </button>
            </div>
        </nav>
    );
};

export default Navbar;
