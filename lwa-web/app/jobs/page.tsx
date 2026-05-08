import { LwaShell } from "../../components/worlds/LwaShell";
import { JobsView } from "../../components/worlds/JobsView";

export default function JobsPage() {
  return (
    <LwaShell title="Jobs">
      <JobsView />
    </LwaShell>
  );
}
