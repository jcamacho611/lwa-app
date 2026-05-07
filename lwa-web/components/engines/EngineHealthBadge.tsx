"use client";

/**
 * EngineHealthBadge
 *
 * Small drop-in widget that calls the backend `/engines/health` route
 * and surfaces a "X/N healthy" pill with status detail on hover/click.
 * Falls back to a calm "—" state when the backend URL is not configured.
 *
 * No backend writes. No auth. No payments. Safe to embed anywhere.
 */

import { useEffect, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "";

type EngineHealthEntry = {
  engine_id: string;
  name: string;
  status: string;
  healthy: boolean;
  warnings?: string[];
};

type EngineHealthResponse = {
  count: number;
  healthy_count: number;
  unhealthy_count: number;
  engines: Record<string, EngineHealthEntry>;
  status_summary: Record<string, number>;
};

type FetchState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; data: EngineHealthResponse }
  | { kind: "error"; message: string }
  | { kind: "no_backend" };

export default function EngineHealthBadge({
  pollMs = 0,
}: {
  /** If > 0, refresh the health snapshot at this interval. */
  pollMs?: number;
}) {
  const [state, setState] = useState<FetchState>({ kind: "idle" });
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setInterval> | null = null;

    async function load() {
      if (!API_BASE) {
        if (!cancelled) setState({ kind: "no_backend" });
        return;
      }
      if (!cancelled) setState({ kind: "loading" });
      try {
        const res = await fetch(`${API_BASE}/engines/health`, {
          cache: "no-store",
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = (await res.json()) as EngineHealthResponse;
        if (!cancelled) setState({ kind: "ready", data });
      } catch (err) {
        if (!cancelled) {
          setState({
            kind: "error",
            message: err instanceof Error ? err.message : "fetch failed",
          });
        }
      }
    }

    load();
    if (pollMs > 0) {
      timer = setInterval(load, pollMs);
    }
    return () => {
      cancelled = true;
      if (timer) clearInterval(timer);
    };
  }, [pollMs]);

  let label: string;
  let tone: "ok" | "warn" | "err" | "muted";
  if (state.kind === "ready") {
    label = `${state.data.healthy_count}/${state.data.count} engines healthy`;
    tone =
      state.data.healthy_count === state.data.count
        ? "ok"
        : state.data.healthy_count >= state.data.count - 2
        ? "warn"
        : "err";
  } else if (state.kind === "loading") {
    label = "engines · loading";
    tone = "muted";
  } else if (state.kind === "no_backend") {
    label = "engines · backend not configured";
    tone = "muted";
  } else if (state.kind === "error") {
    label = `engines · ${state.message}`;
    tone = "err";
  } else {
    label = "engines · —";
    tone = "muted";
  }

  const toneClass =
    tone === "ok"
      ? "border-emerald-400/40 bg-emerald-400/10 text-emerald-200"
      : tone === "warn"
      ? "border-amber-300/40 bg-amber-300/10 text-amber-100"
      : tone === "err"
      ? "border-red-400/40 bg-red-500/10 text-red-100"
      : "border-white/15 bg-white/[0.04] text-white/60";

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-[11px] font-mono uppercase tracking-[0.18em] transition ${toneClass}`}
        aria-expanded={open}
      >
        <span
          aria-hidden
          className={`h-1.5 w-1.5 rounded-full ${
            tone === "ok"
              ? "bg-emerald-300"
              : tone === "warn"
              ? "bg-amber-300"
              : tone === "err"
              ? "bg-red-300"
              : "bg-white/40"
          }`}
        />
        {label}
      </button>

      {open && state.kind === "ready" && (
        <div className="absolute right-0 z-10 mt-2 w-72 rounded-2xl border border-white/10 bg-black/90 p-3 text-xs text-white/80 shadow-xl shadow-black/40">
          <div className="mb-2 font-mono text-[10px] uppercase tracking-[0.25em] text-amber-200/80">
            engine health · {state.data.count}
          </div>
          <ul className="divide-y divide-white/5">
            {Object.values(state.data.engines).map((entry) => (
              <li
                key={entry.engine_id}
                className="flex items-center justify-between gap-2 py-1.5"
              >
                <span className="font-mono text-[11px] text-white/70">
                  {entry.engine_id}
                </span>
                <span
                  className={`rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.2em] ${
                    entry.healthy
                      ? "border-emerald-400/40 bg-emerald-400/10 text-emerald-200"
                      : "border-white/15 bg-white/[0.04] text-white/55"
                  }`}
                >
                  {entry.status.replace(/_/g, " ")}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
