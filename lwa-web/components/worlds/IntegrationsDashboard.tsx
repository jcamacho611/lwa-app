import { safetyCopy } from "../../lib/worlds/copy";
import { mockIntegrations } from "../../lib/worlds/mock-data";
import type { IntegrationCard } from "../../lib/worlds/types";
import { SafetyNotice } from "./SafetyNotice";
import { StatusBadge } from "./StatusBadge";

export function IntegrationsDashboard({
  integrations = mockIntegrations,
}: {
  integrations?: IntegrationCard[];
}) {
  return (
    <div className="space-y-6">
      <SafetyNotice title="Integration safety">
        {safetyCopy.polymarket} API keys must stay in environment variables. Posting APIs require platform approval and
        compliance review.
      </SafetyNotice>

      <section className="grid gap-5 lg:grid-cols-2">
        {integrations.map((integration) => (
          <article key={integration.id} className="glass-panel rounded-[24px] p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-ink/46">{integration.category}</p>
                <h3 className="mt-1 text-xl font-semibold text-ink">{integration.name}</h3>
              </div>
              <StatusBadge status={integration.status} />
            </div>
            <p className="mt-3 text-sm leading-7 text-ink/62">{integration.description}</p>
            {integration.envVars.length > 0 && (
              <div className="mt-4 rounded-[18px] border border-[var(--divider)] bg-[var(--surface-inset)] p-3">
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-ink/46">Required env vars</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {integration.envVars.map((envVar) => (
                    <span key={envVar} className="rounded-full border border-[var(--divider)] bg-white/50 px-3 py-1 text-xs text-ink/62">
                      {envVar}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </article>
        ))}
      </section>
    </div>
  );
}
