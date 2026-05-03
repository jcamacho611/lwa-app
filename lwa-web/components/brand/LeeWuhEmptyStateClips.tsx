"use client";

import Link from "next/link";
import { LeeWuhMascot } from "./LeeWuhMascot";

export function LeeWuhEmptyStateClips() {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6">
      <LeeWuhMascot
        state="watching"
        size="lg"
        showAura={true}
        className="mb-6"
      />
      
      <div className="text-center max-w-md">
        <h3 className="text-2xl font-bold text-white mb-2">
          Feed Lee-Wuh a source.
        </h3>
        <p className="text-white/80 leading-relaxed mb-6">
          Paste a video URL and let the clipping engine find the best short-form moments.
        </p>
        
        <Link
          href="/generate"
          className="inline-flex items-center justify-center px-6 py-3 bg-yellow-400 text-black font-semibold rounded-lg hover:bg-yellow-300 transition-all duration-200 hover:-translate-y-1"
        >
          Add Your First Source
        </Link>
      </div>
    </div>
  );
}
