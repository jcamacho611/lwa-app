import type { Metadata } from "next";
import Link from "next/link";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Social Integrations",
  description: "Future LWA social integration status shell for provider readiness, OAuth planning, and distribution workflow visibility.",
  path: "/social",
  keywords: ["LWA social integrations", "creator distribution", "YouTube Shorts", "Instagram Reels", "TikTok"],
});

const providers = [
  { name: "YouTube", status: "readiness shell", detail: "Plan for channel reads, upload review, and Shorts packaging." },
  { name: "TikTok", status: "review later", detail: "Direct posting requires platform approval before live publishing claims." },
  { name: "Instagram", status: "review later", detail: "Creator or business account workflows require provider review and account linking." },
  { name: "Twitch", status: "clip workflow", detail: "Stream and VOD clip workflows stay visible as a creator source lane." },
  { name: "Reddit", status: "trend research", detail: "Future public trend signal only, not spam automation." },
  { name: "Polymarket", status: "read-only trend", detail: "Cultural-attention metadata only. No betting, trading, or recommendations." },
];

const rules = [
  "No fake direct posting",
  "No provider approval claims until reviewed",
  "No social tokens without encrypted storage",
  "No spam automation",
  "Read-only trend data stays clearly labeled",
  "User consent before any future publishing action",
];

export default function SocialPage() {
  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <section className="mx-auto max-w-7xl">
        <div className="rounded-[36px] border border-white/12 bg-[radial-gradient(circle_at_top_left,rgba(49,130,246,0.2),transparent_30%),linear-gradient(180deg,var(--bg-card),var(--bg))] p-6 shadow-card sm:p-8">
          <p className="section-kicker">Future distribution layer</p>
          <h1 className="mt-5 text-4xl font-semibold leading-tight text-ink sm:text-6xl">Social Integration Status</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-ink/66">
            This shell tracks future distribution readiness without pretending direct posting is already approved. LWA remains source-to-package first: generate, review, export, then connect provider workflows only when they are verified.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/generate" className="primary-button rounded-full px-5 py-3 text-sm font-semibold">Generate package</Link>
            <Link href="/operator" className="secondary-button rounded-full px-5 py-3 text-sm font-medium">Operator center</Link>
          </div>
        </div>

        <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {providers.map((provider) => (
            <article key={provider.name} className="rounded-[28px] border border-white/12 bg-white/[0.04] p-5 shadow-card">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-lg font-semibold text-ink">{provider.name}</h2>
                <span className="rounded-full border border-white/12 bg-white/[0.05] px-2.5 py-1 text-[10px] uppercase tracking-[0.16em] text-ink/62">{provider.status}</span>
              </div>
              <p className="mt-3 text-sm leading-6 text-ink/62">{provider.detail}</p>
            </article>
          ))}
        </section>

        <section className="mt-6 rounded-[30px] border border-white/12 bg-white/[0.04] p-6">
          <h2 className="text-xl font-semibold text-ink">Integration rules</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {rules.map((rule) => <div key={rule} className="rounded-[18px] border border-white/10 bg-black/10 p-4 text-sm text-ink/70">{rule}</div>)}
          </div>
        </section>
      </section>
    </main>
  );
}
