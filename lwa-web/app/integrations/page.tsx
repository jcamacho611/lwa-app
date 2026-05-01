import { IntegrationsDashboard } from "../../components/worlds/IntegrationsDashboard";
import { LwaShell } from "../../components/worlds/LwaShell";
import { getIntegrations } from "../../lib/worlds/api";
import { mockIntegrations } from "../../lib/worlds/mock-data";

async function getIntegrationData() {
  try {
    return await getIntegrations();
  } catch {
    return null;
  }
}

export default async function IntegrationsPage() {
  const integrations = await getIntegrationData();

  if (!integrations) {
    return (
      <LwaShell title="Integrations">
        <div className="glass-panel rounded-[28px] p-8 text-center">
          <p className="text-lg font-semibold text-ink">Live data unavailable</p>
          <p className="mt-2 text-sm text-ink/62">Connect or sign in to view your integrations.</p>
        </div>
      </LwaShell>
    );
  }

  return (
    <LwaShell title="Integrations">
      <IntegrationsDashboard integrations={integrations} />
    </LwaShell>
  );
}
