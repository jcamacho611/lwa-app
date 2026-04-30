import { cn } from "../../lib/worlds/utils";

export function StatPill({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: string | number;
  accent?: boolean;
}) {
  return (
    <div
      className={cn(
        "inline-flex min-h-[32px] items-center rounded-full border px-3 py-1 text-xs",
        accent
          ? "border-[var(--gold-border)] bg-[var(--gold-dim)] text-[var(--gold)]"
          : "border-[var(--divider)] bg-[var(--surface-soft)] text-ink/72",
      )}
    >
      <span className="mr-2 text-ink/46">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}
