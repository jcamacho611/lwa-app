import { IntegrationsDashboard } from "../../components/worlds/IntegrationsDashboard";
import { LwaShell } from "../../components/worlds/LwaShell";
import { loadPostingConnections } from "../../lib/api";
import { readStoredToken } from "../../lib/auth";
import type { PostingConnection } from "../../lib/types";
import type { IntegrationCard } from "../../lib/worlds/types";

async function getIntegrationData() {
  const token = readStoredToken();

  if (!token) {
    return null;
  }

  try {
    const connections = await loadPostingConnections(token);

    // Transform PostingConnection data to match IntegrationCard interface
    const integrations: IntegrationCard[] = connections.map((connection: PostingConnection) => ({
      id: connection.id,
      name: connection.provider,
      category: "social" as const, // All posting connections are social integrations
      status: connection.is_active ? "connected" as const : "configured" as const,
      description: connection.account_label
        ? `Posting connection for ${connection.provider} (${connection.account_label})`
        : `Posting connection for ${connection.provider}`,
      envVars: [], // No env vars exposed for existing connections
      adminOnly: false,
    }));

    return integrations;
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
