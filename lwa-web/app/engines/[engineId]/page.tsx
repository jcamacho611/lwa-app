import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import EngineDeepLinkPanel from "../../../components/engines/EngineDeepLinkPanel";

const KNOWN_ENGINE_IDS = [
  "creator",
  "brain",
  "render",
  "marketplace",
  "wallet_entitlements",
  "proof_history",
  "world_game",
  "safety",
  "social_distribution",
  "operator_admin",
] as const;

type Params = { engineId: string };

export function generateStaticParams(): Params[] {
  return KNOWN_ENGINE_IDS.map((engineId) => ({ engineId }));
}

export function generateMetadata({ params }: { params: Params }): Metadata {
  const engineId = params.engineId;
  return {
    title: `LWA Engine · ${engineId}`,
    description: `Backend engine deep-link page for ${engineId}.`,
    robots: { index: false, follow: false },
  };
}

export default function EngineDeepLinkPage({ params }: { params: Params }) {
  const engineId = params.engineId;
  if (!KNOWN_ENGINE_IDS.includes(engineId as (typeof KNOWN_ENGINE_IDS)[number])) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-[#07030f] px-5 py-10 text-white md:px-10">
      <div className="mx-auto max-w-4xl">
        <Link
          href="/engines"
          className="text-xs font-mono uppercase tracking-[0.3em] text-amber-200/70 hover:text-amber-100"
        >
          ← engine room
        </Link>
        <div className="mt-4 rounded-[2rem] border border-white/10 bg-white/[0.03] p-6">
          <p className="text-xs font-mono uppercase tracking-[0.3em] text-violet-200/70">
            backend engine
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight">{engineId}</h1>
          <p className="mt-3 text-sm text-white/60">
            Direct view of one backend engine. No payment, no posting, no paid
            providers — only the deterministic demo path and the live health
            snapshot from the backend `/engines` route.
          </p>
        </div>
        <EngineDeepLinkPanel engineId={engineId} />
      </div>
    </main>
  );
}
