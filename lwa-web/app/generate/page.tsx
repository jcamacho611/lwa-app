import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Forge Clips",
  description:
    "Paste a source or upload a file to generate ranked clips with hooks, captions, previews, and post-order signals.",
  path: "/generate",
  keywords: ["generate clips", "clip generator", "hooks captions timestamps", "ranked clip outputs"],
});

export default function GeneratePage() {
  return <ClipStudio initialSection="generate" />;
}
