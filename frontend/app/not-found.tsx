import Link from "next/link";

export default function NotFound() {
    return (
        <div className="flex h-screen w-full flex-col items-center justify-center gap-6 bg-white text-center">
            <div className="space-y-2">
                <h1 className="text-foreground text-4xl font-bold tracking-tight">
                    404
                </h1>
                <p className="text-muted-foreground text-lg">
                    Oops! Halaman yang dikunjung belum ada.
                </p>
            </div>

            <Link
                href="/"
                className="bg-primary text-primary-foreground hover:bg-primary/90 focus-visible:ring-ring inline-flex h-10 items-center justify-center rounded-md px-6 py-2 text-sm font-medium shadow transition-colors focus-visible:ring-1 focus-visible:outline-none"
            >
                Kembali ke Beranda
            </Link>
        </div>
    );
}
