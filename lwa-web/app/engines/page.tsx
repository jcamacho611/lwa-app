import type { Metadata } from "next";
import Link from "next/link";

import BackendEngineRoomPanel from "../../components/engines/BackendEngineRoomPanel";
import EngineHealthBadge from "../../components/engines/EngineHealthBadge";
import OperatorSnapshot from "../../components/engines/OperatorSnapshot";
import { getDeployOrder } from "../../lib/lwa-engine-deploy-order";
import { LWA_ENGINE_STAGE_BINDINGS } from "../../lib/lwa-engine-stage-map";

export const metadata: Metadata = {
  title: "LWA Engine Room",
  description: "Actual backend engine status for the LWA platform.",
};

export default function EnginesPage() {
  return (
    <main className="min-h-screen bg-[#07030f] px-5 py-10 text-white md:px-10">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 rounded-[2rem] border border-white/10 bg-white/[0.03] p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-violet-200/70">Actual backend truth</p>
              <h1 className="mt-3 text-4xl font-black tracking-tight md:text-6xl">LWA Engine Room</h1>
            </div>
            <EngineHealthBadge pollMs={30000} />
          </div>
          <p className="mt-4 max-w-4xl text-base text-white/65">
            This route separates real backend engines from frontend demos. Railway services are deployable boxes; backend engines are modules inside the API until they are intentionally split into workers or services.
          </p>
        </div>

        <BackendEngineRoomPanel />

        <div className="mt-10">
          <OperatorSnapshot />
        </div>

        <section className="mt-10 rounded-[2rem] border border-white/10 bg-white/[0.03] p-6">
          <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="text-xs font-mono uppercase tracking-[0.3em] text-amber-200/70">demo &rarr; engine map</p>
              <h2 className="mt-2 text-2xl font-black">Each demo stage is grounded in a real engine</h2>
              <p className="mt-2 max-w-3xl text-sm text-white/60">
                Click any stage to deep-link to the backend engine that powers it. The public demo journey at <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">/demo</code> walks through these in order.
              </p>
            </div>
          </div>
          <ul className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {LWA_ENGINE_STAGE_BINDINGS.map((binding, i) => (
              <li key={binding.stageId}>
                <Link
                  href={`/engines/${binding.engineId}`}
                  className="group flex h-full flex-col rounded-2xl border border-white/10 bg-black/30 p-4 transition hover:border-amber-300/40 hover:bg-amber-300/[0.04]"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-[10px] uppercase tracking-[0.25em] text-white/45">
                      stage {String(i + 1).padStart(2, "0")}
                    </span>
                    <span className="rounded-full border border-amber-300/30 bg-amber-300/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.2em] text-amber-100">
                      {binding.engineId}
                    </span>
                  </div>
                  <h3 className="mt-2 text-base font-semibold text-white">
                    {binding.stageId.replace(/_/g, " ")}
                  </h3>
                  <p className="mt-1 text-xs text-white/55">{binding.rationale}</p>
                  <span className="mt-auto pt-3 font-mono text-[10px] uppercase tracking-[0.25em] text-violet-200/70 group-hover:text-amber-200">
                    open engine &rarr;
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  );
}
