/**
 * Demo Mode Data
 * 
 * Pre-generated clips for instant demo experience.
 * No backend required - works 100% client-side.
 */

export const DEMO_INPUT_TEXT = `If you want to grow on social media, you need to stop posting randomly.
Most people post without strategy and wonder why nothing works.
The truth is consistency without direction is useless.
You need a system that tells you exactly what to post and when.
This is that system.`;

export const DEMO_CLIPS = [
  {
    clip_id: "demo_001",
    hook: "Stop posting randomly if you want to grow",
    caption: "This is the system you need.",
    text: "If you want to grow on social media, you need to stop posting randomly. Most people post without strategy and wonder why nothing works.",
    cta: "Follow for the full system",
    thumbnail_text: "STOP",
    score: 0.92,
    why: "High urgency hook with clear problem statement. Strong emotional trigger.",
    rank: 1,
  },
  {
    clip_id: "demo_002",
    hook: "The truth about social media growth",
    caption: "Most people miss this completely.",
    text: "The truth is consistency without direction is useless. You need a system that tells you exactly what to post and when.",
    cta: "Save this for later",
    thumbnail_text: "TRUTH",
    score: 0.85,
    why: "Reveals hidden insight that challenges common belief. Creates curiosity gap.",
    rank: 2,
  },
  {
    clip_id: "demo_003",
    hook: "This is the system that actually works",
    caption: "Watch this twice.",
    text: "You need a system that tells you exactly what to post and when. This is that system.",
    cta: "Comment SYSTEM for details",
    thumbnail_text: "SYSTEM",
    score: 0.78,
    why: "Clear solution presentation with actionable framing. Direct call to action.",
    rank: 3,
  },
];

export type DemoClip = typeof DEMO_CLIPS[0];

/**
 * Load demo clips instantly - no backend required
 */
export function loadDemoClips() {
  return {
    job_id: "demo_job",
    status: "completed",
    clips: DEMO_CLIPS.map(clip => ({
      clip_id: clip.clip_id,
      title: clip.hook,
      hook: clip.hook,
      caption: clip.caption,
      text: clip.text,
      ai_score: clip.score,
      why_this_matters: clip.why,
      cta: clip.cta,
      thumbnail_text: clip.thumbnail_text,
      duration_seconds: 20,
      render_status: "strategy_only",
      original_vertical_url: undefined,
      vertical_with_captions_url: undefined,
    })),
    clips_summary: DEMO_CLIPS.map(clip => ({
      clip_id: clip.clip_id,
      title: clip.hook,
      duration_seconds: 20,
      ai_score: clip.score,
      render_status: "strategy_only",
    })),
    strategy_only: true,
    source_type: "demo",
    generation_method: "demo_mode",
  };
}
