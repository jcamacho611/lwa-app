"use client";

import { useEffect, useState } from "react";
import { readStoredToken } from "../../lib/auth";
import { createPostingConnection, loadPostingConnections } from "../../lib/api";
import type { PostingConnection } from "../../lib/types";

const PROVIDERS = ["tiktok", "instagram", "youtube", "twitter", "facebook", "snapchat", "pinterest", "linkedin"];

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
  const [token, setToken] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [formProvider, setFormProvider] = useState("tiktok");
  const [formLabel, setFormLabel] = useState("");
  const [adding, setAdding] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  useEffect(() => {
    const t = readStoredToken();
    if (!t) {
      setState("no-token");
      return;
    }
    setToken(t);
    loadPostingConnections(t)
      .then((data) => {
        setConnections(data);
        setState("ready");
      })
      .catch((err) => {
        setErrorMsg(err instanceof Error ? err.message : "Unable to load connections.");
        setState("error");
      });
  }, []);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    setAdding(true);
    setAddError(null);
    try {
      const conn = await createPostingConnection(token, {
        provider: formProvider,
        account_label: formLabel.trim() || undefined,
      });
      setConnections((prev) => [...prev, conn]);
      setShowForm(false);
      setFormLabel("");
    } catch (err) {
      setAddError(err instanceof Error ? err.message : "Failed to add connection.");
    } finally {
      setAdding(false);
    }
  }

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

      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-ink/60">{connections.length} connection{connections.length !== 1 ? "s" : ""}</p>
        <button
          type="button"
          onClick={() => setShowForm((v) => !v)}
          className="secondary-button rounded-full px-4 py-2 text-sm font-semibold"
        >
          {showForm ? "Cancel" : "Add connection"}
        </button>
      </div>

      {showForm ? (
        <form onSubmit={handleAdd} className="glass-panel grid gap-4 rounded-[28px] p-6">
          {addError ? (
            <p className="rounded-[16px] border border-red-400/30 bg-red-400/10 p-3 text-sm text-red-200">{addError}</p>
          ) : null}
          <label className="grid gap-2">
            <span className="text-sm font-medium text-ink/70">Platform</span>
            <select
              value={formProvider}
              onChange={(e) => setFormProvider(e.target.value)}
              className="input-surface rounded-[20px] px-4 py-3 text-sm"
            >
              {PROVIDERS.map((p) => (
                <option key={p} value={p}>{providerLabel(p)}</option>
              ))}
            </select>
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-medium text-ink/70">Account label (optional)</span>
            <input
              value={formLabel}
              onChange={(e) => setFormLabel(e.target.value)}
              placeholder="@handle or channel name"
              className="input-surface rounded-[20px] px-4 py-3 text-sm"
            />
          </label>
          <button
            type="submit"
            disabled={adding}
            className="primary-button rounded-full px-5 py-3 text-sm font-semibold disabled:opacity-60"
          >
            {adding ? "Adding…" : "Add connection"}
          </button>
        </form>
      ) : null}

      {connections.length === 0 ? (
        <div className="glass-panel rounded-[28px] p-6">
          <p className="section-kicker">No connections yet</p>
          <h3 className="mt-3 text-xl font-semibold text-ink">Platform readiness starts here</h3>
          <p className="mt-3 text-sm leading-7 text-ink/60">
            Add a posting connection to record your intended platform targets. OAuth flows and live publishing are not yet active.
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
