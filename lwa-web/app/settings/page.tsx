import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Settings",
  description: "Review plan, credits, feature gates, and workspace controls.",
  path: "/settings",
  keywords: ["plan limits", "creator workspace settings", "premium feature gates", "credits visibility"],
});

export default function SettingsPage() {
  return <ClipStudio initialSection="settings" />;
}
