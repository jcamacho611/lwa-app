"use client";

import { type ReactNode } from "react";

type LeeWuhTipProps = {
  tone?: "default" | "success" | "warning" | "danger" | "premium";
  children: ReactNode;
};

const toneClass = {
  default: "border-white/10 bg-white/[0.04] text-white/70",
  success: "border-emerald-300/20 bg-emerald-300/10 text-emerald-100",
  warning: "border-yellow-300/20 bg-yellow-300/10 text-yellow-100",
  danger: "border-red-400/20 bg-red-400/10 text-red-100",
  premium: "border-purple-300/20 bg-purple-400/10 text-purple-100",
};

export function LeeWuhTip({ tone = "default", children }: LeeWuhTipProps) {
  return (
    <div className={`rounded-2xl border px-4 py-3 text-sm leading-6 ${toneClass[tone]}`}>
      <span className="mr-2 text-yellow-200">Lee-Wuh:</span>
      {children}
    </div>
  );
}
