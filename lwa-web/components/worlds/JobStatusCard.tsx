import type { WorldJob } from "../../lib/worlds/types";
import { formatDate } from "../../lib/worlds/utils";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function JobStatusCard({ job }: { job: WorldJob }) {
  return (
    <article className="glass-panel rounded-[28px] p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="section-kicker">{job.jobType}</p>
          <h3 className="mt-2 text-xl font-semibold text-ink">{job.title || job.id}</h3>
        </div>
        <StatusBadge status={job.status} />
      </div>

      {job.description ? <p className="mt-3 text-sm leading-6 text-ink/62">{job.description}</p> : null}

      <div className="mt-5">
        <div className="mb-2 flex justify-between text-xs text-ink/46">
          <span>Progress</span>
          <span>{job.progressPercent}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-[var(--surface-soft)]">
          <div className="h-full bg-[var(--gold)]" style={{ width: `${job.progressPercent}%` }} />
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <StatPill label="Priority" value={job.priority} />
        <StatPill label="Attempts" value={`${job.attemptCount}/${job.maxAttempts}`} />
        <StatPill label="Created" value={formatDate(job.createdAt)} />
        {job.targetType ? <StatPill label="Target" value={job.targetType} /> : null}
      </div>

      {job.errorMessage ? (
        <p className="mt-4 rounded-[18px] border border-red-400/25 bg-red-400/10 p-3 text-sm text-red-700 dark:text-red-100">
          {job.errorMessage}
        </p>
      ) : null}
    </article>
  );
}
