import type { Metadata } from "next";
import { RoutePlaceholder } from "../../components/RoutePlaceholder";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Control Room",
  description: "Run clip packs, queue state, uploads, campaigns, and wallet visibility from one workspace.",
  path: "/dashboard",
  keywords: ["creator control room", "clip workflow", "operator dashboard", "content repurposing workspace"],
});

export default function DashboardPage() {
  return <RoutePlaceholder title="Dashboard" />;
}
