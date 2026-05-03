"use client";

import { useEffect, useMemo, useState } from "react";
import {
  DirectorBrainRankResponse,
  DirectorBrainScoreResponse,
  DirectorBrainStatusResponse,
  getDirectorBrainStatus,
  rankDirectorBrainCandidates,
  scoreDirectorBrainText,
  submitDirectorBrainLearningEvent,
} from "../../lib/director-brain-api";

type Goal = "balanced" | "viral" | "engagement" | "conversion" | "personal";
type ContentType = "hook" | "caption" | "title" | "offer" | "description" | "clip_summary" | "opportunity" | "campaign_angle";

const SAMPLE_CANDIDATES = [
  "Stop posting clips in the wrong order.",
  "Nobody is talking about the money hidden inside old content.",
  "This is the exact moment your audience actually cares about.",
].join("\n");

function scorePercent(score?: number) {
  if (typeof score !== "number") return "—";
  return `${Math.round(score * 100)}%`;
}

function componentLabel(key: string) {
  return key
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function DirectorBrainPanel() {
  const [text, setText] = useState("Nobody is talking about the system behind viral clips.");
  const [candidates, setCandidates] = useState(SAMPLE_CANDIDATES);
  const [contentType, setContentType] = useState<ContentType>("hook");
  const [goal, setGoal] = useState<Goal>("balanced");
  const [platform, setPlatform] = useState("tiktok");
  const [status, setStatus] = useState<DirectorBrainStatusResponse | null>(null);
  const [score, setScore] = useState<DirectorBrainScoreResponse | null>(null);
  const [ranking, setRanking] = useState<DirectorBrainRankResponse | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const candidateList = useMemo(
    () => candidates.split("\n").map((item) => item.trim()).filter(Boolean),
    [candidates],
  );

  useEffect(() => {
    getDirectorBrainStatus()
      .then(setStatus)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load Director Brain status."));
  }, []);

  async function handleScore() {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const result = await scoreDirectorBrainText({
        text,
        content_type: contentType,
        platform,
        goal,
        style_memory: {
          approved_hook_patterns: ["nobody is talking about", "watch this before", "stop posting"],
          rejected_hook_patterns: ["you won't believe", "check this out"],
          preferred_words: ["system", "money", "proof", "creator"],
          avoid_words: ["easy", "cheap", "obviously"],
        },
        proof_signals: {
          winning_keywords: ["system", "money", "proof", "order"],
          rejected_keywords: ["generic", "boring"],
        },
      });
      setScore(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Director Brain score failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRank() {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const result = await rankDirectorBrainCandidates({
        candidates: candidateList,
        content_type: contentType,
        platform,
        goal,
        style_memory: {
          approved_hook_patterns: ["nobody is talking about", "watch this before", "stop posting"],
          rejected_hook_patterns: ["you won't believe", "check this out"],
          preferred_words: ["system", "money", "proof", "creator"],
          avoid_words: ["easy", "cheap", "obviously"],
        },
        proof_signals: {
          winning_keywords: ["system", "money", "proof", "order"],
          rejected_keywords: ["generic", "boring"],
        },
      });
      setRanking(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Director Brain ranking failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleLearn(label: "winning" | "rejected" | "neutral") {
    setError(null);
    setMessage(null);
    try {
      const result = await submitDirectorBrainLearningEvent({
        text: score?.text || text,
        label,
        signal_type: label === "winning" ? "save" : label === "rejected" ? "manual_feedback" : "manual_feedback",
        weight: label === "winning" ? 1.25 : 1,
        metadata: {
          source: "command_center_director_brain_panel",
          score: score?.score,
          platform,
          goal,
        },
      });
      setMessage(result.message);
      const nextStatus = await getDirectorBrainStatus();
      setStatus(nextStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Director Brain learning event failed.");
    }
  }

  return (
    <div className="space-y-6">
      <section className="glass-panel rounded-[28px] p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="section-kicker">Director Brain v0</p>
            <h3 className="mt-3 text-2xl font-semibold text-ink">Score the hook before it becomes the clip.</h3>
            <p className="mt-2 max-w-3xl text-sm leading-7 text-ink/62">
              Deterministic scoring for hooks, captions, offers, campaign angles, and opportunity ideas. It is explainable,
              safe, and ready to connect into Proof Vault, Style Memory, Campaign Export, and Generate results.
            </p>
          </div>
          <div className="rounded-2xl border border-ink/10 bg-white/50 p-4 text-sm text-ink/70">
            <p className="font-semibold text-ink">Mode: {status?.mode || "loading"}</p>
            <p className="mt-1">Events learned: {status?.learning_event_count ?? "—"}</p>
            <p className="mt-1">Paid providers: {status?.live_paid_providers_enabled ? "on" : "off"}</p>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1fr_0.9fr]">
        <div className="glass-panel rounded-[28px] p-6">
          <p className="section-kicker">Single score</p>
          <textarea
            value={text}
            onChange={(event) => setText(event.target.value)}
            className="mt-4 min-h-[130px] w-full rounded-[22px] border border-ink/10 bg-white/65 p-4 text-sm leading-6 text-ink outline-none"
            placeholder="Paste a hook, caption, title, offer, clip summary, or campaign angle..."
          />

          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <select
              value={contentType}
              onChange={(event) => setContentType(event.target.value as ContentType)}
              className="rounded-2xl border border-ink/10 bg-white/70 px-4 py-3 text-sm text-ink outline-none"
            >
              <option value="hook">Hook</option>
              <option value="caption">Caption</option>
              <option value="title">Title</option>
              <option value="offer">Offer</option>
              <option value="clip_summary">Clip summary</option>
              <option value="opportunity">Opportunity</option>
              <option value="campaign_angle">Campaign angle</option>
            </select>
            <select
              value={goal}
              onChange={(event) => setGoal(event.target.value as Goal)}
              className="rounded-2xl border border-ink/10 bg-white/70 px-4 py-3 text-sm text-ink outline-none"
            >
              <option value="balanced">Balanced</option>
              <option value="viral">Viral</option>
              <option value="engagement">Engagement</option>
              <option value="conversion">Conversion</option>
              <option value="personal">Personal</option>
            </select>
            <input
              value={platform}
              onChange={(event) => setPlatform(event.target.value)}
              className="rounded-2xl border border-ink/10 bg-white/70 px-4 py-3 text-sm text-ink outline-none"
              placeholder="tiktok, instagram, youtube..."
            />
          </div>

          <div className="mt-4 flex flex-wrap gap-3">
            <button onClick={handleScore} disabled={loading || !text.trim()} className="primary-button rounded-full px-5 py-3 text-sm font-semibold disabled:opacity-50">
              {loading ? "Scoring..." : "Score text"}
            </button>
            <button onClick={() => handleLearn("winning")} disabled={!score} className="secondary-button rounded-full px-5 py-3 text-sm font-semibold disabled:opacity-50">
              Mark winning
            </button>
            <button onClick={() => handleLearn("rejected")} disabled={!score} className="ghost-button rounded-full px-5 py-3 text-sm font-semibold disabled:opacity-50">
              Mark rejected
            </button>
          </div>
        </div>

        <div className="glass-panel rounded-[28px] p-6">
          <p className="section-kicker">Score output</p>
          {score ? (
            <div className="mt-4 space-y-4">
              <div className="rounded-[24px] border border-ink/10 bg-white/65 p-5">
                <p className="text-sm text-ink/50">Overall score</p>
                <p className="mt-2 text-5xl font-semibold text-ink">{scorePercent(score.score)}</p>
                <p className="mt-3 text-sm leading-6 text-ink/70">{score.lee_wuh_recommendation}</p>
              </div>

              <div className="space-y-2">
                {Object.entries(score.component_scores).map(([key, value]) => (
                  <div key={key} className="rounded-2xl border border-ink/10 bg-white/55 p-3">
                    <div className="flex items-center justify-between gap-3 text-sm">
                      <span className="font-medium text-ink">{componentLabel(key)}</span>
                      <span className="text-ink/70">{scorePercent(value)}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="rounded-2xl border border-ink/10 bg-white/55 p-4">
                <p className="text-sm font-semibold text-ink">Reasons</p>
                <ul className="mt-2 space-y-2 text-sm leading-6 text-ink/70">
                  {score.reasons.map((reason) => (
                    <li key={reason}>• {reason}</li>
                  ))}
                </ul>
              </div>

              <div className="rounded-2xl border border-ink/10 bg-white/55 p-4">
                <p className="text-sm font-semibold text-ink">Suggested improvement</p>
                <p className="mt-2 text-sm leading-6 text-ink/70">{score.suggested_improvement}</p>
              </div>
            </div>
          ) : (
            <p className="mt-4 rounded-2xl border border-ink/10 bg-white/55 p-4 text-sm leading-6 text-ink/62">
              Score a hook or campaign angle to see component scores, reasons, and Lee-Wuh's recommendation.
            </p>
          )}
        </div>
      </section>

      <section className="glass-panel rounded-[28px] p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="section-kicker">Candidate ranking</p>
            <h3 className="mt-2 text-xl font-semibold text-ink">Pick the best first post before you render.</h3>
          </div>
          <button onClick={handleRank} disabled={loading || candidateList.length === 0} className="primary-button rounded-full px-5 py-3 text-sm font-semibold disabled:opacity-50">
            Rank candidates
          </button>
        </div>

        <textarea
          value={candidates}
          onChange={(event) => setCandidates(event.target.value)}
          className="mt-4 min-h-[150px] w-full rounded-[22px] border border-ink/10 bg-white/65 p-4 text-sm leading-6 text-ink outline-none"
          placeholder="Add one candidate per line..."
        />

        {ranking?.ranked_candidates?.length ? (
          <div className="mt-5 grid gap-4 lg:grid-cols-3">
            {ranking.ranked_candidates.map((candidate) => (
              <div key={`${candidate.rank}-${candidate.text}`} className="rounded-[24px] border border-ink/10 bg-white/60 p-5">
                <div className="flex items-center justify-between gap-3">
                  <span className="rounded-full bg-ink px-3 py-1 text-xs font-semibold text-white">#{candidate.rank}</span>
                  <span className="text-sm font-semibold text-ink">{scorePercent(candidate.score)}</span>
                </div>
                <p className="mt-4 text-sm font-semibold leading-6 text-ink">{candidate.text}</p>
                <p className="mt-3 text-sm leading-6 text-ink/65">{candidate.lee_wuh_recommendation}</p>
              </div>
            ))}
          </div>
        ) : null}
      </section>

      {(error || message) && (
        <div className={`rounded-[24px] border p-4 text-sm ${error ? "border-red-300 bg-red-50 text-red-700" : "border-emerald-300 bg-emerald-50 text-emerald-700"}`}>
          {error || message}
        </div>
      )}
    </div>
  );
}
