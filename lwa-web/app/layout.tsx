import type { Metadata } from "next";
import { headers } from "next/headers";
import { Inter, Zen_Kaku_Gothic_New } from "next/font/google";
import { resolveDirection, resolveLocale } from "../lib/intl";
import { siteUrl } from "../lib/seo";
import "./globals.css";

const bodyFont = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const displayFont = Zen_Kaku_Gothic_New({
  subsets: ["latin"],
  weight: ["700"],
  variable: "--font-display",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "LWA — AI Clipping Engine",
    template: "%s | LWA",
  },
  description: "Turn one long-form source into a ranked clip stack with hooks, captions, timestamps, packaging, and short-form outputs built to move faster.",
  keywords: [
    "ai clipping engine",
    "opus clip alternative",
    "capcut alternative",
    "podcast clip generator",
    "short form repurposing",
    "hooks captions timestamps",
    "ranked clip stack",
  ],
  openGraph: {
    title: "LWA — AI Clipping Engine",
    description: "Turn one long-form source into a ranked clip stack with hooks, captions, timestamps, packaging, and short-form outputs built to move faster.",
    url: siteUrl,
    siteName: "LWA",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "LWA — AI Clipping Engine",
    description: "Turn one long-form source into a ranked clip stack with hooks, captions, timestamps, packaging, and short-form outputs built to move faster.",
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const requestHeaders = await headers();
  const locale = resolveLocale(requestHeaders.get("accept-language"));
  const direction = resolveDirection(locale);

  return (
    <html lang={locale} dir={direction} className="dark" suppressHydrationWarning>
      <body className={`${bodyFont.variable} ${displayFont.variable} bg-bgDark text-white antialiased`}>{children}</body>
    </html>
  );
}
