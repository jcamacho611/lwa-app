import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Studio Settings",
  description:
    "Review plan, credits, feature gates, and workflow depth from the same premium creator workspace.",
  path: "/settings",
  keywords: ["plan limits", "creator workspace settings", "premium feature gates", "credits visibility"],
});

export default function SettingsPage() {
  return <ClipStudio initialSection="settings" />;
}
