import type { Metadata } from "next";
import Link from "next/link";
import { Logo } from "../components/brand/Logo";
import { buildUtmUrl, getMoneyLinkByKey, getPrimaryMoneyLink, type MoneyLink } from "../lib/money-links";
import { COUNCIL_BRAND_LINE } from "../lib/production-council";
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
    status: "Live now",
    detail: "Clip-ready packages from public links and owned media workflows when they are enabled.",
    tone: "from-[rgba(109,92,255,0.14)] to-white",
  },
  {
    label: "Audio",
    status: "Expanding",
    detail: "Turn podcasts, voice notes, and sound-led sources into captions, scripts, and packaging angles.",
    tone: "from-[rgba(49,130,246,0.14)] to-white",
  },
  {
    label: "Music",
    status: "Expanding",
    detail: "Shape music ideas into promo hooks, visual direction, and posting packages without pretending a full editor already exists.",
    tone: "from-[rgba(236,72,153,0.14)] to-white",
  },
  {
    label: "Prompt",
    status: "In studio",
    detail: "Start from an idea when no finished media exists yet and build the package from intent first.",
    tone: "from-[rgba(16,185,129,0.14)] to-white",
  },
  {
    label: "Twitch / Stream",
    status: "Foundation",
    detail: "Keep VOD and stream highlight workflows visible so the product does not collapse back into a YouTube-only tool.",
    tone: "from-[rgba(245,158,11,0.16)] to-white",
  },
  {
    label: "Campaign / Objective",
    status: "Manual prep",
    detail: "Translate goals into hooks, captions, thumbnails, and manual-review briefs without fake submission automation.",
    tone: "from-[rgba(139,92,246,0.14)] to-white",
  },
  {
    label: "Upload / File",
    status: "When enabled",
    detail: "Use owned source files when the active workflow can actually process them.",
    tone: "from-[rgba(20,184,166,0.14)] to-white",
  },
];

type ActionPath = {
  label: string;
  detail: string;
  href: string | MoneyLink | null;
  source?: string;
  external?: boolean;
};

const actionPaths: ActionPath[] = [
  {
    label: "Generate from source",
    detail: "Open the live source engine and move into clip review.",
    href: "/generate",
    external: false,
  },
  {
    label: "Operator command center",
    detail: "Open the internal launch checklist for quality, reliability, and Director Brain readiness.",
    href: "/operator",
    external: false,
  },
  {
    label: "Signal Realms",
    detail: "Preview the future creator progression layer: classes, factions, quests, badges, and cosmetic identity.",
    href: "/realm",
    external: false,
  },
  {
    label: "Marketplace preview",
    detail: "See the future template, hook, caption, brand kit, and campaign asset layer.",
    href: "/marketplace",
    external: false,
  },
  {
    label: "Social status",
    detail: "Track future provider readiness without pretending direct posting is already approved.",
    href: "/social",
    external: false,
  },
  {
    label: "Proof layer",
    detail: "Review the future off-chain provenance plan without wallet, token, or unlock claims.",
    href: "/proof",
    external: false,
  },
  {
    label: "Request custom clip pack",
    detail: "Use a custom workflow or creator brief when direct generation is not the right first step.",
    href: getMoneyLinkByKey("demoForm") || getMoneyLinkByKey("contact") || getMoneyLinkByKey("booking") || getPrimaryMoneyLink(),
    source: "homepage_custom_clip_pack",
  },
  {
    label: "Support the build",
    detail: "Use the live support path without making checkout the whole product story.",
    href: getPrimaryMoneyLink(),
    source: "homepage_support_the_build",
  },
  {
    label: "Book demo",
    detail: "Use a guided walkthrough when a human operator path fits better.",
    href: getMoneyLinkByKey("booking") || getMoneyLinkByKey("demoForm") || getMoneyLinkByKey("contact") || getPrimaryMoneyLink(),
    source: "homepage_book_demo",
  },
  {
    label: "Join creator/referral program",
    detail: "Keep partner and early-operator lanes visible before every external form is configured.",
    href: getMoneyLinkByKey("affiliateForm") || getMoneyLinkByKey("contact") || getPrimaryMoneyLink(),
    source: "homepage_referral",
  },
];

