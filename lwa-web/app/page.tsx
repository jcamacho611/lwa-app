import type { Metadata } from "next";
import Link from "next/link";
import { Logo } from "../components/brand/Logo";
import { buildPageMetadata } from "../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "AI Clipping Engine",
  description: "Turn one source into viral-ready clips with hooks, previews, and post order.",
  path: "/",
  keywords: ["ai clipping engine", "viral-ready clips", "short form repurposing", "creator workflow"],
});

export default function HomePage() {
  return (
    <main className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-3xl flex-col items-center justify-center text-center">
        <Logo showTagline animated />

        <section className="mt-12 w-full rounded-[34px] border border-[var(--gold-border)] bg-black/55 p-6 shadow-[0_24px_80px_rgba(0,0,0,0.45)] backdrop-blur-xl sm:p-8">
          <p className="section-kicker">LWA</p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight text-ink sm:text-6xl">
            Viral-ready clips. One source in.
          </h1>

          <form action="/generate" method="get" className="mt-8 space-y-4">
            <input
              type="url"
              name="url"
              placeholder="Paste a YouTube or TikTok URL..."
              className="source-command-input input-surface input-command w-full rounded-[28px] px-5 py-5 text-base"
              aria-label="Source URL"
            />
            <button type="submit" className="primary-button w-full rounded-full px-6 py-4 text-base font-semibold">
              Generate clips
            </button>
          </form>

          <div className="mt-5 flex justify-center">
            <Link href="/generate" className="text-sm font-medium text-[var(--gold)] hover:text-[var(--gold)]/85">
              Open generator
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
