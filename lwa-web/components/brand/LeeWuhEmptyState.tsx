"use client";

import { type ReactNode } from "react";
import { LeeWuhMascot } from "./LeeWuhMascot";

type LeeWuhEmptyStateProps = {
  title: string;
  body: string;
  action?: ReactNode;
};

export function LeeWuhEmptyState({ title, body, action }: LeeWuhEmptyStateProps) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-white/[0.035] p-6 text-center">
      <LeeWuhMascot state="watching" size="md" showAura />
      <h3 className="mt-4 text-xl font-semibold text-white">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-white/60">{body}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}
