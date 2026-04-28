"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CampaignAssignment,
  CampaignDetail,
  CampaignSummary,
  ClipPackDetail,
  ClipPackSummary,
  PlatformOption,
  SubmissionStatus,
  WorkspaceRole,
} from "../lib/types";

const platforms: PlatformOption[] = ["TikTok", "Instagram Reels", "YouTube Shorts"];
const workspaceViews: Array<{ id: WorkspaceRole; label: string }> = [
  { id: "creator", label: "Creator" },
  { id: "clipper", label: "Clipper" },
  { id: "operator", label: "Operator" },
];

type CampaignPanelProps = {
  userRole?: WorkspaceRole;
  campaigns: CampaignSummary[];
  clipPacks: ClipPackSummary[];
  selectedClipPack: ClipPackDetail | null;
  selectedCampaign: CampaignDetail | null;
  selectedCampaignId?: string | null;
  isLoading?: boolean;
  onCreate: (payload: {
    title: string;
    description?: string;
    allowed_platforms: string[];
    target_angle?: string;
    requirements?: string;
    payout_cents_per_1000_views?: number;
  }) => Promise<void>;
  onOpenCampaign: (campaignId: string) => Promise<void>;
  onUpdateStatus: (campaignId: string, status: string) => Promise<void>;
  onAssign: (campaignId: string, payload: {
    request_id?: string;
    clip_ids?: string[];
    target_platform?: string;
    packaging_angle?: string;
    assignee_role?: string;
    assignee_label?: string;
    note?: string;
    payout_amount_cents?: number;
  }) => Promise<void>;
  onUpdateAssignment: (
    campaignId: string,
    assignmentId: string,
    payload: {
      status?: string;
      assignee_role?: string;
      assignee_label?: string;
      note?: string;
      payout_amount_cents?: number;
    },
  ) => Promise<void>;
};

