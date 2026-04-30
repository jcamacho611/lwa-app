import type { ReactNode } from "react";

export function SafetyNotice({
  title = "Safety note",
  children,
}: {
  title?: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-[18px] border border-[var(--gold-border)] bg-[var(--gold-dim)] p-4 text-sm leading-7 text-ink/74">
      <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-[var(--accent-wine)]">
        {title}
      </p>
      <div>{children}</div>
    </div>
  );
}
