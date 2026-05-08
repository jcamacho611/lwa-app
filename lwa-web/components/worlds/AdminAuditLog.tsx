import type { AdminAuditEntry } from "../../lib/worlds/api";

function actionColor(actionType: string): string {
  if (actionType.includes("delete") || actionType.includes("remove") || actionType.includes("ban"))
    return "text-red-400";
  if (actionType.includes("approve") || actionType.includes("create") || actionType.includes("add"))
    return "text-emerald-400";
  if (actionType.includes("update") || actionType.includes("edit") || actionType.includes("patch"))
    return "text-[var(--gold)]";
  return "text-ink/72";
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function AdminAuditLog({ entries }: { entries: AdminAuditEntry[] }) {
  return (
    <div className="space-y-6">
      <section className="grid gap-5 md:grid-cols-3">
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/50">Total entries</p>
          <p className="mt-2 text-3xl font-semibold text-ink">{entries.length}</p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/50">Unique actors</p>
          <p className="mt-2 text-3xl font-semibold text-ink">
            {new Set(entries.map((e) => e.actor_user_id).filter(Boolean)).size}
          </p>
        </div>
        <div className="metric-tile rounded-[24px] p-5">
          <p className="text-sm text-ink/50">Action types</p>
          <p className="mt-2 text-3xl font-semibold text-ink">
            {new Set(entries.map((e) => e.action_type)).size}
          </p>
        </div>
      </section>

      <section className="glass-panel rounded-[30px] p-5">
        <h2 className="text-2xl font-semibold text-ink">Audit log</h2>
        {entries.length === 0 ? (
          <p className="mt-5 text-sm text-ink/50">No audit log entries recorded yet.</p>
        ) : (
          <div className="mt-5 space-y-2">
            {entries.map((entry) => (
              <article
                key={entry.public_id}
                className="rounded-[18px] border border-[var(--divider)] bg-white/[0.03] p-4"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={["text-sm font-semibold", actionColor(entry.action_type)].join(" ")}>
                        {entry.action_type}
                      </span>
                      <span className="rounded-full border border-white/10 px-2 py-0.5 text-[10px] text-ink/50">
                        {entry.target_type}
                      </span>
                      {entry.target_public_id ? (
                        <span className="font-mono text-[10px] text-ink/40 truncate max-w-[120px]">
                          {entry.target_public_id}
                        </span>
                      ) : null}
                    </div>
                    {entry.note ? (
                      <p className="mt-1.5 text-sm text-ink/62">{entry.note}</p>
                    ) : null}
                    {(entry.before_state || entry.after_state) ? (
                      <div className="mt-2 flex flex-wrap gap-3 text-xs text-ink/40">
                        {entry.before_state ? (
                          <span>
                            <span className="text-ink/30">before: </span>
                            <span className="font-mono">{entry.before_state.slice(0, 60)}</span>
                          </span>
                        ) : null}
                        {entry.after_state ? (
                          <span>
                            <span className="text-ink/30">after: </span>
                            <span className="font-mono">{entry.after_state.slice(0, 60)}</span>
                          </span>
                        ) : null}
                      </div>
                    ) : null}
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-[11px] text-ink/40">{formatDate(entry.created_at)}</p>
                    {entry.actor_user_id ? (
                      <p className="mt-0.5 font-mono text-[10px] text-ink/30 truncate max-w-[100px]">
                        {entry.actor_user_id}
                      </p>
                    ) : (
                      <p className="mt-0.5 text-[10px] text-ink/20">system</p>
                    )}
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
