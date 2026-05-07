"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowRight, BadgeCheck, Cpu, RefreshCw, Sparkles, ShieldAlert } from "lucide-react";
import {
  fetchBackendEngines,
  runBackendEngineDemo,
  type BackendEngineDemoResult,
  type BackendEngineMetadata,
  type BackendEngineRegistryResponse,
} from "../../lib/backend-engines-api";

function statusLabel(status: string) {
  return status.replace(/_/g, " ").toUpperCase();
}

function statusClass(status: string) {
  if (status === "production_ready") return "border-emerald-400/40 bg-emerald-400/10 text-emerald-200";
  if (status === "backend_ready" || status === "local_ready") return "border-violet-400/40 bg-violet-400/10 text-violet-100";
  if (status === "provider_ready") return "border-sky-400/40 bg-sky-400/10 text-sky-100";
  return "border-amber-400/40 bg-amber-400/10 text-amber-100";
}

export default function BackendEngineRoomPanel() {
  const [registry, setRegistry] = useState<BackendEngineRegistryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedEngineId, setSelectedEngineId] = useState<string>("creator");
  const [demoResult, setDemoResult] = useState<BackendEngineDemoResult | null>(null);
  const [demoError, setDemoError] = useState<string>("");

  useEffect(() => {
    let mounted = true;
    fetchBackendEngines()
      .then((data) => {
        if (!mounted) return;
        setRegistry(data);
        const firstEngineId = Object.keys(data.engines)[0];
        if (firstEngineId) setSelectedEngineId(firstEngineId);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const engines = useMemo(() => {
    if (!registry) return [] as BackendEngineMetadata[];
    return Object.values(registry.engines);
  }, [registry]);

  const selectedEngine = registry?.engines[selectedEngineId];

  async function handleRunDemo() {
    setDemoError("");
    setDemoResult(null);
    try {
      const result = await runBackendEngineDemo(selectedEngineId, {
        source: "demo source",
        platform: "tiktok",
        event: "engine_inspection",
      });
      setDemoResult(result);
    } catch (error) {
      setDemoError(error instanceof Error ? error.message : "Unknown engine demo error");
    }
  }

  return (
    <section className="rounded-[28px] border border-violet-300/20 bg-black/70 p-6 text-white shadow-2xl shadow-violet-950/30">
      <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-amber-200/70">LWA Engine Room</p>
          <h2 className="mt-2 text-3xl font-black tracking-tight">Actual Backend Engines</h2>
          <p className="mt-2 max-w-3xl text-sm text-white/65">
            This route shows backend-owned engines from the `/engines` API when available. If the backend route is not connected yet, it falls back to honest local demo data.
          </p>
        </div>
        <div className="rounded-2xl border border-amber-300/20 bg-amber-300/10 px-4 py-3 text-sm text-amber-100">
          {loading ? "Loading engine truth..." : `${registry?.count ?? 0} engines tracked`}
        </div>
      </div>

      {registry?.note ? (
        <div className="mb-6 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/70">
          {registry.note}
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        {engines.map((engine) => (
          <button
            key={engine.engine_id}
            type="button"
            onClick={() => setSelectedEngineId(engine.engine_id)}
            className={`rounded-3xl border p-5 text-left transition hover:border-amber-300/50 ${
              selectedEngineId === engine.engine_id
                ? "border-amber-300/60 bg-amber-300/10"
                : "border-white/10 bg-white/[0.03]"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-bold">{engine.name}</h3>
                <p className="mt-1 text-xs text-white/45">{engine.engine_id}</p>
              </div>
              <span className={`rounded-full border px-3 py-1 text-[10px] font-bold ${statusClass(engine.status)}`}>
                {statusLabel(engine.status)}
              </span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2 text-[11px] text-white/60">
              <span className="rounded-full border border-white/10 px-3 py-1">Backend module</span>
              <span className="rounded-full border border-white/10 px-3 py-1">
                {engine.capabilities.length} capabilities
              </span>
              <span className="rounded-full border border-white/10 px-3 py-1">
                {engine.health.healthy ? "Healthy" : "Not production-ready"}
              </span>
            </div>
          </button>
        ))}
      </div>

      {selectedEngine ? (
        <div className="mt-8 rounded-3xl border border-violet-300/20 bg-violet-950/20 p-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-violet-200/70">Selected Engine</p>
              <h3 className="mt-1 text-2xl font-black">{selectedEngine.name}</h3>
            </div>
            <button
              type="button"
              onClick={handleRunDemo}
              className="rounded-full bg-amber-300 px-5 py-3 text-sm font-black text-black transition hover:bg-amber-200"
            >
              Run safe demo
            </button>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
              <h4 className="font-bold text-white">Capabilities</h4>
              <div className="mt-3 space-y-3">
                {selectedEngine.capabilities.length === 0 ? (
                  <p className="text-sm text-white/50">No live capabilities returned yet.</p>
                ) : (
                  selectedEngine.capabilities.map((capability) => (
                    <div key={capability.id} className="rounded-xl bg-white/5 p-3">
                      <p className="font-semibold text-white">{capability.label}</p>
                      <p className="mt-1 text-xs text-white/55">{capability.description}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
              <h4 className="font-bold text-white">Next integrations</h4>
              <div className="mt-3 flex flex-wrap gap-2">
                {selectedEngine.next_required_integrations.map((item) => (
                  <span key={item} className="rounded-full border border-amber-300/20 bg-amber-300/10 px-3 py-1 text-xs text-amber-100">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {demoError ? (
            <div className="mt-5 rounded-2xl border border-red-400/30 bg-red-500/10 p-4 text-sm text-red-100">
              {demoError}
            </div>
          ) : null}

          {demoResult ? (
            <div className="mt-5 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4">
              <p className="text-sm font-bold text-emerald-100">{demoResult.summary}</p>
              <pre className="mt-3 max-h-80 overflow-auto rounded-xl bg-black/50 p-4 text-xs text-white/70">
                {JSON.stringify(demoResult, null, 2)}
              </pre>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
