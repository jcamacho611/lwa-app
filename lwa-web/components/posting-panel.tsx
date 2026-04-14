"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ClipPackDetail, PostingConnection, ScheduledPost } from "../lib/types";

type PostingPanelProps = {
  connections: PostingConnection[];
  scheduledPosts: ScheduledPost[];
  selectedClipPack: ClipPackDetail | null;
  onCreateConnection: (payload: { provider: string; account_label?: string }) => Promise<void>;
  onCreateScheduledPost: (payload: {
    clip_id: string;
    provider: string;
    caption?: string;
    scheduled_for?: string;
  }) => Promise<void>;
  onUpdateScheduledPost: (postId: string, payload: { status?: string; caption?: string; scheduled_for?: string }) => Promise<void>;
};

const providers = ["TikTok", "Instagram", "YouTube Shorts"];

export function PostingPanel({
  connections,
  scheduledPosts,
  selectedClipPack,
  onCreateConnection,
  onCreateScheduledPost,
  onUpdateScheduledPost,
}: PostingPanelProps) {
  const [provider, setProvider] = useState("TikTok");
  const [accountLabel, setAccountLabel] = useState("");
  const [postProvider, setPostProvider] = useState("TikTok");
  const [selectedClipId, setSelectedClipId] = useState("");
  const [caption, setCaption] = useState("");
  const [scheduledFor, setScheduledFor] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [isSavingConnection, setIsSavingConnection] = useState(false);
  const [isSavingPost, setIsSavingPost] = useState(false);
  const [updatingPostId, setUpdatingPostId] = useState<string | null>(null);

  const availableClips = useMemo(
    () =>
      (selectedClipPack?.clips || [])
        .filter((clip) => clip.record_id)
        .map((clip) => ({
          id: clip.record_id as string,
          label: `${clip.rank || clip.best_post_order || 1}. ${clip.hook}`,
          caption: clip.caption,
        })),
    [selectedClipPack],
  );

  async function handleCreateConnection() {
    setIsSavingConnection(true);
    setMessage(null);
    try {
      await onCreateConnection({
        provider,
        account_label: accountLabel.trim() || undefined,
      });
      setAccountLabel("");
      setMessage("Posting connection created.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create posting connection.");
    } finally {
      setIsSavingConnection(false);
    }
  }

  async function handleCreateScheduledPost() {
    if (!selectedClipId) {
      setMessage("Open a clip pack in History, then choose a clip to queue.");
      return;
    }

    setIsSavingPost(true);
    setMessage(null);
    try {
      await onCreateScheduledPost({
        clip_id: selectedClipId,
        provider: postProvider,
        caption: caption.trim() || undefined,
        scheduled_for: scheduledFor || undefined,
      });
      setCaption("");
      setScheduledFor("");
      setMessage("Scheduled post created.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to create scheduled post.");
    } finally {
      setIsSavingPost(false);
    }
  }

  async function updateStatus(postId: string, status: string) {
    setUpdatingPostId(postId);
    setMessage(null);
    try {
      await onUpdateScheduledPost(postId, { status });
      setMessage(`Scheduled post moved to ${status}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to update scheduled post.");
    } finally {
      setUpdatingPostId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-[0.92fr,1.08fr]">
        <div className="glass-panel rounded-[32px] p-6 sm:p-8">
        <p className="text-xs uppercase tracking-[0.24em] text-muted">Connections</p>
        <h3 className="mt-2 text-3xl font-semibold text-ink">Build posting groundwork</h3>
        <p className="mt-4 text-sm leading-7 text-ink/64">
            Prepare the accounts and queue state you need so the best clips are ready to move.
        </p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-ink/80">Provider</span>
              <select
                value={provider}
                onChange={(event) => setProvider(event.target.value)}
                className="w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition focus:border-accent/40"
              >
                {providers.map((item) => (
                  <option key={item} value={item} className="bg-slate-950">
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-ink/80">Account label</span>
              <input
                value={accountLabel}
                onChange={(event) => setAccountLabel(event.target.value)}
                placeholder="@creatorhandle"
                className="w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent/40"
              />
            </label>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={isSavingConnection}
              onClick={handleCreateConnection}
              className="rounded-full bg-gradient-to-r from-accent to-accentSoft px-5 py-3 text-sm font-semibold text-white shadow-glow disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSavingConnection ? "Saving..." : "Add Connection"}
            </button>
            {message ? <span className="text-sm text-accent">{message}</span> : null}
          </div>

          <div className="mt-6 space-y-3">
            {connections.length ? (
              connections.map((connection) => (
                <div key={connection.id} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
                  <p className="text-sm font-medium text-ink">{connection.provider}</p>
                  <p className="mt-1 text-sm text-ink/62">{connection.account_label || "Account label pending"}</p>
                </div>
              ))
            ) : (
              <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4 text-sm text-ink/62">
                No posting connections yet.
              </div>
            )}
          </div>
        </div>

        <div className="glass-panel rounded-[32px] p-6 sm:p-8">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-muted">Queue</p>
              <h3 className="mt-2 text-2xl font-semibold text-ink">Create scheduled posts</h3>
            </div>
            <Link href="/history" className="text-sm font-medium text-accent hover:text-accentSoft">
              Open history
            </Link>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-ink/80">Provider</span>
              <select
                value={postProvider}
                onChange={(event) => setPostProvider(event.target.value)}
                className="w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition focus:border-accent/40"
              >
                {providers.map((item) => (
                  <option key={item} value={item} className="bg-slate-950">
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-ink/80">Clip</span>
              <select
                value={selectedClipId}
                onChange={(event) => {
                  setSelectedClipId(event.target.value);
                  const selectedClip = availableClips.find((clip) => clip.id === event.target.value);
                  if (selectedClip) {
                    setCaption(selectedClip.caption || "");
                  }
                }}
                className="w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition focus:border-accent/40"
              >
                <option value="" className="bg-slate-950">
                  {availableClips.length ? "Select a clip" : "Open a clip pack first"}
                </option>
                {availableClips.map((clip) => (
                  <option key={clip.id} value={clip.id} className="bg-slate-950">
                    {clip.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink/80">Caption</span>
            <textarea
              value={caption}
              onChange={(event) => setCaption(event.target.value)}
              rows={4}
              placeholder="Optional platform-ready caption"
              className="min-h-[110px] w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent/40"
            />
          </label>

          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink/80">Schedule for</span>
            <input
              type="datetime-local"
              value={scheduledFor}
              onChange={(event) => setScheduledFor(event.target.value)}
              className="w-full rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition focus:border-accent/40"
            />
          </label>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={isSavingPost}
              onClick={handleCreateScheduledPost}
              className="rounded-full bg-gradient-to-r from-accent to-accentSoft px-5 py-3 text-sm font-semibold text-white shadow-glow disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSavingPost ? "Queueing..." : "Queue Post"}
            </button>
            {!selectedClipPack ? <span className="text-sm text-amber-300">Open a clip pack from History to target a clip.</span> : null}
          </div>

          <div className="mt-6 space-y-3">
            {scheduledPosts.length ? (
              scheduledPosts.map((post) => (
                <div key={post.id} className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-ink">{post.provider}</p>
                      <p className="mt-1 text-xs text-muted">{post.scheduled_for || post.created_at || "queued now"}</p>
                    </div>
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-ink/72">{post.status}</span>
                  </div>
                  <p className="mt-3 text-sm text-ink/62">{post.caption || "Caption pending."}</p>
                  <div className="mt-4 flex flex-wrap gap-3">
                    {["queued", "published", "failed"].map((status) => (
                      <button
                        key={status}
                        type="button"
                        disabled={updatingPostId === post.id || post.status === status}
                        onClick={() => updateStatus(post.id, status)}
                        className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-ink/80 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {post.status === status ? `Current: ${status}` : `Set ${status}`}
                      </button>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-[24px] border border-white/10 bg-white/[0.03] p-4 text-sm text-ink/62">
                No scheduled posts yet. Queue the first one from a saved clip pack.
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
