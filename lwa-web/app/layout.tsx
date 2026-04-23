import type { Metadata } from "next";
import { headers } from "next/headers";
import { BackgroundCanvas } from "../components/BackgroundCanvas";
import { CharacterStage } from "../components/CharacterStage";
import { resolveDirection, resolveLocale } from "../lib/intl";
import { siteUrl } from "../lib/seo";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "LWA — AI Clipping Engine",
    template: "%s | LWA",
  },
  description: "Turn one source into viral-ready clips with hooks, previews, post order, and export-ready packaging.",
  keywords: [
    "ai clipping engine",
    "opus clip alternative",
    "capcut alternative",
    "podcast clip generator",
    "short form repurposing",
    "hooks captions timestamps",
    "viral-ready clips",
  ],
  openGraph: {
    title: "LWA — AI Clipping Engine",
    description: "Turn one source into viral-ready clips with hooks, previews, post order, and export-ready packaging.",
    url: siteUrl,
    siteName: "LWA",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "LWA — AI Clipping Engine",
    description: "Turn one source into viral-ready clips with hooks, previews, post order, and export-ready packaging.",
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
      <body className="bg-bgDark text-white antialiased">
        <BackgroundCanvas />
        <CharacterStage />
        <main className="lwa-ui-layer" style={{ position: "relative", zIndex: 10 }}>
          {children}
        </main>
      </body>
    </html>
  );
}
