import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClipForge",
  description: "Long videos to high-quality vertical clips",
};

const nav = [
  { href: "/", label: "Dashboard" },
  { href: "/studio", label: "Studio" },
  { href: "/clips", label: "Clips" },
  { href: "/discover", label: "Discover" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <header className="border-b border-white/10 px-8 py-4">
            <nav className="mx-auto flex max-w-6xl items-center gap-8">
              <Link href="/" className="text-xl font-bold tracking-tight">
                Clip<span className="text-violet-400">Forge</span>
              </Link>
              {nav.map((item) => (
                <Link key={item.href} href={item.href} className="text-sm text-zinc-400 hover:text-white">
                  {item.label}
                </Link>
              ))}
            </nav>
          </header>
          <main className="mx-auto max-w-6xl px-8 py-10">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
