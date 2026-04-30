import type { Metadata } from "next";
import { SearchHubPage } from "../../components/search/SearchHubPage";
import { comparisonPages } from "../../lib/search-pages";
import { absoluteUrl, breadcrumbJsonLd, buildPageMetadata, softwareJsonLd } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Compare AI Clipping Tools",
  description: "Compare LWA against Opus Clip, CapCut, and related clipping workflows without leaving the live product layer.",
  path: "/compare",
  keywords: [
    "ai clipping tool comparison",
    "opus clip alternative",
    "capcut alternative for clipping",
    "best ai clipping tool",
  ],
});

export default function CompareHubPage() {
  const jsonLd = [
    softwareJsonLd({
      name: "LWA",
      url: absoluteUrl("/compare"),
      description: "Comparison pages for LWA and the current AI clipping tool landscape.",
    }),
    breadcrumbJsonLd([
      { name: "LWA", url: absoluteUrl("/") },
      { name: "Compare", url: absoluteUrl("/compare") },
    ]),
  ];

  return (
    <SearchHubPage
      kicker="Compare"
      title="Open the clipping comparisons without cluttering the product."
      description="These pages help high-intent traffic understand where LWA wins on ranked output, packaging, and operator flow before they move into the generator."
      pages={comparisonPages}
      jsonLd={<script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />}
    />
  );
}
