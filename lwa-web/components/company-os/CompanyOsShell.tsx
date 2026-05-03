import Link from "next/link";
import {
  type CompanyOsCard,
  type CompanyOsMetric,
  type CompanyOsNavItem,
  statusClasses,
  statusLabel,
} from "../../lib/company-os";

type ShellProps = {
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
  activeHref?: string;
};

export function CompanyOsShell({
  eyebrow,
  title,
  description,
  children,
  activeHref,
}: ShellProps) {
  return (
    <main className="min-h-screen bg-[#08080A] text-[#F5F1E8]">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-[-18%] top-[-10%] h-[560px] w-[560px] rounded-full bg-[#C9A24A]/10 blur-[120px]" />
        <div className="absolute right-[-15%] top-[15%] h-[520px] w-[520px] rounded-full bg-purple-600/15 blur-[130px]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.05),transparent_35%)]" />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl px-6 py-8">
        <CompanyOsTopNav activeHref={activeHref} />

        <section className="py-12">
          <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
            {eyebrow}
          </p>
          <div className="mt-4 grid gap-6 lg:grid-cols-[1fr_0.55fr] lg:items-end">
            <div>
              <h1 className="max-w-4xl text-balance text-[clamp(2.5rem,6vw,5.6rem)] font-semibold leading-[1.02] tracking-[-0.04em]">
                {title}
              </h1>
              <p className="mt-6 max-w-3xl text-lg leading-8 text-[#B8B3A7]">
                {description}
              </p>
            </div>

            <div className="rounded-[24px] border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-5">
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#E9C77B]">
                Execution rule
              </p>
              <p className="mt-3 text-sm leading-6 text-[#E7DDC8]">
                If it does not exist, build a useful v0. If it is unreachable,
                wire it. If validation fails, fix it. Ship coherent slices.
              </p>
            </div>
          </div>
        </section>

        {children}
      </div>
    </main>
  );
}

export function CompanyOsTopNav({ activeHref }: { activeHref?: string }) {
  const nav = [
    { title: "Company OS", href: "/company-os" },
    { title: "Command Center", href: "/command-center" },
    { title: "Council", href: "/council" },
    { title: "Brand World", href: "/brand-world" },
    { title: "Revenue", href: "/revenue" },
    { title: "Generate", href: "/generate" },
  ];

  return (
    <header className="flex flex-col gap-4 rounded-[24px] border border-white/10 bg-white/[0.04] p-4 backdrop-blur md:flex-row md:items-center md:justify-between">
      <Link href="/" className="flex items-center gap-3">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-[#16161B] ring-1 ring-[#2E2E38]">
          <span className="text-lg font-bold text-[#C9A24A]">L</span>
        </span>
        <div>
          <p className="text-sm font-semibold text-white">LWA Company OS</p>
          <p className="text-xs text-white/45">lee-wuh operating layer</p>
        </div>
      </Link>

      <nav className="flex flex-wrap gap-2">
        {nav.map((item) => {
          const active = activeHref === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={
                active
                  ? "rounded-full border border-[#C9A24A]/30 bg-[#C9A24A]/15 px-3 py-2 text-xs font-semibold text-[#E9C77B]"
                  : "rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-xs font-medium text-white/65 transition hover:border-white/20 hover:text-white"
              }
            >
              {item.title}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}

export function StatusBadge({ status }: { status: Parameters<typeof statusClasses>[0] }) {
  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${statusClasses(
        status,
      )}`}
    >
      {statusLabel(status)}
    </span>
  );
}

export function MetricGrid({ metrics }: { metrics: CompanyOsMetric[] }) {
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5"
        >
          <div className="flex items-center justify-between gap-3">
            <p className="font-mono text-xs uppercase tracking-[0.2em] text-white/45">
              {metric.label}
            </p>
            <StatusBadge status={metric.status} />
          </div>
          <p className="mt-4 text-2xl font-semibold text-white">{metric.value}</p>
          <p className="mt-2 text-sm leading-6 text-white/55">{metric.detail}</p>
        </div>
      ))}
    </section>
  );
}

export function CompanyOsCardGrid({ cards }: { cards: CompanyOsCard[] }) {
  return (
    <section className="grid gap-5 lg:grid-cols-2">
      {cards.map((card) => (
        <div
          key={card.title}
          className="rounded-[26px] border border-white/10 bg-white/[0.04] p-6"
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#C9A24A]">
              {card.eyebrow}
            </p>
            <StatusBadge status={card.status} />
          </div>

          <h2 className="mt-4 text-2xl font-semibold text-white">{card.title}</h2>
          <p className="mt-3 text-sm leading-7 text-[#B8B3A7]">{card.description}</p>

          <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-mono text-xs uppercase tracking-[0.2em] text-white/40">
              Next actions
            </p>
            <ul className="mt-3 space-y-2">
              {card.actions.map((action) => (
                <li key={action} className="text-sm leading-6 text-white/70">
                  • {action}
                </li>
              ))}
            </ul>
          </div>

          {card.href ? (
            <Link
              href={card.href}
              className="mt-5 inline-flex rounded-full bg-[#C9A24A] px-4 py-2 text-sm font-semibold text-black transition hover:bg-[#E9C77B]"
            >
              Open surface
            </Link>
          ) : null}
        </div>
      ))}
    </section>
  );
}

export function SurfaceLinkGrid({ items }: { items: CompanyOsNavItem[] }) {
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className="group rounded-[22px] border border-white/10 bg-white/[0.035] p-5 transition hover:-translate-y-0.5 hover:border-[#C9A24A]/35 hover:bg-[#C9A24A]/[0.06]"
        >
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-lg font-semibold text-white">{item.title}</h3>
            <StatusBadge status={item.status} />
          </div>
          <p className="mt-3 text-sm leading-6 text-white/55">
            {item.description}
          </p>
          <p className="mt-4 text-sm font-semibold text-[#E9C77B]">
            Open →
          </p>
        </Link>
      ))}
    </section>
  );
}

export function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description?: string;
}) {
  return (
    <div className="mb-5">
      <p className="font-mono text-xs uppercase tracking-[0.25em] text-[#C9A24A]">
        {eyebrow}
      </p>
      <h2 className="mt-2 text-3xl font-semibold tracking-[-0.03em] text-white">
        {title}
      </h2>
      {description ? (
        <p className="mt-3 max-w-3xl text-sm leading-6 text-white/55">
          {description}
        </p>
      ) : null}
    </div>
  );
}
