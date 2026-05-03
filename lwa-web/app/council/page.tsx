import {
  CompanyOsShell,
  SectionHeader,
  StatusBadge,
} from "../../components/company-os/CompanyOsShell";
import { lwaCouncil } from "../../lib/company-os";

export default function CouncilPage() {
  return (
    <CompanyOsShell
      activeHref="/council"
      eyebrow="Company Council OS"
      title="The senior expert council encoded into the operating system."
      description="This is not a fantasy list. It is a role map for who owns decisions, metrics, next actions, and build responsibility across LWA."
    >
      <div className="space-y-10">
        <SectionHeader
          eyebrow="Council members"
          title={`${lwaCouncil.length} specialized operators`}
          description="Use these roles to assign work, prevent confusion, and keep every part of LWA moving."
        />

        <section className="grid gap-5 lg:grid-cols-2">
          {lwaCouncil.map((role) => (
            <article
              key={role.title}
              className="rounded-[26px] border border-white/10 bg-white/[0.04] p-6"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#C9A24A]">
                  {role.codename}
                </p>
                <StatusBadge status="ready" />
              </div>

              <h2 className="mt-4 text-2xl font-semibold text-white">
                {role.title}
              </h2>
              <p className="mt-3 text-sm leading-7 text-[#B8B3A7]">
                {role.mission}
              </p>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <MiniList title="Owns" items={role.owns} />
                <MiniList title="Metrics" items={role.metrics} />
                <MiniList title="Next actions" items={role.nextActions} />
                <MiniList
                  title="Build responsibilities"
                  items={role.buildResponsibilities}
                />
              </div>
            </article>
          ))}
        </section>
      </div>
    </CompanyOsShell>
  );
}

function MiniList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-white/40">
        {title}
      </p>
      <ul className="mt-3 space-y-2">
        {items.map((item) => (
          <li key={item} className="text-sm leading-6 text-white/70">
            • {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
