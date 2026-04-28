import type { Metadata } from "next";
import { Logo } from "../components/brand/Logo";
import { buildPageMetadata } from "../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Any-Source AI Content Engine",
  description: "Give LWA video, audio, streams, prompts, campaigns, or files and build ranked creator-ready packages.",
  path: "/",
  keywords: [
    "any source ai content engine",
    "ranked clip packages",
    "audio repurposing",
    "twitch stream clipping",
    "creator workflow",
  ],
});

const proofPoints = [
  "Best clip first",
  "Rendered proof when available",
  "Strategy fallback stays separate",
  "Hooks, captions, timestamps",
  "Score and post order",
  "Copy-ready package",
];

const sourceModes = [
  {
    label: "Video",
    detail: "Clip-ready packages from video links or uploaded media when supported.",
    tone: "from-[rgba(109,92,255,0.14)] to-white",
  },
  {
    label: "Audio",
    detail: "Turn podcasts, voice, or sound sources into captions, scripts, and angles.",
    tone: "from-[rgba(49,130,246,0.14)] to-white",
  },
  {
    label: "Music",
    detail: "Shape music ideas into promo hooks, visual direction, and posting packages.",
    tone: "from-[rgba(236,72,153,0.14)] to-white",
  },
  {
    label: "Prompt",
    detail: "Start from an idea when no finished media exists yet.",
    tone: "from-[rgba(16,185,129,0.14)] to-white",
  },
  {
    label: "Twitch / Stream",
    detail: "Package VOD and stream moments for creator-native short-form review.",
    tone: "from-[rgba(245,158,11,0.16)] to-white",
  },
  {
    label: "Campaign / Objective",
    detail: "Translate goals into hooks, captions, thumbnails, and manual-review briefs.",
    tone: "from-[rgba(139,92,246,0.14)] to-white",
  },
  {
    label: "Upload / File",
    detail: "Use owned source files when the active workflow can process them.",
    tone: "from-[rgba(20,184,166,0.14)] to-white",
  },
];

const moneyPaths = [
  "Generate from source",
  "Request custom clip pack",
  "Support the build",
  "Book demo",
  "Join creator/referral program",
];

export default function HomePage() {
  return (
    <section className="px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] w-full max-w-6xl items-center gap-10 py-10 lg:grid-cols-[minmax(0,1fr),420px]">
        <div className="text-center lg:text-left">
          <Logo animated />

          <h1 className="mt-10 text-4xl font-semibold leading-tight text-ink sm:text-6xl">
            Any source in. Creator-ready content out.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-8 text-subtext sm:text-lg">
            Drop video, audio, a stream, prompt, music idea, campaign objective, or owned file. LWA helps build ranked hooks, captions, visuals, post order, and rendered assets when available.
          </p>

          <form action="/generate" method="get" className="mt-10 w-full space-y-4">
            <input
              type="text"
              inputMode="url"
              autoCapitalize="off"
              autoCorrect="off"
              spellCheck={false}
              name="url"
              placeholder="Drop a video, audio file, stream link, Twitch VOD, music idea, campaign, or prompt..."
              className="source-command-input input-surface input-command w-full rounded-[28px] px-5 py-5 text-base"
              aria-label="Source, campaign, or prompt"
            />
            <button type="submit" className="primary-button w-full rounded-full px-6 py-4 text-base font-semibold">
              Generate from source
            </button>
          </form>

          <div className="mt-6 flex flex-wrap justify-center gap-2 lg:justify-start">
            {moneyPaths.map((path) => (
              <span key={path} className="rounded-full border border-[var(--divider)] bg-white/72 px-3 py-2 text-xs font-medium text-ink/72 shadow-sm">
                {path}
              </span>
            ))}
          </div>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-subtext">
            Whop is one access path. Direct checkout, demos, support, custom packs, and referral routes can be configured without changing the product flow.
          </p>
        </div>

        <aside className="relative overflow-hidden rounded-[38px] border border-white/70 bg-white/74 p-4 shadow-[0_28px_90px_rgba(88,70,140,0.16)] backdrop-blur-xl">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(236,72,153,0.20),transparent_30%),radial-gradient(circle_at_78%_24%,rgba(109,92,255,0.18),transparent_34%),radial-gradient(circle_at_56%_86%,rgba(16,185,129,0.18),transparent_30%)]" />
          <div className="relative overflow-hidden rounded-[30px] border border-white/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.72),rgba(255,255,255,0.42))]">
            <img
              src="/brand-source/chars/athena.png"
              alt="LWA character command interface"
              className="h-full min-h-[320px] w-full object-cover object-center"
            />
            <div className="absolute inset-x-4 bottom-4 rounded-[24px] border border-white/62 bg-white/78 p-4 shadow-[0_18px_50px_rgba(41,31,68,0.18)] backdrop-blur-md">
              <p className="section-kicker">Muse source engine</p>
              <p className="mt-2 text-lg font-semibold text-ink">Signal scan, package, render when possible.</p>
              <p className="mt-2 text-sm leading-6 text-subtext">
                Character-led brand assets are now visible without making the product dark-only.
              </p>
            </div>
          </div>
        </aside>
      </div>

      <section className="mx-auto mt-8 grid w-full max-w-6xl gap-3 pb-8 sm:grid-cols-2 lg:grid-cols-4">
        {sourceModes.map((mode) => (
          <div
            key={mode.label}
            className={`rounded-[24px] border border-white/66 bg-gradient-to-br ${mode.tone} px-5 py-5 shadow-sm`}
          >
            <p className="text-sm font-semibold text-ink">{mode.label}</p>
            <p className="mt-2 text-sm leading-6 text-subtext">{mode.detail}</p>
          </div>
        ))}
      </section>

      <section className="mx-auto grid w-full max-w-5xl gap-4 pb-16 sm:grid-cols-2 lg:grid-cols-3">
        {proofPoints.map((item) => (
          <div
            key={item}
            className="metric-tile rounded-[24px] px-5 py-5 text-sm font-medium text-ink/84 backdrop-blur-sm"
          >
            {item}
          </div>
        ))}
      </section>
    </section>
  );
}
