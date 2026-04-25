import type { Metadata } from "next";
import { Geist, Geist_Mono, Figtree } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import Navbar from "./_components/Navbar";
import Footer from "./_components/Footer";
import Providers from "./_components/Providers";
import NextTopLoader from "nextjs-toploader";

const figtree = Figtree({ subsets: ["latin"], variable: "--font-sans" });

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Vokara",
  description:
    "Indonesian Aspiration System for Policy Intelligence and Responsive Engagement",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={cn(
        "h-full",
        "antialiased",
        geistSans.variable,
        geistMono.variable,
        "font-sans",
        figtree.variable,
        "bg-background",
      )}
    >
      <body className="flex min-h-full flex-col">
        <NextTopLoader color="#2D3F08" showSpinner={false} />
        <Providers>
          <Navbar />
          {children}
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
