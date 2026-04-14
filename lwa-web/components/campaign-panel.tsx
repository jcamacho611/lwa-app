"use client";

import { useMemo, useState } from "react";
import { CampaignSummary, PlatformOption } from "../lib/types";

const platforms: PlatformOption[] = ["TikTok", "Instagram Reels", "YouTube Shorts"];

type CampaignPanelProps = {
  campaigns: CampaignSummary[];
  onCreate: (payload: {
    title: string;
    description?: string;
    allowed_platforms: string[];
    target_angle?: string;
    requirements?: string;
    payout_cents_per_1000_views?: number;
  }) => Promise<void>;
  onUpdateStatus: (campaignId: string, status: string) => Promise<void>;
};

export function CampaignPanel({ campaigns, onCreate, onUpdateStatus }: CampaignPanelProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [targetAngle, setTargetAngle] = useState("");
  const [requirements, setRequirements] = useState("");
  const [payout, setPayout] = useState("");
  const [allowedPlatforms, setAllowedPlatforms] = useState<string[]>(["TikTok"]);
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [updatingCampaignId, setUpdatingCampaignId] = useState<string | null>(null);

  const orderedCampaigns = useMemo(
    () => [...campaigns].sort((left, right) => (right.created_at || "").localeCompare(left.created_at || "")),
    [campaigns],
  );

  function togglePlatform(platform: string) {
    setAllowedPlatforms((current) =>
      current.includes(platform) ? current.filter((item) => item !== platform) : [...current, platform],
    );
  }

  async function handleCreate() {
    if (!title.trim()) {
      setMessage("Campaign title is required.");
      return;
    }

    setIsSaving(true);
    setMessage(null);
    try {
      await onCreate({
        title: title.trim(),
        description: description.trim() || undefined,
        allowed_platforms: allowedPlatforms,
        target_angle: targetAngle.trim() || undefined,
        requirements: requirements.trim() || undefined,
        payout_cents_per_1000_views: payout ? Number(payout) : undefined,
      });
      setTitle("");
      setDescription("");
      setTargetAngle("");
      setRequirements("");
      setPayout("");
      setAllowedPlatforms(["TikTok"]);
      setMessage("Campaign created.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create campaign.");
    } finally {
      setIsSaving(false);
    }
  }

  async function updateStatus(campaignId: string, status: string) {
    setUpdatingCampaignId(campaignId);
    setMessage(null);
    try {
      await onUpdateStatus(campaignId, status);
      setMessage(`Campaign moved to ${status}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to update campaign.");
    } finally {
      setUpdatingCampaignId(null);
    }
  }

  return (
    <section className="grid gap-6 xl:grid-cols-[0.98fr,1.02fr]">
      <div className="glass-panel rounded-[32px] p-6 sm:p-8">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Campaigns</p>
        <h3 className="mt-2 text-3xl font-semibold text-ink">Create a distribution brief</h3>
        <p className="mt-4 text-sm leading-7 text-ink/64">
          Turn loose clips into a focused push with a target angle, platform list, and clear posting requirements.
        </p>

        <div className="mt-6 space-y-5">
          <Field label="Campaign title" value={title} onChange={setTitle} placeholder="Summer launch sprint" />
          <Field label="Target angle" value={targetAngle} onChange={setTargetAngle} placeholder="curiosity, value, story" />
          <Field
            label="Description"
            value={description}
            onChange={setDescription}
            multiline
            placeholder="Explain the campaign goal, audience, and packaging direction."
          />
          <Field
            label="Requirements"
            value={requirements}
            onChange={setRequirements}
            multiline
            placeholder="Mandatory disclosures, duration range, brand notes."
          />

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-ink/80">Payout per 1,000 views (cents)</span>
            <input
              type="number"
              min="0"
              value={payout}
              onChange={(event) => setPayout(event.target.value)}
              className="w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent/40"
            />
          </label>

          <div>
            <p className="mb-3 text-sm font-medium text-ink/80">Allowed platforms</p>
            <div className="flex flex-wrap gap-3">
              {platforms.map((platform) => {
                const active = allowedPlatforms.includes(platform);
                return (
                  <button
                    key={platform}
                    type="button"
                    onClick={() => togglePlatform(platform)}
                    className={[
                      "rounded-full border px-4 py-2 text-sm transition",
                      active ? "border-accent/30 bg-accent/10 text-accent" : "border-white/10 bg-white/5 text-ink/72",
                    ].join(" ")}
                  >
                    {platform}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={isSaving}
              onClick={handleCreate}
              className="rounded-full bg-gradient-to-r from-accent to-accentSoft px-5 py-3 text-sm font-semibold text-white shadow-glow disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSaving ? "Creating campaign..." : "Create Campaign"}
            </button>
            {message ? <span className="text-sm text-accent">{message}</span> : null}
          </div>
        </div>
      </div>

      <div className="glass-panel rounded-[32px] p-6 sm:p-8">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Campaign State</p>
            <h3 className="mt-2 text-2xl font-semibold text-ink">Live workflow inventory</h3>
          </div>
          <span className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-ink/72">{campaigns.length} campaigns</span>
        </div>

        <div className="mt-6 space-y-3">
          {orderedCampaigns.length ? (
            orderedCampaigns.map((campaign) => (
              <div key={campaign.id} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/72">{campaign.status}</span>
                  {campaign.target_angle ? (
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/72">
                      {campaign.target_angle}
                    </span>
                  ) : null}
                </div>
                <p className="mt-3 text-lg font-semibold text-ink">{campaign.title || campaign.name || "Campaign"}</p>
                <p className="mt-2 text-sm leading-7 text-ink/62">
                  {campaign.description || "No description yet."}
                </p>
                <p className="mt-2 text-sm text-ink/55">
                  {(campaign.allowed_platforms || []).join(" · ") || "Any platform"} · $
                  {((campaign.payout_cents_per_1000_views || 0) / 100).toFixed(2)} per 1k views
                </p>

                <div className="mt-4 flex flex-wrap gap-3">
                  {["active", "paused", "completed"].map((status) => (
                    <button
                      key={status}
                      type="button"
                      disabled={updatingCampaignId === campaign.id || campaign.status === status}
                      onClick={() => updateStatus(campaign.id, status)}
                      className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {campaign.status === status ? `Current: ${status}` : `Set ${status}`}
                    </button>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4 text-sm text-ink/62">
              No campaigns yet. Create one to turn scattered clip output into a real publishing brief.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  multiline = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  multiline?: boolean;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-ink/80">{label}</span>
      {multiline ? (
        <textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          rows={4}
          placeholder={placeholder}
          className="min-h-[110px] w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent/40"
        />
      ) : (
        <input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          className="w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent/40"
        />
      )}
    </label>
  );
}
