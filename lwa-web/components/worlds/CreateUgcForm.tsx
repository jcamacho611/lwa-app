"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createUgcAsset } from "../../lib/worlds/api";
import { SafetyNotice } from "./SafetyNotice";

const ASSET_TYPES = ["Hook Pack", "Caption Pack", "Quest Template", "Campaign Template", "Prompt Pack", "Cosmetic Concept"];

export function CreateUgcForm() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);

    const title = (data.get("title") as string).trim();
    const assetType = (data.get("asset_type") as string).trim();
    const description = (data.get("description") as string).trim();
    const rightsConfirmed = data.get("rights_confirmed") === "on";

    if (!title || !description) {
      setError("Title and description are required.");
      return;
    }
    if (!rightsConfirmed) {
      setError("You must confirm original rights before saving.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await createUgcAsset({ title, asset_type: assetType, description, rights_confirmed: true });
      router.push("/ugc");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save asset. Try again.");
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="hero-card grid gap-4 rounded-[32px] p-6">
        {error ? (
          <p className="rounded-[16px] border border-red-400/30 bg-red-400/10 p-3 text-sm text-red-700 dark:text-red-200">
            {error}
          </p>
        ) : null}

        <label className="grid gap-2">
          <span className="text-sm text-ink/62">Asset title</span>
          <input
            name="title"
            required
            className="input-surface rounded-[20px] px-4 py-3 text-sm"
            placeholder="Gold Thread Hook Pack"
          />
        </label>

        <label className="grid gap-2">
          <span className="text-sm text-ink/62">Asset type</span>
          <select name="asset_type" className="input-surface rounded-[20px] px-4 py-3 text-sm">
            {ASSET_TYPES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </label>

        <label className="grid gap-2">
          <span className="text-sm text-ink/62">Description</span>
          <textarea
            name="description"
            required
            className="input-surface min-h-32 rounded-[20px] px-4 py-3 text-sm"
            placeholder="Describe the asset and how creators use it..."
          />
        </label>

        <label className="flex gap-3 rounded-[18px] border border-[var(--divider)] bg-[var(--surface-inset)] p-4 text-sm leading-6 text-ink/70">
          <input name="rights_confirmed" type="checkbox" className="mt-1 h-4 w-4 accent-[var(--gold)]" />
          <span>
            I confirm this asset is original or properly licensed and does not copy existing characters, brands,
            worlds, or protected IP.
          </span>
        </label>

        <button
          type="submit"
          disabled={submitting}
          className="primary-button justify-center rounded-full px-5 py-3 text-sm disabled:opacity-60"
        >
          {submitting ? "Saving…" : "Save UGC draft"}
        </button>
      </form>

      <SafetyNotice>
        UGC assets save as drafts pending review before marketplace availability. No automatic publishing occurs.
      </SafetyNotice>
    </div>
  );
}