function ActionCard({
  label,
  detail,
  href,
  source,
  external = true,
}: {
  label: string;
  detail: string;
  href: string | MoneyLink | null;
  source?: string;
  external?: boolean;
}) {
  const className =
    "rounded-[24px] border border-white/66 bg-white/78 px-5 py-5 shadow-sm transition hover:-translate-y-0.5 hover:border-[var(--gold-border)] hover:shadow-[var(--shadow-card)]";

  if (!href) {
    return (
      <div className={[className, "opacity-80"].join(" ")}>
        <p className="text-sm font-semibold text-ink">{label}</p>
        <p className="mt-2 text-sm leading-6 text-subtext">{detail}</p>
        <p className="mt-4 text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent-wine)]">
          Add path when configured
        </p>
      </div>
    );
  }

  if (!external && typeof href === "string") {
    return (
      <Link href={href} className={className}>
        <p className="text-sm font-semibold text-ink">{label}</p>
        <p className="mt-2 text-sm leading-6 text-subtext">{detail}</p>
        <p className="mt-4 text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent-wine)]">
          Open now
        </p>
      </Link>
    );
  }

  const link = typeof href === "string" ? href : buildUtmUrl(href, source || "homepage");

  return (
    <a href={link} target="_blank" rel="noreferrer" className={className}>
      <p className="text-sm font-semibold text-ink">{label}</p>
      <p className="mt-2 text-sm leading-6 text-subtext">{detail}</p>
      <p className="mt-4 text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent-wine)]">
        Open path
      </p>
    </a>
  );
}

export default function HomePage() {
  return (
    <section className="px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] w-full max-w-6xl items-center gap-10 py-10 lg:grid-cols-[minmax(0,1fr),420px]">
        <div className="text-center lg:text-left">
          <Logo animated />

          <p className="mt-10 text-[11px] font-semibold uppercase tracking-[0.32em] text-[var(--accent-wine)]">
            Any source in. Creator-ready content out.
          </p>
          <h1 className="mt-10 text-4xl font-semibold leading-tight text-ink sm:text-6xl">
            Give LWA the source, stream, prompt, music idea, or objective. It builds the content package.
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-8 text-subtext sm:text-lg">
            LWA is the any-source creator engine: video, audio, music, Twitch or stream material, prompt-led ideas, campaign objectives, and owned files when the workflow supports them. Ranked hooks, captions, visuals, post order, and rendered proof stay in one path.
          </p>

          <form action="/generate" method="get" className="mt-10 w-full space-y-4">
            <input
              type="text"
              inputMode="text"
              autoCapitalize="off"
              autoCorrect="off"
              spellCheck={false}
              name="url"
              placeholder="Drop a video, audio file, stream link, Twitch VOD, music idea, campaign, or prompt..."
              className="source-command-input input-surface input-command w-full rounded-[28px] px-5 py-5 text-base"
              aria-label="Source, campaign, or prompt"
            />
            <div className="flex flex-col gap-3 sm:flex-row">
              <button type="submit" className="primary-button w-full rounded-full px-6 py-4 text-base font-semibold sm:w-auto sm:min-w-[220px]">
                Generate from source
              </button>
              <Link
                href="/generate"
                className="inline-flex w-full items-center justify-center rounded-full border border-[var(--gold-border)] bg-white/72 px-6 py-4 text-base font-semibold text-ink transition hover:bg-[var(--surface-gold-ghost)] sm:w-auto"
              >
                Open source engine
              </Link>
            </div>
          </form>

          <p className="mt-4 max-w-2xl text-sm leading-7 text-subtext">
            Public links work now. Prompt, upload, audio, stream, and campaign lanes keep expanding inside the same studio without pretending every backend path is already fully finished.
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
                Existing Athena art is the current hero signature while the dedicated character-girl system is tightened further.
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
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-ink">{mode.label}</p>
              <span className="rounded-full border border-[var(--gold-border)] bg-white/72 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent-wine)]">
                {mode.status}
              </span>
            </div>
            <p className="mt-2 text-sm leading-6 text-subtext">{mode.detail}</p>
          </div>
        ))}
      </section>

      <section className="mx-auto mt-8 max-w-6xl pb-4">
        <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--accent-wine)]">How LWA is built</p>
        <p className="mt-2 text-base font-semibold text-ink sm:text-lg">{COUNCIL_BRAND_LINE}</p>
      </section>

      <section className="mx-auto mt-2 grid w-full max-w-6xl gap-4 pb-10 md:grid-cols-2 xl:grid-cols-5">
        {actionPaths.map((path) => (
          <ActionCard
            key={path.label}
            label={path.label}
            detail={path.detail}
            href={path.href}
            source={path.source}
            external={path.external}
          />
        ))}
      </section>

      <p className="mx-auto max-w-6xl pb-10 text-xs leading-6 text-subtext/80">
        Whop stays available as one live access path today. Demo, booking, support, referral, operator, marketplace, social, proof, and Realms routes appear as they are configured, without changing the product identity.
      </p>

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
