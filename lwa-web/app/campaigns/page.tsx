import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Campaigns",
  description: "Move clip packs into assignments and operator-ready delivery.",
  path: "/campaigns",
  keywords: ["clipping campaigns", "campaign workflow", "creator assignments", "operator clip workflow"],
});

export default function CampaignsPage() {
  return <ClipStudio initialSection="campaigns" />;
}
