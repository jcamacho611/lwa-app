import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Archive",
  description:
    "Reopen saved clip packs, compare ranked outputs, and keep playback, packaging, and review continuity intact.",
  path: "/history",
  keywords: ["clip archive", "saved clip packs", "history workflow", "ranked clip history"],
});

export default function HistoryPage() {
  return <ClipStudio initialSection="history" />;
}
