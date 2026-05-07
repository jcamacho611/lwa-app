"use client";

/**
 * EngineDeepLinkPanel
 *
 * Renders a single backend engine via the existing
 * `lib/backend-engines-api.ts` client. Used by the
 * `/engines/[engineId]` deep-link route.
 *
 * No backend writes. No auth. No payments. No paid providers.
 */

import { useEffect, useMemo, useState } from "react";
import {
  fetchBackendEngines,
  runBackendEngineDemo,
  type BackendEngineDemoResult,
  type BackendEngineMetadata,
} from "../../lib/backend-engines-api";

type LoadState =
  | { kind: "loading" }
  | { kind: "missing"; engineId: string }
  | { kind: "ready"; engine: BackendEngineMetadata };

function statusTone(status: string) {
  if (status === "production_ready")
    return "border-emerald-400/40 bg-emerald-400/10 text-emerald-200";
  if (status === "backend_ready" || status === "local_ready")
    return "border-violet-400/40 bg-violet-400/10 text-violet-100";
  if (status === "provider_ready")
    return "border-sky-400/40 bg-sky-400/10 text-sky-100";
  return "border-amber-400/40 bg-amber-400/10 text-amber-100";
}

export default function EngineDeepLinkPanel({ engineId }: { engineId: string }) {
  const [state, setState] = useState<LoadState>({ kind: "loading" });
  const [demoResult, setDemoResult] = useState<BackendEngineDemoResult | null>(
    null,
  );
  const [demoError, setDemoError] = useState<string>("");
  const [running, setRunning] = useState(false);

  useEffect(() => {
    let mounted = true;
    fetchBackendEngines().then((registry) => {
      if (!mounted) return;
      const engine = registry.engines[engineId];
      if (!engine) {
        setState({ kind: "missing", engineId });
        return;
      }
      setState({ kind: "ready", engine });
    });
    return () => {
      mounted = false;
    };
  }, [engineId]);

  const samplePayload = useMemo<Record<string, unknown>>(() => {
    switch (engineId) {
      case "creator":
        return { source: "demo source", title: "Demo upload" };
      case "brain":
        return { recommended_action: "Lead with the strongest hook" };
      case "render":
        return { render_requested: false };
      case "marketplace":
        return { preview_offer: "Creator growth lane" };
      case "wallet_entitlements":
        return { credits: 120 };
      case "proof_history":
        return { proof_id: "proof_demo_001" };
      case "world_game":
        return { current_realm: "signal_realm" };
      case "safety":
        return { request_type: "clip_review" };
      case "social_distribution":
        return { destination: "manual_review" };
      case "operator_admin":
      default:
        return { focus: "engine_inspection" };
    }
  }, [engineId]);

  async function handleRun() {
    setDemoError("");
    setDemoResult(null);
    setRunning(true);
    try {
      const result = await runBackendEngineDemo(engineId, samplePayload);
      setDemoResult(result);
    } catch (err) {
      setDemoError(err instanceof Error ? err.message : "Unknown demo error");
    } finally {
      setRunning(false);
    }
  }

  if (state.kind === "loading") {
    return (
      <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.03] p-6 text-sm text-white/60">
        Loading engine truth…
      </div>
    );
  }

  if (state.kind === "missing") {
    return (
      <div className="mt-8 rounded-3xl border border-amber-300/30 bg-amber-300/10 p-6 text-sm text-amber-100">
        Engine `{state.engineId}` is not in the live registry. Either the
        backend is unreachable or the engine id was renamed.
      </div>
    );
  }

  const engine = state.engine;
  return (
    <section className="mt-8 space-y-6">
      <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-mono uppercase tracking-[0.3em] text-violet-200/70">
              status
            </p>
            <h2 className="mt-1 text-2xl font-black">{engine.name}</h2>
          </div>
          <span
            className={`rounded-full border px-3 py-1 font-mono text-[10px] uppercase tracking-[0.25em] ${statusTone(
              engine.status,
            )}`}
          >
            {engine.status.replace(/_/g, " ")}
          </span>
        </div>

        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-white/45">
              capabilities · {engine.capabilities.length}
            </p>
            <ul className="mt-3 space-y-2">
              {engine.capabilities.length === 0 ? (
                <li className="text-sm text-white/50">
                  None reported by the engine.
                </li>
              ) : (
                engine.capabilities.map((cap) => (
                  <li key={cap.id} className="rounded-xl bg-white/5 p-3">
                    <p className="font-semibold">{cap.label}</p>
                    <p className="mt-1 text-xs text-white/55">
                      {cap.description}
                    </p>
                  </li>
                ))
              )}
            </ul>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-white/45">
              next required integrations
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {engine.next_required_integrations.map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-amber-300/20 bg-amber-300/10 px-3 py-1 text-xs text-amber-100"
                >
                  {item}
                </span>
              ))}
            </div>
            <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.25em] text-white/45">
              warnings
            </p>
            <ul className="mt-2 space-y-1 text-xs text-white/55">
              {engine.health.warnings.map((w, i) => (
                <li key={i}>· {w}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="rounded-3xl border border-violet-300/20 bg-violet-950/20 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-violet-200/70">
              live demo · POST /engines/{engineId}/demo
            </p>
            <p className="mt-1 text-sm text-white/65">
              Runs the deterministic demo path. No payouts, no external posting,
              no paid providers.
            </p>
          </div>
          <button
            type="button"
            onClick={handleRun}
            disabled={running}
            className={`rounded-full px-5 py-3 text-sm font-black transition ${
              running
                ? "bg-white/10 text-white/40"
                : "bg-amber-300 text-black hover:bg-amber-200"
            }`}
          >
            {running ? "Running…" : "Run safe demo"}
          </button>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-black/40 p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-white/45">
              sample payload
            </p>
            <pre className="mt-2 overflow-auto rounded-lg bg-black/60 p-3 text-[11px] text-white/70">
              {JSON.stringify(samplePayload, null, 2)}
            </pre>
          </div>
          <div className="rounded-2xl border border-white/10 bg-black/40 p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-white/45">
              response
            </p>
            {demoError ? (
              <p className="mt-2 text-sm text-red-200">{demoError}</p>
            ) : demoResult ? (
              <>
                <p className="mt-2 text-sm text-emerald-100">
                  {demoResult.summary}
                </p>
                <pre className="mt-2 max-h-72 overflow-auto rounded-lg bg-black/60 p-3 text-[11px] text-white/70">
                  {JSON.stringify(demoResult, null, 2)}
                </pre>
              </>
            ) : (
              <p className="mt-2 text-xs text-white/45">No run yet.</p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
