import Link from "next/link";

import { LwaShell } from "../../components/worlds/LwaShell";

export default function WorldsPage() {
  return (
    <LwaShell title="The Signal Realms">
      <section className="hero-card p-6">
        <p className="kicker">RPG Identity Layer</p>
        <h2 className="mt-3 max-w-3xl text-3xl font-semibold tracking-tight md:text-4xl">
          Every creator action becomes progress.
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/62">
          The Signal Realms turns clipping, campaigns, UGC, referrals, and approved work into
          classes, factions, XP, badges, relics, and reputation.
        </p>

        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/worlds/profile" className="primary-button px-5 py-3 text-sm">
            Open profile
          </Link>
          <Link href="/worlds/quests" className="secondary-button px-5 py-3 text-sm">
            View quests
          </Link>
        </div>
      </section>
    </LwaShell>
  );
}
