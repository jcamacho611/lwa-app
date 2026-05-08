import type { Metadata } from "next";
import { headers } from "next/headers";
import { Poppins } from "next/font/google";
import Script from "next/script";
import { BackgroundCanvas } from "../components/BackgroundCanvas";
import { CharacterStage } from "../components/CharacterStage";
import { FreeLaunchBanner } from "../components/FreeLaunchBanner";
import { resolveDirection, resolveLocale } from "../lib/intl";
import { siteUrl } from "../lib/seo";
import "./globals.css";

const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY || "";
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://app.posthog.com";

const poppinsBody = Poppins({
  subsets: ["latin"],
  weight: ["300", "400"],
  variable: "--font-poppins-body",
  display: "swap",
});

const poppinsDisplay = Poppins({
  subsets: ["latin"],
  weight: ["700"],
  variable: "--font-poppins-display",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "LWA — AI Clipping Engine",
    template: "%s | LWA",
  },
  description: "Turn one source into ranked clip packages with hooks, previews, post order, and export-ready packaging.",
  keywords: [
    "ai clipping engine",
    "opus clip alternative",
    "capcut alternative",
    "podcast clip generator",
    "short form repurposing",
    "hooks captions timestamps",
    "ranked clip packages",
  ],
  openGraph: {
    title: "LWA — AI Clipping Engine",
    description: "Turn one source into ranked clip packages with hooks, previews, post order, and export-ready packaging.",
    url: siteUrl,
    siteName: "LWA",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "LWA — AI Clipping Engine",
    description: "Turn one source into ranked clip packages with hooks, previews, post order, and export-ready packaging.",
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
    <html lang={locale} dir={direction} suppressHydrationWarning>
      <body className={`${poppinsBody.variable} ${poppinsDisplay.variable} antialiased`}>
        {POSTHOG_KEY && (
          <Script id="posthog-init" strategy="afterInteractive">{`
            !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]);t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys onSessionId".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
            posthog.init('${POSTHOG_KEY}',{api_host:'${POSTHOG_HOST}',capture_pageview:true,capture_pageleave:true});
          `}</Script>
        )}
        <FreeLaunchBanner />
        <BackgroundCanvas />
        <CharacterStage />
        <main className="lwa-ui-layer" style={{ position: "relative", zIndex: 10 }}>
          {children}
        </main>
      </body>
    </html>
  );
}
