import type { Metadata } from "next";
import Link from "next/link";
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
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/generate" className="primary-button rounded-full px-5 py-3 text-sm font-semibold">Generate clips</Link>
            <Link href="/operator" className="secondary-button rounded-full px-5 py-3 text-sm font-medium">Operator center</Link>
          </div>
        </div>

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
