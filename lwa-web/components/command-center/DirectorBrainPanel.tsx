"use client";

import { useState } from "react";
import {
  scoreDirectorBrain,
  rankDirectorBrain,
  learnDirectorBrain,
  getDirectorBrainStatus,
  DirectorBrainContentType,
  DirectorBrainGoal,
  DirectorBrainScoreResponse,
  DirectorBrainStatusResponse,
} from "../../lib/api";

type Tab = "score" | "rank" | "learn" | "status";

export default function DirectorBrainPanel() {
  const [activeTab, setActiveTab] = useState<Tab>("score");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [scoreText, setScoreText] = useState("");
  const [contentType, setContentType] = useState<DirectorBrainContentType>("hook");
  const [goal, setGoal] = useState<DirectorBrainGoal>("balanced");
  const [platform, setPlatform] = useState("");
  const [scoreResult, setScoreResult] = useState<DirectorBrainScoreResponse | null>(null);

  const [rankInput, setRankInput] = useState("");
  const [rankResults, setRankResults] = useState<DirectorBrainScoreResponse[] | null>(null);

  const [learnText, setLearnText] = useState("");
  const [learnLabel, setLearnLabel] = useState<"winning" | "rejected" | "neutral">("neutral");
  const [learnMessage, setLearnMessage] = useState<string | null>(null);

  const [status, setStatus] = useState<DirectorBrainStatusResponse | null>(null);

  async function handleScore() {
    if (!scoreText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await scoreDirectorBrain({
        text: scoreText,
        content_type: contentType,
        goal,
        platform: platform || null,
      });
      setScoreResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Score failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleRank() {
    const candidates = rankInput.split("\n").map((s) => s.trim()).filter(Boolean);
    if (candidates.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const result = await rankDirectorBrain({
        candidates,
        content_type: contentType,
        goal,
        platform: platform || null,
      });
      setRankResults(result.ranked_candidates || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Rank failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleLearn() {
    if (!learnText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await learnDirectorBrain({
        text: learnText,
        label: learnLabel,
        signal_type: "manual_feedback",
        weight: 1.0,
      });
      setLearnMessage(result.message || "Learning event stored.");
      setTimeout(() => setLearnMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Learn failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleStatus() {
    setLoading(true);
    setError(null);
    try {
      const result = await getDirectorBrainStatus();
      setStatus(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Status fetch failed");
    } finally {
      setLoading(false);
    }
  }

  const scoreColor = (score: number) => {
    if (score >= 0.84) return "text-emerald-400";
    if (score >= 0.70) return "text-[var(--gold)]";
    if (score >= 0.55) return "text-amber-400";
    return "text-red-400";
  };

  const scoreBg = (score: number) => {
    if (score >= 0.84) return "bg-emerald-400/10 border-emerald-400/20";
    if (score >= 0.70) return "bg-[var(--gold-dim)] border-[var(--gold-border)]";
    if (score >= 0.55) return "bg-amber-400/10 border-amber-400/20";
    return "bg-red-400/10 border-red-400/20";
  };

  return (
    <div className="rounded-[28px] border border-[var(--divider)] bg-[var(--surface-soft)] p-6 shadow-card">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-ink">Director Brain</h2>
          <p className="text-sm text-muted">Explainable ML scoring for hooks, captions, and offers</p>
        </div>
        <span className="rounded-full bg-violet-400/10 px-3 py-1 text-xs font-medium text-violet-300">
          Heuristic v0
        </span>
      </div>

      <div className="mb-6 flex gap-2">
        {(["score", "rank", "learn", "status"] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={[
              "rounded-full px-4 py-2 text-sm font-medium transition",
              activeTab === tab
                ? "bg-[var(--gold-dim)] text-[var(--gold)] border border-[var(--gold-border)]"
                : "bg-white/[0.05] text-ink/70 hover:bg-white/[0.08]",
            ].join(" ")}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-4 rounded-[18px] border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-200">
          {error}
        </div>
      )}

      {activeTab === "score" && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="mb-2 block text-xs uppercase tracking-wider text-muted">Content Type</label>
              <select
                value={contentType}
                onChange={(e) => setContentType(e.target.value as DirectorBrainContentType)}
                className="w-full rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] px-4 py-2 text-sm text-ink"
              >
                <option value="hook">Hook</option>
                <option value="caption">Caption</option>
                <option value="title">Title</option>
                <option value="offer">Offer</option>
                <option value="description">Description</option>
                <option value="clip_summary">Clip Summary</option>
                <option value="opportunity">Opportunity</option>
                <option value="campaign_angle">Campaign Angle</option>
              </select>
            </div>
            <div>
              <label className="mb-2 block text-xs uppercase tracking-wider text-muted">Goal</label>
              <select
                value={goal}
                onChange={(e) => setGoal(e.target.value as DirectorBrainGoal)}
                className="w-full rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] px-4 py-2 text-sm text-ink"
              >
                <option value="balanced">Balanced</option>
                <option value="viral">Viral</option>
                <option value="engagement">Engagement</option>
                <option value="conversion">Conversion</option>
                <option value="personal">Personal Style</option>
              </select>
            </div>
            <div>
              <label className="mb-2 block text-xs uppercase tracking-wider text-muted">Platform (optional)</label>
              <input
                type="text"
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                placeholder="tiktok, instagram, youtube..."
                className="w-full rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] px-4 py-2 text-sm text-ink placeholder:text-muted"
              />
            </div>
          </div>

          <textarea
            value={scoreText}
            onChange={(e) => setScoreText(e.target.value)}
            placeholder="Enter your hook, caption, or offer text to score..."
            rows={4}
            className="w-full rounded-[18px] border border-[var(--divider)] bg-[var(--surface-veil)] px-4 py-3 text-sm text-ink placeholder:text-muted"
          />

          <button
            onClick={handleScore}
            disabled={loading || !scoreText.trim()}
            className="primary-button rounded-full px-6 py-2 text-sm font-semibold disabled:opacity-50"
          >
            {loading ? "Scoring..." : "Score Content"}
          </button>

          {scoreResult && (
            <div className={`mt-4 rounded-[22px] border p-5 ${scoreBg(scoreResult.score)}`}>
              <div className="mb-4 flex items-center justify-between">
                <span className="text-sm font-medium text-ink/70">Overall Score</span>
                <span className={`text-3xl font-bold ${scoreColor(scoreResult.score)}`}>
                  {Math.round(scoreResult.score * 100)}%
                </span>
              </div>

              <div className="mb-4 grid gap-2 sm:grid-cols-2">
                <div className="rounded-[14px] bg-white/[0.05] p-3">
                  <span className="text-xs text-muted">Viral Hook</span>
                  <div className="mt-1 text-lg font-semibold text-ink">
                    {Math.round(scoreResult.component_scores.viral_hook_strength * 100)}%
                  </div>
                </div>
                <div className="rounded-[14px] bg-white/[0.05] p-3">
                  <span className="text-xs text-muted">Retention</span>
                  <div className="mt-1 text-lg font-semibold text-ink">
                    {Math.round(scoreResult.component_scores.retention_engagement * 100)}%
                  </div>
                </div>
                <div className="rounded-[14px] bg-white/[0.05] p-3">
                  <span className="text-xs text-muted">Conversion</span>
                  <div className="mt-1 text-lg font-semibold text-ink">
                    {Math.round(scoreResult.component_scores.conversion_offer_fit * 100)}%
                  </div>
                </div>
                <div className="rounded-[14px] bg-white/[0.05] p-3">
                  <span className="text-xs text-muted">Style Match</span>
                  <div className="mt-1 text-lg font-semibold text-ink">
                    {Math.round(scoreResult.component_scores.user_style_preference * 100)}%
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium text-ink">{scoreResult.lee_wuh_recommendation}</p>
                <p className="text-sm text-ink/70">{scoreResult.suggested_improvement}</p>
              </div>

              {scoreResult.reasons.length > 0 && (
                <div className="mt-4">
                  <p className="mb-2 text-xs uppercase tracking-wider text-muted">Why this score</p>
                  <ul className="space-y-1">
                    {scoreResult.reasons.map((reason, i) => (
                      <li key={i} className="text-sm text-ink/70">• {reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === "rank" && (
        <div className="space-y-4">
          <p className="text-sm text-muted">Enter multiple candidates (one per line) to rank them</p>
          <textarea
            value={rankInput}
            onChange={(e) => setRankInput(e.target.value)}
            placeholder="Hook option 1...&#10;Hook option 2...&#10;Hook option 3..."
            rows={6}
            className="w-full rounded-[18px] border border-[var(--divider)] bg-[var(--surface-veil)] px-4 py-3 text-sm text-ink placeholder:text-muted"
          />
          <button
            onClick={handleRank}
            disabled={loading || !rankInput.trim()}
            className="primary-button rounded-full px-6 py-2 text-sm font-semibold disabled:opacity-50"
          >
            {loading ? "Ranking..." : "Rank Candidates"}
          </button>

          {rankResults && rankResults.length > 0 && (
            <div className="mt-4 space-y-2">
              {rankResults.map((result, i) => (
                <div
                  key={i}
                  className={`rounded-[18px] border p-4 ${i === 0 ? "border-[var(--gold-border)] bg-[var(--gold-dim)]" : "border-[var(--divider)] bg-[var(--surface-veil)]"}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-white/[0.1] text-sm font-bold text-ink">
                        #{i + 1}
                      </span>
                      <span className="text-sm text-ink">{result.text.substring(0, 60)}...</span>
                    </div>
                    <span className={`text-lg font-bold ${scoreColor(result.score)}`}>
                      {Math.round(result.score * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "learn" && (
        <div className="space-y-4">
          <p className="text-sm text-muted">Submit feedback to improve future recommendations</p>
          <textarea
            value={learnText}
            onChange={(e) => setLearnText(e.target.value)}
            placeholder="Enter text that was approved or rejected..."
            rows={4}
            className="w-full rounded-[18px] border border-[var(--divider)] bg-[var(--surface-veil)] px-4 py-3 text-sm text-ink placeholder:text-muted"
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-2 block text-xs uppercase tracking-wider text-muted">Label</label>
              <select
                value={learnLabel}
                onChange={(e) => setLearnLabel(e.target.value as "winning" | "rejected" | "neutral")}
                className="w-full rounded-[14px] border border-[var(--divider)] bg-[var(--surface-veil)] px-4 py-2 text-sm text-ink"
              >
                <option value="winning">Winning</option>
                <option value="rejected">Rejected</option>
                <option value="neutral">Neutral</option>
              </select>
            </div>
          </div>
          <button
            onClick={handleLearn}
            disabled={loading || !learnText.trim()}
            className="primary-button rounded-full px-6 py-2 text-sm font-semibold disabled:opacity-50"
          >
            {loading ? "Learning..." : "Submit Feedback"}
          </button>
          {learnMessage && (
            <div className="rounded-[14px] bg-emerald-400/10 p-3 text-sm text-emerald-300">
              {learnMessage}
            </div>
          )}
        </div>
      )}

      {activeTab === "status" && (
        <div className="space-y-4">
          <button
            onClick={handleStatus}
            disabled={loading}
            className="secondary-button rounded-full px-6 py-2 text-sm font-semibold disabled:opacity-50"
          >
            {loading ? "Loading..." : "Refresh Status"}
          </button>

          {status && (
            <div className="rounded-[22px] border border-[var(--divider)] bg-[var(--surface-veil)] p-5">
              <div className="mb-4 grid gap-4 sm:grid-cols-2">
                <div>
                  <span className="text-xs text-muted">Mode</span>
                  <p className="text-lg font-semibold text-ink">{status.mode}</p>
                </div>
                <div>
                  <span className="text-xs text-muted">Version</span>
                  <p className="text-lg font-semibold text-ink">{status.algorithm_version}</p>
                </div>
                <div>
                  <span className="text-xs text-muted">Learning Events</span>
                  <p className="text-lg font-semibold text-ink">{status.learning_event_count}</p>
                </div>
                <div>
                  <span className="text-xs text-muted">Live Providers</span>
                  <p className="text-lg font-semibold text-ink">
                    {status.live_paid_providers_enabled ? "Enabled" : "Disabled"}
                  </p>
                </div>
              </div>

              <div className="mb-4">
                <span className="text-xs text-muted">Scoring Weights</span>
                <div className="mt-2 grid gap-2 sm:grid-cols-2">
                  {Object.entries(status.weights).map(([key, value]) => (
                    <div key={key} className="flex justify-between rounded-[10px] bg-white/[0.05] px-3 py-2">
                      <span className="text-sm text-ink/70">{key.replace(/_/g, " ")}</span>
                      <span className="text-sm font-medium text-ink">{Math.round(value * 100)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-xs text-muted">Supported Content Types</span>
                <div className="mt-2 flex flex-wrap gap-2">
                  {status.supported_content_types.map((type) => (
                    <span key={type} className="rounded-full bg-white/[0.05] px-3 py-1 text-xs text-ink/70">
                      {type}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
