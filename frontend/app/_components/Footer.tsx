import Link from "next/link";
import Vokara from "@/public/vokara.png";
import Image from "next/image";

export default function Footer() {
    return (
        <footer className="w-full border-t border-gray-200 bg-white py-6">
            <div className="container mx-auto flex flex-col items-center justify-between px-4 md:flex-row md:px-8">
                {/* Bagian Kiri: Brand & Copyright */}
                <div className="flex h-auto items-center gap-4 text-sm text-gray-600">
                    <Image
                        src={Vokara}
                        alt="Vokara"
                        width={2068}
                        height={899}
                        className="w-20"
                    />
                    <span>
                        &copy; {new Date().getFullYear()}. Layanan Aspirasi
                        Terintegrasi Pemerintah Republik Indonesia.
                    </span>
                </div>

                {/* Bagian Kanan: Links */}
                <div className="mt-4 flex gap-6 text-sm text-gray-600 md:mt-0">
                    <Link
                        href="/kebijakan-privasi"
                        className="hover:text-muted-foreground transition-colors"
                    >
                        Kebijakan Privasi
                    </Link>
                    <Link
                        href="/keamanan-data"
                        className="hover:text-muted-foreground transition-colors"
                    >
                        Keamanan Data
                    </Link>
                    <Link
                        href="/kontak"
                        className="hover:text-muted-foreground transition-colors"
                    >
                        Kontak Portal
                    </Link>
                </div>
            </div>
        </footer>
    );
}
