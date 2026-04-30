import type { WorldJobDashboard } from "../../lib/worlds/types";
import { mockJobDashboard } from "../../lib/worlds/mock-data";
import { JobStatusCard } from "./JobStatusCard";
import { SafetyNotice } from "./SafetyNotice";

export function JobsMonitor({
  dashboard = mockJobDashboard,
}: {
  dashboard?: WorldJobDashboard;
}) {
  return (
    <div className="space-y-6">
      <section className="hero-card rounded-[30px] p-6">
        <p className="section-kicker">Job Control</p>
        <h2 className="mt-3 text-3xl font-semibold text-ink">
          Track uploads, transcripts, AI scoring, clip generation, and renders.
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/62">
          Long-running work now has records for status, progress, attempts, events, retry state, and ownership.
        </p>
      </section>

      <SafetyNotice>
        Jobs may retry processing tasks, but they must not double-charge credits, duplicate earnings, or approve payouts automatically.
      </SafetyNotice>

      <section className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
        {[
          ["Queued", dashboard.queued],
          ["Running", dashboard.running],
          ["Succeeded", dashboard.succeeded],
          ["Failed", dashboard.failed],
          ["Retrying", dashboard.retrying],
          ["Cancelled", dashboard.cancelled],
        ].map(([label, value]) => (
          <div key={label} className="metric-tile rounded-[24px] p-5">
            <p className="text-sm text-ink/46">{label}</p>
            <p className="mt-2 text-3xl font-semibold text-ink">{value}</p>
          </div>
        ))}
      </section>

      <section>
        <h3 className="mb-4 text-2xl font-semibold text-ink">Recent jobs</h3>
        <div className="grid gap-5 lg:grid-cols-2">
          {dashboard.recentJobs.map((job) => (
            <JobStatusCard key={job.id} job={job} />
          ))}
        </div>
      </section>
    </div>
  );
}
