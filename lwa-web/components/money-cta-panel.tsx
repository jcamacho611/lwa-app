import { buildUtmUrl, getEnabledMoneyLinks, getPrimaryMoneyLink, type MoneyLink } from "../lib/money-links";

type MoneyCtaPanelProps = {
  variant?: "compact" | "full" | "quota" | "demo";
  title?: string;
  description?: string;
  source?: string;
};

function defaultTitle(variant: NonNullable<MoneyCtaPanelProps["variant"]>) {
  if (variant === "quota") return "Choose how to keep generating";
  if (variant === "demo") return "Start with the path that fits";
  return "Choose how to start";
}

function defaultDescription(variant: NonNullable<MoneyCtaPanelProps["variant"]>) {
  if (variant === "quota") {
    return "Daily free generation limit reached. Choose a checkout path, request a demo, or wait for reset.";
  }
  if (variant === "demo") {
    return "Use direct checkout, request a demo, or join the referral list. Whop is one option, not the only path.";
  }
  return "Use direct checkout, request a demo, or open Whop access when it fits. Payment and access verification depend on the selected platform.";
}

function categoryLabel(link: MoneyLink) {
  if (link.category === "checkout") return "Checkout";
  if (link.category === "demo") return "Demo";
  if (link.category === "affiliate") return "Partner";
  if (link.category === "booking") return "Booking";
  return "Contact";
}

export function MoneyCtaPanel({ variant = "full", title, description, source = "money_cta" }: MoneyCtaPanelProps) {
  const enabledLinks = getEnabledMoneyLinks();
  const primary = getPrimaryMoneyLink();
  const secondary = enabledLinks.filter((link) => link.key !== primary.key);
  const compact = variant === "compact";

  return (
    <section className={compact ? "rounded-[24px] border border-[var(--gold-border)] bg-[var(--gold-dim)] p-4" : "hero-card rounded-[32px] p-6 sm:p-8"}>
      <div className={compact ? "space-y-3" : "flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between"}>
        <div className="max-w-3xl">
          <p className="section-kicker">Money paths</p>
          <h3 className={compact ? "mt-2 text-xl font-semibold text-ink" : "mt-3 text-3xl font-semibold text-ink"}>
            {title || defaultTitle(variant)}
          </h3>
          <p className={compact ? "mt-2 text-sm leading-6 text-ink/66" : "mt-4 text-sm leading-7 text-ink/64"}>
            {description || defaultDescription(variant)}
          </p>
        </div>

        <a
          href={buildUtmUrl(primary, source)}
          target="_blank"
          rel="noreferrer"
          className="primary-button inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-semibold sm:w-auto"
        >
          {primary.label}
        </a>
      </div>

      {secondary.length ? (
        <div className={compact ? "mt-4 flex flex-wrap gap-2" : "mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3"}>
          {secondary.map((link) => (
            <a
              key={link.key}
              href={buildUtmUrl(link, source)}
              target="_blank"
              rel="noreferrer"
              className="rounded-[20px] border border-white/10 bg-white/[0.04] px-4 py-3 text-left transition hover:border-[var(--gold-border)] hover:bg-[var(--gold-dim)]"
            >
              <span className="block text-[10px] font-semibold uppercase tracking-[0.22em] text-muted">{categoryLabel(link)}</span>
              <span className="mt-2 block text-sm font-semibold text-ink">{link.shortLabel}</span>
              {!compact ? <span className="mt-2 block text-xs leading-5 text-ink/58">{link.description}</span> : null}
            </a>
          ))}
        </div>
      ) : null}

      {!compact ? (
        <p className="mt-5 text-xs leading-6 text-ink/48">
          LWA helps prepare ranked clip packages. It does not guarantee views, revenue, campaign approval, or automatic posting.
        </p>
      ) : null}
    </section>
  );
}
