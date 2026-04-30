import { statusLabel, statusTone } from "../../lib/worlds/utils";

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${statusTone(status)}`}>
      {statusLabel(status)}
    </span>
  );
}
