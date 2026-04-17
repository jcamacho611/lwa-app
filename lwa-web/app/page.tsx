import type { Metadata } from "next";
import { ClipStudio } from "../components/clip-studio";
import { buildPageMetadata } from "../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "AI Clipping Engine",
  description:
    "Turn one long-form source into a ranked clip stack with hooks, captions, timestamps, packaging, and short-form-ready output.",
  path: "/",
  keywords: ["ai clipping engine", "ranked clip stack", "short form repurposing", "creator workflow"],
});

export default function HomePage() {
  return <ClipStudio initialSection="home" />;
}
