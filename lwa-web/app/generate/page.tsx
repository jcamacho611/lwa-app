import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Generate Clips",
  description: "Paste a source or upload a file to generate clips worth posting.",
  path: "/generate",
  keywords: ["generate clips", "clip generator", "hooks captions timestamps", "viral-ready clips"],
});

export default function GeneratePage() {
  return <ClipStudio initialSection="generate" />;
}
