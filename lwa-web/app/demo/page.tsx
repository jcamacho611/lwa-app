import type { Metadata } from "next";
import LwaPublicDemoLoopPanel from "../../components/demo/LwaPublicDemoLoopPanel";

export const metadata: Metadata = {
  title: "LWA Public Demo Loop",
  description: "A public, creator-first demo of the LWA loop.",
};

export default function DemoPage() {
  return (
    <main className="min-h-screen bg-[#050309] px-4 py-8 text-white md:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 rounded-[28px] border border-white/10 bg-white/[0.03] px-6 py-5">
          <p className="text-[11px] uppercase tracking-[0.34em] text-amber-200/70">LWA demo</p>
          <h1 className="mt-2 text-3xl font-black tracking-tight md:text-5xl">This is the public demo loop.</h1>
          <p className="mt-3 max-w-4xl text-sm text-white/65 md:text-base">
            Lee-Wuh guides the first session, the engine ranks source-driven clips, recovery stays honest, and Signal Sprint shows the game layer without fake payout claims.
          </p>
        </div>

        <LwaPublicDemoLoopPanel />
      </div>
    </main>
  );
}
