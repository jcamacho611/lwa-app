import { LwaShell } from "../../components/worlds/LwaShell";
import { PostingConnectionsView } from "../../components/worlds/PostingConnectionsView";

export default function IntegrationsPage() {
  return (
    <LwaShell title="Integrations">
      <PostingConnectionsView />
    </LwaShell>
  );
}
