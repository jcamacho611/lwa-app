"use client";

import { LeeWuhMascot } from "./LeeWuhMascot";

export function LeeWuhProcessingState() {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6">
      <LeeWuhMascot
        state="thinking"
        size="lg"
        showAura={true}
        className="mb-6"
      />
      
      <div className="text-center max-w-md">
        <h3 className="text-xl font-semibold text-white mb-2">
          Lee-Wuh is finding your strongest moments...
        </h3>
        <p className="text-white/80 leading-relaxed">
          Scanning hooks, silence, energy, and viral structure.
        </p>
      </div>
      
      {/* Premium loading indicator */}
      <div className="mt-6 w-48 h-2 bg-white/10 rounded-full overflow-hidden">
        <div className="h-full w-3/4 bg-gradient-to-r from-yellow-400 to-purple-500 rounded-full motion-safe:animate-pulse" />
      </div>
    </div>
  );
}
