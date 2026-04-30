import type { Metadata } from "next";
import Link from "next/link";
import { LWA_AGENT_MODEL_FOUNDATION_NOTE, getAllLwaAgents } from "../../lib/lwa-agents";
import { COUNCIL_BRAND_LINE } from "../../lib/production-council";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Signal Realms",
  description: "The future LWA creator progression layer: classes, factions, quests, badges, and cosmetic relics.",
  path: "/realm",
  keywords: ["Signal Realms", "creator progression", "LWA RPG", "creator quests"],
});

const classes = ["Hookwright", "Captioneer", "Reframer", "Trendseer", "Loremaster", "Voicewright", "Ironforger", "Pricer", "Auditor", "Diplomat", "Cartographer", "Oracle"];
const factions = ["Crimson Court", "Black Loom", "Verdant Pact", "Iron Choir", "Saffron Wake", "Glass Synod", "Tide Marshal", "Driftborn", "Emberkin", "Chorus of Thoth", "House Polis", "Outer Signal"];
const principles = ["XP cannot be bought", "Badges are earned", "Relics are cosmetic only", "No investment language", "No feature unlocks from NFTs", "Web-first before chain"];

const agents = getAllLwaAgents();
const formatSlot = (slot: string) => slot.replace(/([A-Z])/g, " $1").toLowerCase();

export default function RealmPage() {
  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <section className="mx-auto max-w-7xl">
        <div className="rounded-[36px] border border-white/12 bg-[radial-gradient(circle_at_top_left,rgba(185,28,28,0.22),transparent_32%),linear-gradient(180deg,var(--bg-card),var(--bg))] p-6 shadow-card sm:p-8">
          <p className="section-kicker">Future retention layer</p>
          <h1 className="mt-5 text-4xl font-semibold leading-tight text-ink sm:text-6xl">The Signal Realms</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-ink/66">
            Signal Realms is the future creator identity system for LWA. This page is a static shell: no XP purchases, no blockchain requirement, no marketplace money movement, and no feature unlocks from relics.
          </p>
          <p className="mt-4 text-sm font-semibold text-ink/50">{COUNCIL_BRAND_LINE}</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/generate" className="primary-button rounded-full px-5 py-3 text-sm font-semibold">Generate clips</Link>
            <Link href="/operator" className="secondary-button rounded-full px-5 py-3 text-sm font-medium">Operator center</Link>
          </div>
        </div>

        <section className="mt-6">
          <div className="mb-4">
            <p className="section-kicker">AI guides</p>
            <h2 className="mt-2 text-2xl font-semibold text-ink">The Seven Agents</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-ink/58">
              Each agent is an in-world AI guide assigned to a product area. They advise, flag, and assist — they do not publish, deploy, or act without human review.
            </p>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-ink/66">
              {LWA_AGENT_MODEL_FOUNDATION_NOTE}
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {agents.map((agent) => (
              <article
                key={agent.id}
                className="rounded-[28px] border border-white/12 bg-[radial-gradient(circle_at_top_left,rgba(109,92,255,0.10),transparent_40%),linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent-wine)]">{agent.productArea}</p>
                    <h3 className="mt-2 text-lg font-semibold text-ink">{agent.name}</h3>
                    <p className="mt-0.5 text-xs text-ink/52">{agent.title}</p>
                  </div>
                  <span className="rounded-full border border-white/10 bg-white/[0.05] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-ink/50">
                    Review required
                  </span>
                </div>
                <p className="mt-4 text-sm italic leading-6 text-ink/70">&ldquo;{agent.tagline}&rdquo;</p>
                <p className="mt-3 text-sm leading-6 text-ink/55">{agent.aiRole}</p>
                {agent.customizable && agent.customizationSlots?.length ? (
                  <div className="mt-4 rounded-[18px] border border-white/10 bg-black/15 p-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full border border-[var(--gold)]/25 bg-[var(--gold)]/10 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--gold)]">
                        Base model
                      </span>
                      <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/58">
                        Future editor
                      </span>
                    </div>
                    <p className="mt-3 text-xs leading-5 text-ink/58">
                      Planned identity slots. These do not activate a live avatar editor, paid game economy, wallet, or NFT system.
                    </p>
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {agent.customizationSlots.map((slot) => (
                        <span key={slot} className="rounded-full border border-white/10 bg-white/[0.035] px-2 py-1 text-[10px] font-medium text-ink/62">
                          {formatSlot(slot)}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}
              </article>
            ))}
          </div>
        </section>

        <section className="mt-6 grid gap-4 lg:grid-cols-2">
          <article className="rounded-[30px] border border-white/12 bg-white/[0.04] p-6">
            <h2 className="text-xl font-semibold text-ink">Classes</h2>
            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              {classes.map((item) => <div key={item} className="rounded-[18px] border border-white/10 bg-black/10 px-3 py-2 text-sm text-ink/72">{item}</div>)}
            </div>
          </article>
          <article className="rounded-[30px] border border-white/12 bg-white/[0.04] p-6">
            <h2 className="text-xl font-semibold text-ink">Factions</h2>
            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              {factions.map((item) => <div key={item} className="rounded-[18px] border border-white/10 bg-black/10 px-3 py-2 text-sm text-ink/72">{item}</div>)}
            </div>
          </article>
        </section>

        <section className="mt-6 rounded-[30px] border border-white/12 bg-white/[0.04] p-6">
          <h2 className="text-xl font-semibold text-ink">Rules of the realm</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {principles.map((item) => <div key={item} className="rounded-[18px] border border-white/10 bg-black/10 p-4 text-sm text-ink/70">{item}</div>)}
          </div>
        </section>
      </section>
    </main>
  );
}
