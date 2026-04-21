"use client";

import { useEffect, useMemo, useRef } from "react";

export function useStableResults<T>(incoming: T | null | undefined): T | null | undefined {
  const stableRef = useRef<T | null | undefined>(undefined);

  useEffect(() => {
    if (incoming) {
      stableRef.current = incoming;
    }
  }, [incoming]);

  return useMemo(() => stableRef.current ?? incoming, [incoming]);
}
