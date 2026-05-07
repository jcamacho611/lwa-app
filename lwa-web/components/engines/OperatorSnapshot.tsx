"use client";

/**
 * OperatorSnapshot
 *
 * Live read of `POST /engines/operator_admin/demo` — the safest engine.
 * Renders the system snapshot, recommended next action, and engines
 * roll-up for an at-a-glance operator view.
 *
 * No payments, no posting, no paid providers. Falls back to a calm
 * "backend not configured" state if `NEXT_PUBLIC_API_BASE_URL` is unset.
 */

import { useEffect, useState } from "react";
import { runBackendEngineDemo } from "../../lib/backend-engines-api";

type SnapshotOutput = {
  snapshot?: { engines?: number; demo_mode?: boolean; alerts?: number };
  recommended_action?: string;
  // Older versions of the demo runner returned slightly different keys —
  // tolerate them gracefully.
  [key: string]: unknown;
};

type State =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ok"; summary: string; output: SnapshotOutput; warnings: string[] }
  | { kind: "error"; message: string };

export default function OperatorSnapshot() {
  const [state, setState] = useState<State>({ kind: "idle" });

  async function load() {
    setState({ kind: "loading" });
    try {
      const result = await runBackendEngineDemo("operator_admin", {
        focus: "engine_room",
      });
      setState({
        kind: "ok",
        summary: result.summary,
        output: result.output as SnapshotOutput,
        warnings: result.warnings,
      });
    } catch (err) {
      setState({
        kind: "error",
        message: err instanceof Error ? err.message : "Unknown error",
      });
    }
  }

  useEffect(() => {
    let cancelled = false;
    (async () => {
      await load();
      if (cancelled) return;
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/[0.03] p-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-amber-200/70">
            operator snapshot · operator_admin engine
          </p>
          <h2 className="mt-2 text-2xl font-black">System read-only roll-up</h2>
          <p className="mt-1 text-sm text-white/60">
            Live call to <code className="rounded bg-white/5 px-1.5 py-0.5 text-xs">POST /engines/operator_admin/demo</code>. Read-only. No payouts, no posting.
          </p>
        </div>
        <button
          type="button"
          onClick={load}
          disabled={state.kind === "loading"}
          className={`rounded-full px-4 py-2 text-xs font-bold transition ${
            state.kind === "loading"
              ? "bg-white/10 text-white/40"
              : "bg-amber-300 text-black hover:bg-amber-200"
          }`}
        >
          {state.kind === "loading" ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <Stat
          label="engines"
          value={
            state.kind === "ok"
              ? String(state.output?.snapshot?.engines ?? "—")
              : state.kind === "loading"
              ? "…"
              : "—"
          }
        />
        <Stat
          label="demo mode"
          value={
            state.kind === "ok"
              ? state.output?.snapshot?.demo_mode
                ? "ON"
                : "OFF"
              : state.kind === "loading"
              ? "…"
              : "—"
          }
        />
        <Stat
          label="alerts"
          value={
            state.kind === "ok"
              ? String(state.output?.snapshot?.alerts ?? 0)
              : state.kind === "loading"
              ? "…"
              : "—"
          }
        />
      </div>

      <div className="mt-5 rounded-2xl border border-white/10 bg-black/30 p-4">
        <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-white/45">
          recommended next action
        </p>
        <p className="mt-2 text-sm text-white/85">
          {state.kind === "ok"
            ? state.output?.recommended_action ?? "—"
            : state.kind === "loading"
            ? "Reading from operator_admin engine…"
            : state.kind === "error"
            ? `Error: ${state.message}`
            : "—"}
        </p>
      </div>

      {state.kind === "ok" && state.warnings.length > 0 && (
        <ul className="mt-3 space-y-1 text-xs text-white/55">
          {state.warnings.map((w, i) => (
            <li key={i}>· {w}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
      <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-white/45">
        {label}
      </p>
      <p className="mt-2 text-3xl font-black">{value}</p>
    </div>
  );
}
