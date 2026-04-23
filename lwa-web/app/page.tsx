import type { Metadata } from "next";
import { Logo } from "../components/brand/Logo";
import { buildPageMetadata } from "../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "AI Clipping Engine",
  description: "Turn one source into viral-ready clips with hooks, previews, and post order.",
  path: "/",
  keywords: ["ai clipping engine", "viral-ready clips", "short form repurposing", "creator workflow"],
});

const proofPoints = [
  "Best clip first",
  "Hooks, thumbnail text, CTA",
  "Export-ready packaging",
];

export default function HomePage() {
  return (
    <section className="px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-3xl flex-col items-center justify-center text-center">
        <Logo animated />

        <h1 className="mt-10 text-4xl font-semibold leading-tight text-ink sm:text-6xl">
          Viral-ready clips. One source in.
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-8 text-subtext sm:text-lg">
          Paste a link. LWA picks the best moments.
        </p>

        <form action="/generate" method="get" className="mt-10 w-full space-y-4">
          <input
            type="text"
            inputMode="url"
            autoCapitalize="off"
            autoCorrect="off"
            spellCheck={false}
            name="url"
            placeholder="Paste a YouTube or TikTok URL..."
            className="source-command-input input-surface input-command w-full rounded-[28px] px-5 py-5 text-base"
            aria-label="Source URL"
          />
          <button type="submit" className="primary-button w-full rounded-full px-6 py-4 text-base font-semibold">
            Generate clips
          </button>
        </form>
      </div>

      <section className="mx-auto mt-16 grid w-full max-w-5xl gap-4 pb-16 md:grid-cols-3">
        {proofPoints.map((item) => (
          <div
            key={item}
            className="rounded-[24px] border border-[var(--gold-border)] bg-black/30 px-5 py-5 text-sm font-medium text-ink/84 backdrop-blur-sm"
          >
            {item}
          </div>
        ))}
      </section>
    </section>
  );
}
