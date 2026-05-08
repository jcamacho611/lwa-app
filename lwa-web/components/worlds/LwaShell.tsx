import Link from "next/link";
import type { ReactNode } from "react";
import { productThesis } from "../../lib/worlds/copy";

const nav = [
  { label: "Command", href: "/command-center" },
  { label: "Marketplace", href: "/marketplace" },
  { label: "UGC", href: "/ugc" },
  { label: "Jobs", href: "/jobs" },
  { label: "World", href: "/worlds/profile" },
  { label: "Economy", href: "/economy" },
  { label: "Pricing", href: "/pricing" },
  { label: "Integrations", href: "/integrations" },
  { label: "Admin", href: "/admin/marketplace" },
  { label: "Moderation", href: "/admin/moderation" },
  { label: "Audit Log", href: "/admin/audit-log" },
];

export function LwaShell({
  title,
  eyebrow = "LWA Worlds",
  children,
}: {
  title: string;
  eyebrow?: string;
  children: ReactNode;
}) {
  return (
    <section className="min-h-screen px-4 py-6 text-ink sm:px-6 lg:px-8">
      <div className="mx-auto w-full max-w-7xl">
        <header className="glass-panel mb-6 rounded-[28px] p-5 sm:p-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <p className="section-kicker">{eyebrow}</p>
              <h1 className="page-title mt-3 text-3xl font-semibold leading-tight sm:text-5xl">{title}</h1>
              <p className="mt-3 text-sm leading-7 text-ink/62">{productThesis}</p>
            </div>

            <nav className="flex flex-wrap gap-2" aria-label="LWA Worlds navigation">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-full border border-[var(--divider)] bg-white/50 px-4 py-2 text-sm font-medium text-ink/68 transition hover:border-[var(--gold-border)] hover:bg-[var(--gold-dim)] hover:text-[var(--gold)]"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>

        {children}
      </div>
    </section>
  );
}
