"use client";

import Link from "next/link";
import { LeeWuhMascot } from "./LeeWuhMascot";
import { LEE_WUH_BRAND } from "../../lib/brand/lee-wuh";

export function LeeWuhHero() {
  return (
    <div className="flex flex-col lg:flex-row items-center gap-8 lg:gap-12 max-w-6xl mx-auto px-6 py-16">
      {/* Left side - Content */}
      <div className="flex-1 text-center lg:text-left">
        <div className="inline-flex items-center gap-2 mb-4">
          <span className="text-lg font-semibold text-yellow-400">Meet Lee-Wuh.</span>
          <span className="text-lg text-yellow-300/80">⚡</span>
        </div>
        
        <h1 className="text-4xl lg:text-5xl font-bold text-white mb-4 leading-tight">
          The final boss of lazy content.
        </h1>
        
        <p className="text-xl lg:text-2xl text-white/90 mb-8 leading-relaxed">
          Drop one video. Get the best clips, hooks, captions, and posting angles.
        </p>
        
        <Link
          href="/generate"
          className="inline-flex items-center justify-center px-8 py-4 bg-yellow-400 text-black font-bold text-lg rounded-lg hover:bg-yellow-300 transition-all duration-200 hover:-translate-y-1 shadow-lg hover:shadow-xl"
        >
          Generate My Clip Pack
        </Link>
      </div>
      
      {/* Right side - Lee-Wuh Hero Image */}
      <div className="flex-1 flex justify-center lg:justify-end">
        <LeeWuhMascot
          variant="hero"
          size="hero"
          state="overlord"
          showAura={true}
          showLabel={true}
          useHeroAsset={true}
          className="max-w-full"
        />
      </div>
    </div>
  );
}
