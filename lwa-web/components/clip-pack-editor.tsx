"use client";

import { useEffect, useState } from "react";
import { ClipPackDetail } from "../lib/types";

export type ClipPatchPayload = {
  hook_override?: string;
  caption_override?: string;
  cta_override?: string;
  thumbnail_text_override?: string;
  packaging_angle_override?: string;
  trim_start_seconds?: number;
  trim_end_seconds?: number;
};

type ClipPackEditorProps = {
  clipPack: ClipPackDetail;
  onSave: (clipId: string, updates: ClipPatchPayload) => Promise<void>;
  onClose: () => void;
  readOnly?: boolean;
  lockedMessage?: string;
};

export function ClipPackEditor({ clipPack, onSave, onClose, readOnly = false, lockedMessage }: ClipPackEditorProps) {
  const [selectedClipId, setSelectedClipId] = useState<string | null>(clipPack.clips[0]?.record_id || clipPack.clips[0]?.clip_id || null);
  const [draft, setDraft] = useState<ClipPatchPayload>({});
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const selectedClip = clipPack.clips.find((clip) => (clip.record_id || clip.clip_id) === selectedClipId);

  useEffect(() => {
    if (!selectedClip) {
      setDraft({});
      return;
    }
    setDraft({
      hook_override: selectedClip.hook || "",
      caption_override: selectedClip.caption || "",
      cta_override: selectedClip.cta_suggestion || "",
      thumbnail_text_override: selectedClip.thumbnail_text || "",
      packaging_angle_override: selectedClip.packaging_angle || "",
      trim_start_seconds: selectedClip.trim_start_seconds ?? undefined,
      trim_end_seconds: selectedClip.trim_end_seconds ?? undefined,
    });
    setMessage(null);
  }, [selectedClip]);

  if (!selectedClip) {
    return null;
  }

  async function handleSave() {
    if (readOnly) {
      setMessage(lockedMessage || "Upgrade to edit clip metadata.");
      return;
    }
    const currentClip = selectedClip;
    if (!currentClip) {
      return;
    }
    const clipId = currentClip.record_id || currentClip.clip_id;
    if (!clipId) {
      return;
    }
    setIsSaving(true);
    setMessage(null);
    try {
      await onSave(clipId, {
        hook_override: draft.hook_override || undefined,
        caption_override: draft.caption_override || undefined,
        cta_override: draft.cta_override || undefined,
        thumbnail_text_override: draft.thumbnail_text_override || undefined,
        packaging_angle_override: draft.packaging_angle_override || undefined,
        trim_start_seconds: typeof draft.trim_start_seconds === "number" ? draft.trim_start_seconds : undefined,
        trim_end_seconds: typeof draft.trim_end_seconds === "number" ? draft.trim_end_seconds : undefined,
      });
      setMessage("Clip metadata saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to save clip changes.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="mt-10 hero-card rounded-[34px] p-6 sm:p-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="section-kicker">Clip pack detail</p>
          <h3 className="mt-2 text-3xl font-semibold text-ink">{clipPack.source_title || clipPack.request_id}</h3>
          <p className="mt-2 max-w-3xl text-sm leading-7 text-ink/64">
            Review the ranked pack, then adjust hooks, captions, CTA, and packaging without leaving the browser.
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="secondary-button rounded-full px-4 py-2 text-sm font-medium"
        >
          Close Editor
        </button>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[0.92fr,1.08fr]">
        <div className="space-y-3">
          {clipPack.clips.map((clip) => {
            const clipId = clip.record_id || clip.clip_id || clip.title;
            const selected = clipId === selectedClipId;
            return (
              <button
                key={clipId}
                type="button"
                onClick={() => setSelectedClipId(clipId)}
                className={[
                  "w-full rounded-[24px] border p-4 text-left transition",
                  selected ? "hero-card shadow-glow" : "glass-panel hover:-translate-y-0.5 hover:border-white/16",
                ].join(" ")}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/75">
                    #{clip.rank || clip.best_post_order || 1}
                  </span>
                  <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/75">
                    {clip.start_time || "no start"} - {clip.end_time || "no end"}
                  </span>
                </div>
                <p className="mt-3 text-base font-semibold text-ink">{clip.hook}</p>
                <p className="mt-2 text-sm text-ink/62">{clip.reason || "No rationale stored yet."}</p>
              </button>
            );
          })}
        </div>

        <div className="space-y-5">
          {readOnly ? (
            <div className="rounded-[24px] border border-neonPurple/20 bg-neonPurple/10 p-4 text-sm text-white">
              {lockedMessage || "Editing is locked on the current plan."}
            </div>
          ) : null}

          <div className="metric-tile rounded-[28px] p-5">
            <p className="text-sm font-medium text-ink">Selected clip</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="status-chip status-approved">
                Score {selectedClip.score}
              </span>
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/75">
                {selectedClip.packaging_angle || "angle unset"}
              </span>
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/75">
                {selectedClip.platform_fit || "platform fit pending"}
              </span>
            </div>
            <p className="mt-4 text-sm leading-7 text-ink/64">{selectedClip.reason || "No explanation available for this clip yet."}</p>
          </div>

          <EditorField
            label="Hook"
            value={draft.hook_override || ""}
            disabled={readOnly}
            onChange={(value) => setDraft((current) => ({ ...current, hook_override: value }))}
          />
          <EditorField
            label="Caption"
            value={draft.caption_override || ""}
            multiline
            disabled={readOnly}
            onChange={(value) => setDraft((current) => ({ ...current, caption_override: value }))}
          />
          <div className="grid gap-5 lg:grid-cols-2">
            <EditorField
              label="CTA"
              value={draft.cta_override || ""}
              disabled={readOnly}
              onChange={(value) => setDraft((current) => ({ ...current, cta_override: value }))}
            />
            <EditorField
              label="Thumbnail text"
              value={draft.thumbnail_text_override || ""}
              disabled={readOnly}
              onChange={(value) => setDraft((current) => ({ ...current, thumbnail_text_override: value }))}
            />
          </div>
          <div className="grid gap-5 lg:grid-cols-3">
            <EditorField
              label="Packaging angle"
              value={draft.packaging_angle_override || ""}
              disabled={readOnly}
              onChange={(value) => setDraft((current) => ({ ...current, packaging_angle_override: value }))}
            />
            <NumberField
              label="Trim start (s)"
              value={draft.trim_start_seconds}
              disabled={readOnly}
              onChange={(value) => setDraft((current) => ({ ...current, trim_start_seconds: value }))}
            />
            <NumberField
              label="Trim end (s)"
              value={draft.trim_end_seconds}
              disabled={readOnly}
              onChange={(value) => setDraft((current) => ({ ...current, trim_end_seconds: value }))}
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              className="primary-button rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
            >
              {readOnly ? "Upgrade to edit" : isSaving ? "Saving..." : "Save Clip Changes"}
            </button>
            {selectedClip.preview_url || selectedClip.download_url || selectedClip.edited_clip_url || selectedClip.clip_url ? (
              <a
                href={selectedClip.download_url || selectedClip.preview_url || selectedClip.edited_clip_url || selectedClip.clip_url || "#"}
                target="_blank"
                rel="noreferrer"
                className="secondary-button rounded-full px-5 py-3 text-sm font-medium"
              >
                {selectedClip.download_url ? "Open export" : "Open preview"}
              </a>
            ) : null}
            {message ? <span className="text-sm text-accent">{message}</span> : null}
          </div>
        </div>
      </div>
    </section>
  );
}

function EditorField({
  label,
  value,
  onChange,
  multiline = false,
  disabled = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  multiline?: boolean;
  disabled?: boolean;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-ink/80">{label}</span>
      {multiline ? (
        <textarea
          value={value}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          rows={4}
          className="input-surface min-h-[120px] w-full rounded-[24px] px-4 py-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
        />
      ) : (
        <input
          value={value}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          className="input-surface w-full rounded-[24px] px-4 py-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
        />
      )}
    </label>
  );
}

function NumberField({
  label,
  value,
  onChange,
  disabled = false,
}: {
  label: string;
  value?: number;
  onChange: (value: number | undefined) => void;
  disabled?: boolean;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-ink/80">{label}</span>
      <input
        type="number"
        step="0.1"
        value={typeof value === "number" ? value : ""}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value ? Number(event.target.value) : undefined)}
        className="input-surface w-full rounded-[24px] px-4 py-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
      />
    </label>
  );
}
