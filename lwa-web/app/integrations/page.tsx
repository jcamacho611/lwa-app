import { IntegrationsDashboard } from "../../components/worlds/IntegrationsDashboard";
import { LwaShell } from "../../components/worlds/LwaShell";
import { getIntegrations } from "../../lib/worlds/api";
import { mockIntegrations } from "../../lib/worlds/mock-data";

async function getIntegrationData() {
  try {
    return await getIntegrations();
  } catch {
    return mockIntegrations;
  }
}

export default async function IntegrationsPage() {
  const integrations = await getIntegrationData();

  return (
    <LwaShell title="Integrations">
      <IntegrationsDashboard integrations={integrations} />
    </LwaShell>
  );
}
