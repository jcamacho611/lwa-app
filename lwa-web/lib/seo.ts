import type { Metadata } from "next";

const DEFAULT_SITE_URL = "https://lwa-the-god-app-production.up.railway.app";

export const siteUrl = (process.env.NEXT_PUBLIC_SITE_URL || process.env.NEXT_PUBLIC_APP_URL || DEFAULT_SITE_URL).replace(/\/$/, "");

export function absoluteUrl(path = "/") {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${siteUrl}${normalized}`;
}

export function buildTitle(title: string) {
  return `${title} | LWA`;
}

export function buildDescription(description: string) {
  return description.length > 155 ? `${description.slice(0, 152).trimEnd()}...` : description;
}

export function comparisonDescription(a: string, b: string) {
  return `Compare ${a} vs ${b} for clipping speed, structured outputs, hooks, captions, timestamps, packaging, and creator workflow fit.`;
}

export function buildPageMetadata({
  title,
  description,
  path,
  keywords = [],
}: {
  title: string;
  description: string;
  path: string;
  keywords?: string[];
}): Metadata {
  const normalizedDescription = buildDescription(description);
  const url = absoluteUrl(path);

  return {
    title,
    description: normalizedDescription,
    keywords,
    alternates: {
      canonical: url,
    },
    openGraph: {
      title: buildTitle(title),
      description: normalizedDescription,
      url,
      siteName: "LWA",
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: buildTitle(title),
      description: normalizedDescription,
    },
  };
}

export function softwareJsonLd({
  name,
  url,
  description,
}: {
  name: string;
  url: string;
  description: string;
}) {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name,
    url,
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web, iOS",
    description,
  };
}

export function breadcrumbJsonLd(items: Array<{ name: string; url: string }>) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}