export function CampaignPanel({
  userRole = "creator",
  campaigns,
  clipPacks,
  selectedClipPack,
  selectedCampaign,
  selectedCampaignId,
  isLoading = false,
  onCreate,
  onOpenCampaign,
  onUpdateStatus,
  onAssign,
  onUpdateAssignment,
}: CampaignPanelProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [targetAngle, setTargetAngle] = useState("");
  const [requirements, setRequirements] = useState("");
  const [payout, setPayout] = useState("");
  const [allowedPlatforms, setAllowedPlatforms] = useState<string[]>(["TikTok"]);
  const [viewMode, setViewMode] = useState<WorkspaceRole>(userRole === "admin" ? "operator" : userRole);
  const [assignmentRequestId, setAssignmentRequestId] = useState("");
  const [assignmentMode, setAssignmentMode] = useState<"clip_pack" | "clip">("clip_pack");
  const [selectedClipIds, setSelectedClipIds] = useState<string[]>([]);
  const [assignmentRole, setAssignmentRole] = useState<"creator" | "clipper" | "admin">("creator");
  const [assignmentLabel, setAssignmentLabel] = useState("");
  const [assignmentPlatform, setAssignmentPlatform] = useState("TikTok");
  const [assignmentAngle, setAssignmentAngle] = useState("");
  const [assignmentNote, setAssignmentNote] = useState("");
  const [assignmentPayout, setAssignmentPayout] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [updatingCampaignId, setUpdatingCampaignId] = useState<string | null>(null);
  const [updatingAssignmentId, setUpdatingAssignmentId] = useState<string | null>(null);

  const orderedCampaigns = useMemo(
    () => [...campaigns].sort((left, right) => (right.created_at || "").localeCompare(left.created_at || "")),
    [campaigns],
  );

  const assignmentSourceOptions = useMemo(() => {
    const options = clipPacks.map((pack) => ({
      requestId: pack.request_id,
      label: pack.source_title || pack.video_url || pack.request_id,
      detail: `${pack.clip_count || 0} clips · ${pack.target_platform || "Clip pack"}`,
    }));
    if (selectedClipPack && !options.some((item) => item.requestId === selectedClipPack.request_id)) {
      options.unshift({
        requestId: selectedClipPack.request_id,
        label: selectedClipPack.source_title || selectedClipPack.request_id,
        detail: `${selectedClipPack.clips.length} clips · open in editor`,
      });
    }
    return options;
  }, [clipPacks, selectedClipPack]);

  const sourceClipOptions = useMemo(() => {
    if (!selectedClipPack || selectedClipPack.request_id !== assignmentRequestId) {
      return [];
    }
    return selectedClipPack.clips.map((clip) => ({
      id: clip.record_id || clip.clip_id || clip.id,
      hook: clip.hook,
      postOrder: clip.best_post_order || clip.rank || 1,
      packagingAngle: clip.packaging_angle || undefined,
    }));
  }, [assignmentRequestId, selectedClipPack]);

  const visibleAssignments = useMemo(() => {
    const assignments = selectedCampaign?.assignments || [];
    if (viewMode === "operator") {
      return assignments;
    }
    return assignments.filter((assignment) => assignment.assignee_role === viewMode);
  }, [selectedCampaign?.assignments, viewMode]);

  useEffect(() => {
    if (!assignmentRequestId && selectedClipPack?.request_id) {
      setAssignmentRequestId(selectedClipPack.request_id);
    }
  }, [assignmentRequestId, selectedClipPack]);

  function togglePlatform(platform: string) {
    setAllowedPlatforms((current) =>
      current.includes(platform) ? current.filter((item) => item !== platform) : [...current, platform],
    );
  }

  function toggleClip(clipId: string) {
    setSelectedClipIds((current) =>
      current.includes(clipId) ? current.filter((item) => item !== clipId) : [...current, clipId],
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

  async function handleAssign() {
    if (!selectedCampaign) {
      setMessage("Select a campaign before assigning work.");
      return;
    }
    if (!assignmentRequestId) {
      setMessage("Choose a clip pack to assign.");
      return;
    }
    if (assignmentMode === "clip" && !selectedClipIds.length) {
      setMessage("Open a clip pack and select at least one clip.");
      return;
    }

    setIsSaving(true);
    setMessage(null);
    try {
      await onAssign(selectedCampaign.campaign.id, {
        request_id: assignmentRequestId,
        clip_ids: assignmentMode === "clip" ? selectedClipIds : [],
        target_platform: assignmentPlatform || undefined,
        packaging_angle: assignmentAngle.trim() || undefined,
        assignee_role: assignmentRole,
        assignee_label: assignmentLabel.trim() || undefined,
        note: assignmentNote.trim() || undefined,
        payout_amount_cents: assignmentPayout ? Number(assignmentPayout) : undefined,
      });
      setSelectedClipIds([]);
      setAssignmentLabel("");
      setAssignmentNote("");
      setAssignmentPayout("");
      setAssignmentMode("clip_pack");
      setMessage("Assignment created.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create assignment.");
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

  async function advanceAssignment(assignment: CampaignAssignment, status: SubmissionStatus) {
    if (!selectedCampaign) {
      return;
    }
    setUpdatingAssignmentId(assignment.id);
    setMessage(null);
    try {
      await onUpdateAssignment(selectedCampaign.campaign.id, assignment.id, { status });
      setMessage(`Assignment moved to ${status}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to update assignment.");
    } finally {
      setUpdatingAssignmentId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-[0.92fr,1.08fr]">
        <div className="hero-card rounded-[32px] p-6 sm:p-8">
          <p className="section-kicker">Campaigns</p>
          <h3 className="mt-2 text-3xl font-semibold text-ink">Turn outputs into managed workflows</h3>
          <p className="mt-4 text-sm leading-7 text-ink/64">
            Build the brief, assign full packs or selected clips, then move each asset through manual submission and payout-readiness review.
          </p>

          <div className="mt-6 space-y-5">
            <Field label="Campaign title" value={title} onChange={setTitle} placeholder="May founder content sprint" />
            <Field label="Target angle" value={targetAngle} onChange={setTargetAngle} placeholder="curiosity, authority, value" />
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
              placeholder="Posting rules, disclosure notes, performance expectations."
            />

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-ink/80">Payout reference per 1,000 views (cents)</span>
              <input
                type="number"
                min="0"
                value={payout}
                onChange={(event) => setPayout(event.target.value)}
                className="input-surface w-full rounded-[24px] px-4 py-3 text-sm"
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
                        active ? "border-accent/30 bg-accent/10 text-accent" : "border-white/10 bg-white/[0.05] text-ink/72",
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
                className="primary-button rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isSaving ? "Creating..." : "Create campaign"}
              </button>
              {message ? <span className="text-sm text-accent">{message}</span> : null}
            </div>
          </div>
        </div>

        <div className="glass-panel rounded-[32px] p-6 sm:p-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="section-kicker">Campaign inventory</p>
              <h3 className="mt-2 text-2xl font-semibold text-ink">Live workflow state</h3>
            </div>
            <span className={[
              "rounded-full border px-4 py-2 text-sm font-semibold",
              campaigns.length > 0
                ? "border-accent/22 bg-accent/[0.07] text-accent"
                : "border-white/10 bg-white/[0.05] text-ink/72",
            ].join(" ")}>
              {campaigns.length} {campaigns.length === 1 ? "campaign" : "campaigns"}
            </span>
          </div>

          <div className="mt-6 space-y-3">
            {orderedCampaigns.length ? (
              orderedCampaigns.map((campaign) => {
                const selected = campaign.id === selectedCampaignId;
                const summary = campaign.submission_summary;
                return (
                  <button
                    key={campaign.id}
                    type="button"
                    onClick={() => void onOpenCampaign(campaign.id)}
                    className={[
                      "w-full rounded-[24px] border p-5 text-left transition duration-200",
                      selected ? "hero-card shadow-glow" : "glass-panel hover:-translate-y-0.5 hover:border-white/16 hover:shadow-card",
                    ].join(" ")}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={["status-chip", campaignStatusClass(campaign.status)].join(" ")}>{campaign.status}</span>
                      {campaign.target_angle ? (
                        <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/72">
                          {campaign.target_angle}
                        </span>
                      ) : null}
                      {selected ? <span className="status-chip status-ready">Selected</span> : null}
                    </div>
                    <p className="mt-3 text-lg font-semibold text-ink">{campaign.title || campaign.name || "Campaign"}</p>
                    <p className="mt-2 text-sm leading-7 text-ink/62">
                      {campaign.description || "No description yet."}
                    </p>
                    <p className="mt-3 text-xs uppercase tracking-[0.22em] text-muted">
                      {summary?.total_assignments || 0} assignments · {summary?.status_counts?.submitted || 0} submitted · $
                      {(((summary?.eligible_payout_cents || 0) as number) / 100).toFixed(2)} eligible
                    </p>
                  </button>
                );
              })
            ) : (
              <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-6">
                <p className="text-sm font-medium text-ink/72">No campaigns yet</p>
                <p className="mt-2 text-sm leading-7 text-ink/46">
                  Create a campaign above to turn clip output into a real operating workflow with briefs, assignments, and manual payout readiness.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="rounded-[24px] border border-white/10 bg-white/[0.03] px-5 py-6">
          <div className="flex items-center gap-3">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/10 border-t-accent" />
            <span className="text-sm text-ink/70">Loading campaign detail...</span>
          </div>
        </div>
      ) : null}

      {selectedCampaign ? (
        <div className="grid gap-6 xl:grid-cols-[0.96fr,1.04fr]">
          <div className="glass-panel rounded-[32px] p-6 sm:p-8">
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-muted">Selected campaign</p>
                <h3 className="mt-2 text-3xl font-semibold text-ink">{selectedCampaign.campaign.title || "Campaign"}</h3>
                <p className="mt-4 text-sm leading-7 text-ink/64">
                  Assign a whole pack or cherry-pick clips. Submission and payout readiness will stay attached to each assignment.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {["active", "paused", "completed"].map((status) => (
                  <button
                    key={status}
                    type="button"
                    disabled={updatingCampaignId === selectedCampaign.campaign.id || selectedCampaign.campaign.status === status}
                    onClick={() => updateStatus(selectedCampaign.campaign.id, status)}
                    className="secondary-button rounded-full px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {selectedCampaign.campaign.status === status ? `Current: ${status}` : `Set ${status}`}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <SummaryMetric label="Assignments" value={String(selectedCampaign.submission_summary.total_assignments)} />
              <SummaryMetric label="Submitted" value={String(selectedCampaign.submission_summary.status_counts.submitted || 0)} />
              <SummaryMetric label="Eligible payout" value={`$${(selectedCampaign.submission_summary.eligible_payout_cents / 100).toFixed(2)}`} />
            </div>

            <div className="mt-6 space-y-4 rounded-[28px] border border-white/10 bg-white/[0.03] p-5">
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => setAssignmentMode("clip_pack")}
                  className={[
                    "rounded-full border px-4 py-2 text-sm transition",
                    assignmentMode === "clip_pack" ? "border-accent/30 bg-accent/10 text-accent" : "border-white/10 bg-white/[0.05] text-ink/72",
                  ].join(" ")}
                >
                  Assign clip pack
                </button>
                <button
                  type="button"
                  onClick={() => setAssignmentMode("clip")}
                  className={[
                    "rounded-full border px-4 py-2 text-sm transition",
                    assignmentMode === "clip" ? "border-accent/30 bg-accent/10 text-accent" : "border-white/10 bg-white/[0.05] text-ink/72",
                  ].join(" ")}
                >
                  Assign selected clips
                </button>
              </div>

              <label className="block">
                <span className="mb-2 block text-sm font-medium text-ink/80">Source clip pack</span>
                <select
                  value={assignmentRequestId}
                  onChange={(event) => {
                    setAssignmentRequestId(event.target.value);
                    setSelectedClipIds([]);
                  }}
                  className="input-surface w-full rounded-[24px] px-4 py-3 text-sm"
                >
                  <option value="" className="bg-slate-950">
                    Select a saved clip pack
                  </option>
                  {assignmentSourceOptions.map((option) => (
                    <option key={option.requestId} value={option.requestId} className="bg-slate-950">
                      {option.label}
                    </option>
                  ))}
                </select>
                {assignmentRequestId ? (
                  <p className="mt-2 text-sm text-ink/60">
                    {assignmentSourceOptions.find((item) => item.requestId === assignmentRequestId)?.detail}
                  </p>
                ) : null}
              </label>

              {assignmentMode === "clip" ? (
                <div>
                  <p className="mb-3 text-sm font-medium text-ink/80">Select clips</p>
                  {sourceClipOptions.length ? (
                    <div className="space-y-3">
                      {sourceClipOptions.map((clip) => {
                        const active = selectedClipIds.includes(clip.id);
                        return (
                          <label
                            key={clip.id}
                            className={[
                              "flex cursor-pointer items-start gap-3 rounded-[24px] border p-4 transition",
                              active ? "border-accent/30 bg-accent/10" : "border-white/10 bg-white/[0.03]",
                            ].join(" ")}
                          >
                            <input
                              type="checkbox"
                              checked={active}
                              onChange={() => toggleClip(clip.id)}
                              className="mt-1 h-4 w-4 accent-cyan-400"
                            />
                            <span className="text-sm leading-7 text-ink/76">
                              <span className="block font-medium text-ink">#{clip.postOrder} {clip.hook}</span>
                              <span className="block text-xs text-muted">{clip.packagingAngle || "angle pending"}</span>
                            </span>
                          </label>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4 text-sm text-ink/62">
                      Open a clip pack in History first if you want to assign individual clips.
                    </div>
                  )}
                </div>
              ) : null}

              <div className="grid gap-4 md:grid-cols-2">
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-ink/80">Assign to</span>
                  <select
                  value={assignmentRole}
                  onChange={(event) => setAssignmentRole(event.target.value as "creator" | "clipper" | "admin")}
                    className="input-surface w-full rounded-[24px] px-4 py-3 text-sm"
                  >
                    <option value="creator" className="bg-slate-950">Creator</option>
                    <option value="clipper" className="bg-slate-950">Clipper</option>
                    <option value="admin" className="bg-slate-950">Operator</option>
                  </select>
                </label>
                <Field label="Assignee label" value={assignmentLabel} onChange={setAssignmentLabel} placeholder="@clipper-name or internal owner" />
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-ink/80">Target platform</span>
                  <select
                  value={assignmentPlatform}
                  onChange={(event) => setAssignmentPlatform(event.target.value)}
                    className="input-surface w-full rounded-[24px] px-4 py-3 text-sm"
                  >
                    {platforms.map((platform) => (
                      <option key={platform} value={platform} className="bg-slate-950">
                        {platform}
                      </option>
                    ))}
                  </select>
                </label>
                <Field label="Packaging angle" value={assignmentAngle} onChange={setAssignmentAngle} placeholder="curiosity" />
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-ink/80">Payout reference (cents)</span>
                  <input
                    type="number"
                    min="0"
                    value={assignmentPayout}
                    onChange={(event) => setAssignmentPayout(event.target.value)}
                    className="input-surface w-full rounded-[24px] px-4 py-3 text-sm"
                  />
                </label>
              </div>

              <Field
                label="Assignment note"
                value={assignmentNote}
                onChange={setAssignmentNote}
                multiline
                placeholder="Context for the creator, clipper, or operator reviewing this asset."
              />

              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  disabled={isSaving}
                  onClick={handleAssign}
                  className="primary-button rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isSaving ? "Assigning..." : "Create assignment"}
                </button>
                <span className="text-sm text-ink/56">
                  {assignmentMode === "clip_pack" ? "Use clip-pack assignments for broad briefs." : "Use clip assignments for operator-level workflow control."}
                </span>
              </div>
            </div>
          </div>

          <div className="glass-panel rounded-[32px] p-6 sm:p-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-muted">Submission flow</p>
                <h3 className="mt-2 text-2xl font-semibold text-ink">Assignments, review, and payout readiness</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {workspaceViews.map((view) => (
                  <button
                    key={view.id}
                    type="button"
                    onClick={() => setViewMode(view.id)}
                    className={[
                      "rounded-full border px-4 py-2 text-sm transition",
                      viewMode === view.id ? "border-accent/30 bg-accent/10 text-accent" : "border-white/10 bg-white/[0.05] text-ink/72",
                    ].join(" ")}
                  >
                    {view.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-6 space-y-3">
              {visibleAssignments.length ? (
                visibleAssignments.map((assignment) => (
                  <AssignmentCard
                    key={assignment.id}
                    assignment={assignment}
                    viewMode={viewMode}
                    isUpdating={updatingAssignmentId === assignment.id}
                    onAdvance={(status) => advanceAssignment(assignment, status)}
                  />
                ))
              ) : (
                <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4 text-sm text-ink/62">
                  No assignments visible for the current view yet.
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function SummaryMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-tile rounded-[24px] p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-muted">{label}</p>
      <p className="mt-3 text-2xl font-semibold text-ink">{value}</p>
    </div>
  );
}

function AssignmentCard({
  assignment,
  viewMode,
  isUpdating,
  onAdvance,
}: {
  assignment: CampaignAssignment;
  viewMode: WorkspaceRole;
  isUpdating: boolean;
  onAdvance: (status: SubmissionStatus) => void;
}) {
  const actions = availableActionsFor(assignment.status, viewMode);

  return (
    <div className="metric-tile rounded-[24px] p-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/72">{assignment.assignment_kind}</span>
        <span className={["status-chip", submissionStatusClass(assignment.status)].join(" ")}>{assignment.status}</span>
        <span className={["status-chip", payoutStateClass(assignment.payout_state)].join(" ")}>{assignment.payout_state}</span>
        <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs text-ink/72">{assignment.assignee_role}</span>
      </div>

      <p className="mt-3 text-lg font-semibold text-ink">{assignment.title || assignment.hook || assignment.request_id || assignment.id}</p>
      <p className="mt-2 text-sm leading-7 text-ink/62">{assignment.hook || assignment.note || "Assignment detail pending."}</p>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <AssignmentDetail label="Target platform" value={assignment.target_platform || "Not set"} />
        <AssignmentDetail label="Packaging angle" value={assignment.packaging_angle || "Not set"} />
        <AssignmentDetail label="Assignee" value={assignment.assignee_label || assignment.assignee_role} />
        <AssignmentDetail label="Payout amount" value={`$${((assignment.payout_amount_cents || 0) / 100).toFixed(2)}`} />
      </div>

      {actions.length ? (
        <div className="mt-5 flex flex-wrap gap-3">
          {actions.map((status) => (
            <button
              key={status}
              type="button"
              disabled={isUpdating}
              onClick={() => onAdvance(status)}
              className="secondary-button rounded-full px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isUpdating ? "Updating..." : labelForStatusAction(status)}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function AssignmentDetail({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric-tile rounded-[20px] px-4 py-3">
      <p className="text-xs uppercase tracking-[0.18em] text-muted">{label}</p>
      <p className="mt-2 text-sm font-medium text-ink">{value}</p>
    </div>
  );
}

function campaignStatusClass(status: string) {
  switch (status) {
    case "active":
      return "status-ready";
    case "completed":
      return "status-paid";
    case "paused":
      return "status-draft";
    default:
      return "status-draft";
  }
}

function submissionStatusClass(status: SubmissionStatus) {
  switch (status) {
    case "ready":
      return "status-ready";
    case "submitted":
      return "status-submitted";
    case "approved":
      return "status-approved";
    case "rejected":
      return "status-rejected";
    case "paid":
      return "status-paid";
    default:
      return "status-draft";
  }
}

function payoutStateClass(state: string) {
  switch (state) {
    case "eligible":
      return "status-approved";
    case "pending":
      return "status-submitted";
    case "paid":
      return "status-paid";
    default:
      return "status-draft";
  }
}

function availableActionsFor(status: SubmissionStatus, viewMode: WorkspaceRole): SubmissionStatus[] {
  if (viewMode === "creator") {
    if (status === "draft") return ["ready"];
    if (status === "ready") return ["submitted"];
    return [];
  }
  if (viewMode === "clipper") {
    if (status === "ready") return ["submitted"];
    if (status === "rejected") return ["ready"];
    return [];
  }
  if (status === "draft") return ["ready"];
  if (status === "ready") return ["submitted"];
  if (status === "submitted") return ["approved", "rejected"];
  if (status === "approved") return ["paid"];
  if (status === "rejected") return ["ready"];
  return [];
}

function labelForStatusAction(status: SubmissionStatus) {
  switch (status) {
    case "ready":
      return "Mark ready";
    case "submitted":
      return "Submit";
    case "approved":
      return "Approve";
    case "rejected":
      return "Reject";
    case "paid":
      return "Mark paid";
    default:
      return status;
  }
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
          className="input-surface min-h-[110px] w-full rounded-[24px] px-4 py-3 text-sm"
        />
      ) : (
        <input
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          className="input-surface w-full rounded-[24px] px-4 py-3 text-sm"
        />
      )}
    </label>
  );
}
