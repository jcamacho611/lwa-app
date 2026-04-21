import type { Metadata } from "next";
import { ClipStudio } from "../components/clip-studio";
import { buildPageMetadata } from "../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "AI Clipping Engine",
  description: "Turn one source into viral-ready clips with hooks, previews, and post order.",
  path: "/",
  keywords: ["ai clipping engine", "viral-ready clips", "short form repurposing", "creator workflow"],
});

export default function HomePage() {
  return <ClipStudio initialSection="home" />;
}
