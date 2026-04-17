import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SearchLandingPage } from "../../../components/search/SearchLandingPage";
import { comparisonPages, getComparisonPage } from "../../../lib/search-pages";
import { absoluteUrl, breadcrumbJsonLd, buildPageMetadata, softwareJsonLd } from "../../../lib/seo";

export function generateStaticParams() {
  return comparisonPages.map((page) => ({ slug: page.slug }));
}

export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const page = getComparisonPage(params.slug);
  if (!page) {
    return {};
  }

  return buildPageMetadata({
    title: page.metaTitle,
    description: page.metaDescription,
    path: page.path,
    keywords: page.keywords,
  });
}

export default function ComparisonPage({ params }: { params: { slug: string } }) {
  const page = getComparisonPage(params.slug);

  if (!page) {
    notFound();
  }

  const jsonLd = [
    softwareJsonLd({
      name: "LWA",
      url: absoluteUrl(page.path),
      description: page.metaDescription,
    }),
    breadcrumbJsonLd([
      { name: "LWA", url: absoluteUrl("/") },
      { name: "Compare", url: absoluteUrl("/compare/opus-clip-alternative") },
      { name: page.metaTitle, url: absoluteUrl(page.path) },
    ]),
  ];

  return (
    <SearchLandingPage
      page={page}
      jsonLd={
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      }
    />
  );
}
