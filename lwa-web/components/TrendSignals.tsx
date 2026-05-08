"use client";

import { useEffect, useState } from "react";
import { loadTrends, type TrendItem } from "../lib/api";

const SOURCE_COLORS: Record<string, string> = {
  "Google Trends": "bg-[var(--gold-dim)] text-[var(--gold)] border-[var(--gold-border)]",
  Reddit: "bg-orange-500/10 text-orange-600 border-orange-500/20 dark:text-orange-300",
  "Hacker News": "bg-amber-500/10 text-amber-700 border-amber-500/20 dark:text-amber-300",
};

function SourceBadge({ source }: { source: string }) {
  const cls = SOURCE_COLORS[source] ?? "bg-white/10 text-ink/60 border-[var(--divider)]";
  return (
    <span className={`inline-block rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.15em] ${cls}`}>
      {source}
    </span>
  );
}

export function TrendSignals() {
  const [trends, setTrends] = useState<TrendItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrends()
      .then(setTrends)
      .catch(() => setTrends([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex flex-wrap gap-2 px-1">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-6 w-28 animate-pulse rounded-full bg-white/10" />
        ))}
      </div>
    );
  }

  if (trends.length === 0) return null;

  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-ink/46">Live trend signals</p>
      <div className="flex flex-wrap gap-2">
        {trends.map((trend) => (
          <div
            key={trend.id}
            className="glass-panel flex max-w-[260px] flex-col gap-1 rounded-[16px] border p-3"
            title={trend.detail}
          >
            <div className="flex items-center gap-2">
              <SourceBadge source={trend.source} />
            </div>
            {trend.url ? (
              <a
                href={trend.url}
                target="_blank"
                rel="noopener noreferrer"
                className="truncate text-sm font-medium text-ink hover:text-[var(--gold)]"
              >
                {trend.title}
              </a>
            ) : (
              <p className="truncate text-sm font-medium text-ink">{trend.title}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
