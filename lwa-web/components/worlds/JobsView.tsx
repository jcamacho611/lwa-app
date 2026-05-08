"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { readStoredToken } from "../../lib/auth";
import { listMyJobsWithAuth } from "../../lib/worlds/api";
import type { WorldJob } from "../../lib/worlds/types";
import { JobStatusCard } from "./JobStatusCard";

const ACTIVE_STATUSES = new Set(["queued", "running", "retrying"]);
const AUTO_POLL_MS = 8_000;

export function JobsView() {
  const [jobs, setJobs] = useState<WorldJob[]>([]);
  const [state, setState] = useState<"loading" | "no-token" | "error" | "ready">("loading");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const tokenRef = useRef<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const load = useCallback(async (t: string, silent = false) => {
    if (!silent) setRefreshing(true);
    try {
      const data = await listMyJobsWithAuth(t);
      setJobs(data);
      setState("ready");
    } catch (err) {
      if (!silent) {
        setErrorMsg(err instanceof Error ? err.message : "Unable to load jobs.");
        setState("error");
      }
    } finally {
      if (!silent) setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    const t = readStoredToken();
    if (!t) {
      setState("no-token");
      return;
    }
    tokenRef.current = t;
    void load(t);
  }, [load]);

  useEffect(() => {
    if (state !== "ready") return;
    const hasActive = jobs.some((j) => ACTIVE_STATUSES.has(j.status));
    if (!hasActive || !tokenRef.current) return;

    pollRef.current = setTimeout(() => {
      if (tokenRef.current) void load(tokenRef.current, true);
    }, AUTO_POLL_MS);

    return () => {
      if (pollRef.current) clearTimeout(pollRef.current);
    };
  }, [jobs, state, load]);

  const counts = {
    queued: jobs.filter((j) => j.status === "queued").length,
    running: jobs.filter((j) => j.status === "running").length,
    succeeded: jobs.filter((j) => j.status === "succeeded").length,
    failed: jobs.filter((j) => j.status === "failed").length,
    retrying: jobs.filter((j) => j.status === "retrying").length,
    cancelled: jobs.filter((j) => j.status === "cancelled").length,
  };

  return (
    <div className="space-y-6">
      <section className="hero-card rounded-[30px] p-6">
        <p className="section-kicker">Job Monitor</p>
        <h2 className="mt-3 text-3xl font-semibold text-ink">
          Track uploads, transcripts, AI scoring, clip generation, and renders.
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/62">
          Long-running work has records for status, progress, attempts, events, retry state, and ownership.
        </p>
      </section>

      <div className="rounded-[28px] border border-amber-300/20 bg-amber-300/8 px-5 py-4 text-sm leading-6 text-amber-100/80">
        Jobs may retry processing tasks, but they must not double-charge credits, duplicate earnings, or approve payouts automatically.
      </div>

      {state === "loading" && (
        <div className="glass-panel rounded-[28px] p-6 text-sm text-ink/60">Loading jobs…</div>
      )}

      {state === "no-token" && (
        <div className="glass-panel rounded-[28px] p-6">
          <p className="text-sm font-semibold text-ink">Sign in to view your jobs</p>
          <p className="mt-2 text-sm text-ink/60">Job history is tied to your account.</p>
          <a href="/generate" className="primary-button mt-4 inline-flex rounded-full px-5 py-3 text-sm font-semibold">
            Go to generator
          </a>
        </div>
      )}

      {state === "error" && (
        <div className="rounded-[28px] border border-red-400/20 bg-red-400/8 p-6">
          <p className="text-sm font-semibold text-red-200">Unable to load jobs</p>
          <p className="mt-2 text-xs text-red-200/70">{errorMsg}</p>
        </div>
      )}

      {state === "ready" && (
        <>
          <div className="flex items-center justify-between gap-4">
            <p className="text-sm text-ink/46">
              {jobs.some((j) => ACTIVE_STATUSES.has(j.status)) ? "Auto-refreshing every 8 s" : `${jobs.length} total`}
            </p>
            <button
              type="button"
              disabled={refreshing}
              onClick={() => tokenRef.current && void load(tokenRef.current)}
              className="secondary-button rounded-full px-4 py-2 text-sm font-semibold disabled:opacity-60"
            >
              {refreshing ? "Refreshing…" : "Refresh"}
            </button>
          </div>

          <section className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
            {(Object.entries(counts) as [string, number][]).map(([label, value]) => (
              <div key={label} className="metric-tile rounded-[24px] p-5">
                <p className="text-sm capitalize text-ink/46">{label}</p>
                <p className="mt-2 text-3xl font-semibold text-ink">{value}</p>
              </div>
            ))}
          </section>

          <section>
            <h3 className="mb-4 text-2xl font-semibold text-ink">Your jobs</h3>
            {jobs.length === 0 ? (
              <div className="glass-panel rounded-[28px] p-6 text-sm text-ink/60">
                No jobs found for your account. Jobs appear after running generation, batch, or recovery operations.
              </div>
            ) : (
              <div className="grid gap-5 lg:grid-cols-2">
                {jobs.map((job) => (
                  <JobStatusCard key={job.id} job={job} />
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
