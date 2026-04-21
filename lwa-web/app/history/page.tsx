import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Archive",
  description: "Reopen saved clip packs and keep review continuity intact.",
  path: "/history",
  keywords: ["clip archive", "saved clip packs", "history workflow", "clip history"],
});

export default function HistoryPage() {
  return <ClipStudio initialSection="history" />;
}
