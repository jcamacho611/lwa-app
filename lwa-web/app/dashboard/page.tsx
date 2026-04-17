import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Control Room",
  description:
    "Run the creator workspace from one place: ranked clip packs, queue state, uploads, campaigns, and wallet visibility.",
  path: "/dashboard",
  keywords: ["creator control room", "clip workflow", "operator dashboard", "content repurposing workspace"],
});

export default function DashboardPage() {
  return <ClipStudio initialSection="dashboard" />;
}
