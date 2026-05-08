"use client";

import { useEffect, useState } from "react";
import { readStoredToken } from "../../lib/auth";
import { loadPostingConnections } from "../../lib/api";
import type { PostingConnection } from "../../lib/types";

const PROVIDER_LABELS: Record<string, string> = {
  tiktok: "TikTok",
  instagram: "Instagram",
  youtube: "YouTube",
  twitter: "Twitter / X",
  facebook: "Facebook",
  snapchat: "Snapchat",
  pinterest: "Pinterest",
  linkedin: "LinkedIn",
};

function providerLabel(provider: string) {
  return PROVIDER_LABELS[provider.toLowerCase()] ?? provider;
}

export function PostingConnectionsView() {
  const [connections, setConnections] = useState<PostingConnection[]>([]);
  const [state, setState] = useState<"loading" | "no-token" | "error" | "ready">("loading");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const token = readStoredToken();
    if (!token) {
      setState("no-token");
      return;
    }
    loadPostingConnections(token)
      .then((data) => {
        setConnections(data);
        setState("ready");
      })
      .catch((err) => {
        setErrorMsg(err instanceof Error ? err.message : "Unable to load connections.");
        setState("error");
      });
  }, []);

  if (state === "loading") {
    return <div className="glass-panel rounded-[28px] p-6 text-sm text-ink/60">Loading integrations…</div>;
  }

  if (state === "no-token") {
    return (
      <div className="glass-panel rounded-[28px] p-6">
        <p className="text-sm font-semibold text-ink">Sign in to view posting connections</p>
        <p className="mt-2 text-sm text-ink/60">Posting connections are tied to your account.</p>
        <a href="/generate" className="primary-button mt-4 inline-flex rounded-full px-5 py-3 text-sm font-semibold">
          Go to generator
        </a>
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className="rounded-[28px] border border-red-400/20 bg-red-400/8 p-6">
        <p className="text-sm font-semibold text-red-200">Unable to load connections</p>
        <p className="mt-2 text-xs text-red-200/70">{errorMsg}</p>
        <p className="mt-3 text-xs text-ink/46">Posting connections require Scale plan. Check your plan in the generator.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-[28px] border border-amber-300/20 bg-amber-300/8 px-5 py-4 text-sm leading-6 text-amber-100/80">
        <span className="font-semibold">Scheduling readiness only.</span> Connections stored here record provider intent, not live OAuth tokens. Direct API posting is not yet active. No content is published automatically.
      </div>

      {connections.length === 0 ? (
        <div className="glass-panel rounded-[28px] p-6">
          <p className="section-kicker">No connections yet</p>
          <h3 className="mt-3 text-xl font-semibold text-ink">Platform readiness starts here</h3>
          <p className="mt-3 text-sm leading-7 text-ink/60">
            When a posting connection is added via the generator workspace, it will appear here. OAuth flows and live publishing are not yet active.
          </p>
        </div>
      ) : (
        <section className="grid gap-5 lg:grid-cols-2">
          {connections.map((conn) => (
            <article key={conn.id} className="glass-panel rounded-[24px] p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-ink/46">Posting connection</p>
                  <h3 className="mt-1 text-xl font-semibold text-ink">{providerLabel(conn.provider)}</h3>
                  {conn.account_label ? (
                    <p className="mt-1 text-sm text-ink/60">{conn.account_label}</p>
                  ) : null}
                </div>
                <span className={[
                  "rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em]",
                  conn.is_active
                    ? "border-emerald-300/25 bg-emerald-300/10 text-emerald-200"
                    : "border-white/12 bg-white/[0.05] text-ink/46",
                ].join(" ")}>
                  {conn.is_active ? "Active" : "Inactive"}
                </span>
              </div>
              {conn.created_at ? (
                <p className="mt-3 text-xs text-ink/36">Added {new Date(conn.created_at).toLocaleDateString()}</p>
              ) : null}
            </article>
          ))}
        </section>
      )}
    </div>
  );
}
