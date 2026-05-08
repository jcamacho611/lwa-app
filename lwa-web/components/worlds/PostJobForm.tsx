"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createCampaign } from "../../lib/worlds/api";
import { SafetyNotice } from "./SafetyNotice";

export function PostJobForm() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);

    const title = (data.get("title") as string).trim();
    const description = (data.get("description") as string).trim();
    const budget = parseFloat((data.get("budget") as string) || "0");
    const clipCount = parseInt((data.get("clip_count") as string) || "1", 10);
    const deadline = (data.get("deadline") as string) || "";
    const requirements = (data.get("requirements") as string).trim();
    const rightsConfirmed = data.get("rights_confirmed") === "on";

    if (!title || !description) {
      setError("Title and description are required.");
      return;
    }
    if (!rightsConfirmed) {
      setError("You must confirm rights before posting.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await createCampaign({
        title,
        description: description + (requirements ? `\n\nRequirements: ${requirements}` : ""),
        target_platform: "tiktok",
        source_type: "video",
        budget_amount: budget,
        clip_count: clipCount || 1,
        rights_required: deadline ? `Deadline: ${deadline}` : undefined,
      });
      router.push("/marketplace/campaigns");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create campaign. Try again.");
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="hero-card rounded-[32px] p-6 sm:p-8">
        <p className="section-kicker">Post a Job</p>
        <h2 className="page-title mt-3 text-3xl font-semibold">Create a clipping campaign</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/62">
          Post a campaign for clippers to discover and submit work. Budget, deadline, and requirements are shared
          with applicants. Final approval and payout are review-gated.
        </p>
      </section>

      <form onSubmit={handleSubmit} className="glass-panel grid gap-4 rounded-[28px] p-6">
        {error ? (
          <p className="rounded-[16px] border border-red-400/30 bg-red-400/10 p-3 text-sm text-red-700 dark:text-red-200">
            {error}
          </p>
        ) : null}

        <label className="grid gap-2">
          <span className="text-sm font-medium text-ink/70">Campaign title</span>
          <input
            name="title"
            required
            className="input-surface rounded-[20px] px-4 py-3 text-sm"
            placeholder="Turn this podcast into 12 TikTok-ready clips"
          />
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-medium text-ink/70">Description</span>
          <textarea
            name="description"
            required
            className="input-surface min-h-[128px] rounded-[20px] px-4 py-3 text-sm"
            placeholder="Explain what kind of clips you want..."
          />
        </label>

        <div className="grid gap-4 md:grid-cols-3">
          <label className="grid gap-2">
            <span className="text-sm font-medium text-ink/70">Budget (USD)</span>
            <input
              name="budget"
              type="number"
              min="0"
              step="1"
              className="input-surface rounded-[20px] px-4 py-3 text-sm"
              placeholder="300"
            />
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-medium text-ink/70">Clip count</span>
            <input
              name="clip_count"
              type="number"
              min="1"
              className="input-surface rounded-[20px] px-4 py-3 text-sm"
              placeholder="12"
            />
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-medium text-ink/70">Deadline</span>
            <input name="deadline" type="date" className="input-surface rounded-[20px] px-4 py-3 text-sm" />
          </label>
        </div>

        <label className="grid gap-2">
          <span className="text-sm font-medium text-ink/70">Requirements</span>
          <textarea
            name="requirements"
            className="input-surface min-h-[96px] rounded-[20px] px-4 py-3 text-sm"
            placeholder="9:16 vertical, captions, hook in first 2 seconds..."
          />
        </label>

        <label className="flex gap-3 rounded-[18px] border border-[var(--divider)] bg-[var(--surface-inset)] p-4 text-sm leading-7 text-ink/70">
          <input name="rights_confirmed" type="checkbox" className="mt-1 h-4 w-4 accent-[var(--gold)]" />
          <span>
            I confirm I own or have rights to the content/source and understand approved work may be reviewed for
            rights and policy compliance.
          </span>
        </label>

        <button
          type="submit"
          disabled={submitting}
          className="primary-button rounded-full px-5 py-3 text-sm font-semibold disabled:opacity-60"
        >
          {submitting ? "Posting…" : "Post campaign"}
        </button>
      </form>

      <SafetyNotice>
        Campaigns save as pending review. Payouts and final approval require admin review and audit log confirmation.
      </SafetyNotice>
    </div>
  );
}
