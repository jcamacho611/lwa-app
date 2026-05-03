import {
  CompanyOsCardGrid,
  CompanyOsShell,
  MetricGrid,
  SectionHeader,
  SurfaceLinkGrid,
} from "../../components/company-os/CompanyOsShell";
import {
  companyMetrics,
  companyOsCards,
  companyOsNav,
  creativeEngines,
  operationsChecklist,
} from "../../lib/company-os";
import { StatusBadge } from "../../components/company-os/CompanyOsShell";

export default function CompanyOsPage() {
  return (
    <CompanyOsShell
      activeHref="/company-os"
      eyebrow="LWA Company OS"
      title="One system for the app, company, brand, money, council, and execution."
      description="This is the master operating layer for LWA: creator app, clipping engine, Lee-Wuh brand world, revenue, campaigns, marketplace, expert council, automation, and release operations."
    >
      <div className="space-y-12">
        <MetricGrid metrics={companyMetrics} />

        <section>
          <SectionHeader
            eyebrow="Surfaces"
            title="Open the operating surfaces"
            description="Every important part of LWA needs a reachable surface. If it only exists in docs, this Company OS turns it into a working v0."
          />
          <SurfaceLinkGrid items={companyOsNav} />
        </section>

        <section>
          <SectionHeader
            eyebrow="Build map"
            title="Company system cards"
            description="These are the major operating systems Windsurf should keep expanding without stalling."
          />
          <CompanyOsCardGrid cards={companyOsCards} />
        </section>

        <section>
          <SectionHeader
            eyebrow="Creative engines"
            title="Everything LWA must eventually automate"
            description="Static metadata for v0 is acceptable. Later, backend routes can power this data."
          />
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {creativeEngines.map((engine) => (
              <div
                key={engine.name}
                className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5"
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold text-white">
                    {engine.name}
                  </h3>
                  <StatusBadge status={engine.status} />
                </div>
                <p className="mt-3 text-sm leading-6 text-white/60">
                  {engine.purpose}
                </p>
                <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-4">
                  <p className="font-mono text-xs uppercase tracking-[0.2em] text-white/40">
                    Next action
                  </p>
                  <p className="mt-2 text-sm text-white/75">
                    {engine.nextAction}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section>
          <SectionHeader
            eyebrow="Release control"
            title="Operations checklist"
            description="This keeps the company build from drifting into planning loops."
          />
          <div className="grid gap-4 md:grid-cols-2">
            {operationsChecklist.map((item) => (
              <div
                key={item.title}
                className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {item.title}
                    </h3>
                    <p className="mt-1 text-sm text-white/45">{item.owner}</p>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
                <p className="mt-4 text-sm leading-6 text-white/65">
                  {item.nextAction}
                </p>
                <p className="mt-3 text-xs uppercase tracking-[0.2em] text-[#E9C77B]">
                  {item.value}
                </p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </CompanyOsShell>
  );
}
