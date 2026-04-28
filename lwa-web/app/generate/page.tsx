import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Generate Clips",
  description: "Paste a source URL to generate clips worth posting.",
  path: "/generate",
  keywords: ["generate clips", "clip generator", "hooks captions timestamps", "ranked clip packages"],
});

type GeneratePageProps = {
  searchParams?: {
    url?: string | string[];
  };
};

export default function GeneratePage({ searchParams }: GeneratePageProps) {
  const queryUrl = Array.isArray(searchParams?.url) ? searchParams?.url[0] : searchParams?.url;

  return <ClipStudio initialSection="generate" initialUrl={queryUrl || ""} />;
}
