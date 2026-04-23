import type { Metadata } from "next";
import { RoutePlaceholder } from "../../components/RoutePlaceholder";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Campaigns",
  description: "Move clip packs into assignments and operator-ready delivery.",
  path: "/campaigns",
  keywords: ["clipping campaigns", "campaign workflow", "creator assignments", "operator clip workflow"],
});

export default function CampaignsPage() {
  return <RoutePlaceholder title="Campaigns" />;
}
