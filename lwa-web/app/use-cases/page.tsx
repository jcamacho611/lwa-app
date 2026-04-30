import type { Metadata } from "next";
import { SearchHubPage } from "../../components/search/SearchHubPage";
import { useCasePages } from "../../lib/search-pages";
import { absoluteUrl, breadcrumbJsonLd, buildPageMetadata, softwareJsonLd } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "AI Clipping Use Cases",
  description: "Open creator, podcast, and clipping-operator use cases that map directly to the live LWA workflow.",
  path: "/use-cases",
  keywords: [
    "podcast clip generator",
    "creator repurposing tool",
    "whop clipping workflow",
    "ai clipping use cases",
  ],
});

export default function UseCasesHubPage() {
  const jsonLd = [
    softwareJsonLd({
      name: "LWA",
      url: absoluteUrl("/use-cases"),
      description: "Use-case pages for creators, podcasters, and clipping operators using LWA.",
    }),
    breadcrumbJsonLd([
      { name: "LWA", url: absoluteUrl("/") },
      { name: "Use Cases", url: absoluteUrl("/use-cases") },
    ]),
  ];

  return (
    <SearchHubPage
      kicker="Use Cases"
      title="Show the workflow by audience, not with generic SEO sludge."
      description="These pages map LWA to real creator, podcast, and clipping-operator workflows so search traffic lands on something that still feels like the product."
      pages={useCasePages}
      jsonLd={<script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />}
    />
  );
}
