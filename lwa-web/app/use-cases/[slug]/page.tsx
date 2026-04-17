import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SearchLandingPage } from "../../../components/search/SearchLandingPage";
import { getUseCasePage, useCasePages } from "../../../lib/search-pages";
import { absoluteUrl, breadcrumbJsonLd, buildPageMetadata, softwareJsonLd } from "../../../lib/seo";

export function generateStaticParams() {
  return useCasePages.map((page) => ({ slug: page.slug }));
}

export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const page = getUseCasePage(params.slug);
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

export default function UseCasePage({ params }: { params: { slug: string } }) {
  const page = getUseCasePage(params.slug);

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
      { name: "Use Cases", url: absoluteUrl("/use-cases/podcast-clipping") },
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
