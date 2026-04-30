import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Batch Queue",
  description: "Group multiple sources into repeatable batch runs and track processing state.",
  path: "/batches",
  keywords: ["batch clipping", "multi-source queue", "creator batch workflow", "clip batch"],
});

export default function BatchesPage() {
  return <ClipStudio initialSection="batches" />;
}
