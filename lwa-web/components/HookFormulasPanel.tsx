"use client";

import { useEffect, useState } from "react";

type HookFormula = {
  id: string;
  category?: string;
  formula?: string;
  example?: string;
  improved_version?: string;
  platform_fit?: string[];
  use_case?: string;
};

function loadHookFormulas(): Promise<HookFormula[]> {
  return fetch("/api/intelligence?endpoint=hook-formulas")
    .then((r) => r.json())
    .then((d) => (Array.isArray(d?.items) ? d.items : []));
}

export function HookFormulasPanel() {
  const [formulas, setFormulas] = useState<HookFormula[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHookFormulas()
      .then(setFormulas)
      .catch(() => setFormulas([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.15em] text-ink/46">Hook formulas</p>
        <div className="flex flex-wrap gap-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-8 w-24 animate-pulse rounded-full bg-white/10" />
          ))}
        </div>
      </div>
    );
  }

  if (formulas.length === 0) return null;

  return (
    <div className="space-y-3">
      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-ink/46">Hook formulas · {formulas.length} patterns</p>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {formulas.slice(0, 9).map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => setExpanded(expanded === f.id ? null : f.id)}
            className="glass-panel rounded-[18px] p-4 text-left transition hover:border-[var(--gold-border)]"
          >
            <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-ink/46">
              {f.category ?? f.id}
            </p>
            <p className="mt-1 text-sm font-medium text-ink">{f.formula}</p>
            {expanded === f.id ? (
              <div className="mt-3 space-y-2">
                {f.improved_version ? (
                  <p className="text-xs leading-5 text-[var(--gold)]">&ldquo;{f.improved_version}&rdquo;</p>
                ) : null}
                {f.use_case ? (
                  <p className="text-xs text-ink/50">{f.use_case}</p>
                ) : null}
                {f.platform_fit?.length ? (
                  <div className="flex flex-wrap gap-1">
                    {f.platform_fit.map((p) => (
                      <span key={p} className="rounded-full border border-[var(--divider)] px-2 py-0.5 text-[10px] text-ink/50">
                        {p.replace("_", " ")}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            ) : null}
          </button>
        ))}
      </div>
    </div>
  );
}
