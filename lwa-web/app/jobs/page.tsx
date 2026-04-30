import { JobsMonitor } from "../../components/worlds/JobsMonitor";
import { LwaShell } from "../../components/worlds/LwaShell";
import { getWorldJobDashboard } from "../../lib/worlds/api";
import { mockJobDashboard } from "../../lib/worlds/mock-data";

async function getJobsData() {
  try {
    return await getWorldJobDashboard();
  } catch {
    return mockJobDashboard;
  }
}

export default async function JobsPage() {
  const dashboard = await getJobsData();

  return (
    <LwaShell title="Jobs">
      <JobsMonitor dashboard={dashboard} />
    </LwaShell>
  );
}
