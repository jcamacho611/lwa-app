import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Missions",
  description:
    "Move ranked clip packs into campaign workflows, assignments, and operator-ready delivery without leaving the workspace.",
  path: "/campaigns",
  keywords: ["clipping campaigns", "campaign workflow", "creator assignments", "operator clip workflow"],
});

export default function CampaignsPage() {
  return <ClipStudio initialSection="campaigns" />;
}
