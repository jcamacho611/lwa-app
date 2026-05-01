import { JobsMonitor } from "../../components/worlds/JobsMonitor";
import { LwaShell } from "../../components/worlds/LwaShell";
import { getWorldJobDashboard } from "../../lib/worlds/api";
import { mockJobDashboard } from "../../lib/worlds/mock-data";

async function getJobsData() {
  try {
    return await getWorldJobDashboard();
  } catch {
    return null;
  }
}

export default async function JobsPage() {
  const dashboard = await getJobsData();

  if (!dashboard) {
    return (
      <LwaShell title="Jobs">
        <div className="glass-panel rounded-[28px] p-8 text-center">
          <p className="text-lg font-semibold text-ink">Live data unavailable</p>
          <p className="mt-2 text-sm text-ink/62">Connect or sign in to view job dashboard.</p>
        </div>
      </LwaShell>
    );
  }

  return (
    <LwaShell title="Jobs">
      <JobsMonitor dashboard={dashboard} />
    </LwaShell>
  );
}
