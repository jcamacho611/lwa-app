"use client";

import { useState } from "react";
import { LeeWuhCharacter, LeeWuhAvatar } from "./LeeWuhCharacter";

interface BrandRule {
  id: string;
  title: string;
  description: string;
  do: string[];
  dont: string[];
}

const brandRules: BrandRule[] = [
  {
    id: "character",
    title: "Character Identity",
    description: "Lee-Wuh is the mascot, not the product. LWA is the creator engine.",
    do: ["Use Lee-Wuh as brand guardian", "Show personality in loading states", "Keep character consistent"],
    dont: ["Confuse mascot with product name", "Use Lee-Wuh without context", "Break character consistency"],
  },
  {
    id: "visual",
    title: "Visual Identity",
    description: "Afro-Futurist meets Japanese anime final-boss energy.",
    do: ["Use gold (#C9A24A) as primary", "Purple (#6D3BFF) for accents", "Black base with charcoal layers"],
    dont: ["Use clashing bright colors", "Lose the premium dark feel", "Make it too playful/cartoonish"],
  },
  {
    id: "voice",
    title: "Voice &amp; Tone",
    description: "Cute, powerful, premium, flashy. Final boss energy with approachability.",
    do: ["Be encouraging but confident", "Use 'we' when helping creators", "Celebrate wins with flair"],
    dont: ["Be condescending", "Use corporate robot voice", "Apologize excessively"],
  },
  {
    id: "usage",
    title: "Usage Guidelines",
    description: "Where and how Lee-Wuh appears across the app.",
    do: ["Loading states", "Empty states", "Celebration moments", "Help/tooltips"],
    dont: ["Error pages (unless soft errors)", "Critical business UI", "iOS app (separate guidelines)"],
  },
];

const assetPaths = [
  { name: "Hero 16:9", path: "/brand/lee-wuh-hero-16x9.png", usage: "Homepage, Whop cover, social" },
  { name: "Avatar Square", path: "/brand/lee-wuh-avatar.png", usage: "Loading states, empty states" },
  { name: "3D Model", path: "/brand/lee-wuh/3d/lee-wuh-mascot.glb", usage: "Future 3D viewer" },
  { name: "Rive States", path: "/brand/lee-wuh/lee-wuh-states.riv", usage: "Interactive animations" },
];

export function LeeWuhBrandGuide() {
  const [activeSection, setActiveSection] = useState<string>("character");
  const [showAssetPaths, setShowAssetPaths] = useState(false);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="rounded-[28px] border border-[#C9A24A]/30 bg-[#C9A24A]/10 p-8">
        <div className="flex flex-col items-center gap-6 text-center md:flex-row md:text-left">
          <LeeWuhCharacter mood="idle" size="xl" showMessage={false} />
          <div className="flex-1">
            <h2 className="text-3xl font-bold text-white">Lee-Wuh Brand World</h2>
            <p className="mt-2 text-lg text-white/70">
              The mascot universe that makes LWA unforgettable without hiding the product.
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2 md:justify-start">
              <span className="rounded-full bg-[#C9A24A]/20 px-3 py-1 text-xs text-[#E9C77B]">Afro-Futurist</span>
              <span className="rounded-full bg-[#6D3BFF]/20 px-3 py-1 text-xs text-[#6D3BFF]">Anime Energy</span>
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">Final Boss</span>
            </div>
          </div>
        </div>
      </div>

      {/* Brand Rules */}
      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        {/* Navigation */}
        <div className="space-y-3">
          {brandRules.map((rule) => (
            <button
              key={rule.id}
              onClick={() => setActiveSection(rule.id)}
              className={`w-full rounded-2xl border p-4 text-left transition ${
                activeSection === rule.id
                  ? "border-[#C9A24A] bg-[#C9A24A]/10"
                  : "border-white/10 bg-white/[0.04] hover:border-white/20"
              }`}
            >
              <h3 className={`font-medium ${activeSection === rule.id ? "text-[#E9C77B]" : "text-white"}`}>
                {rule.title}
              </h3>
            </button>
          ))}

          <button
            onClick={() => setShowAssetPaths(!showAssetPaths)}
            className="w-full rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-left transition hover:border-[#C9A24A]/50"
          >
            <h3 className="font-medium text-white">Asset Paths</h3>
            <p className="mt-1 text-xs text-white/50">File locations & usage</p>
          </button>
        </div>

        {/* Content */}
        <div>
          {brandRules.map((rule) => (
            activeSection === rule.id && (
              <div key={rule.id} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
                <div className="mb-6 flex items-center gap-3">
                  <LeeWuhAvatar mood={rule.id === "character" ? "idle" : rule.id === "visual" ? "victory" : "helping"} size="md" />
                  <div>
                    <h3 className="text-xl font-semibold text-white">{rule.title}</h3>
                    <p className="text-sm text-white/50">{rule.description}</p>
                  </div>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                  <div>
                    <h4 className="mb-3 flex items-center gap-2 text-sm font-medium text-green-400">
                      <span>✓</span> Do
                    </h4>
                    <ul className="space-y-2">
                      {rule.do.map((item, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-white/70">
                          <span className="mt-1 text-green-400">•</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="mb-3 flex items-center gap-2 text-sm font-medium text-red-400">
                      <span>✗</span> Don&apos;t
                    </h4>
                    <ul className="space-y-2">
                      {rule.dont.map((item, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-white/70">
                          <span className="mt-1 text-red-400">•</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )
          ))}

          {showAssetPaths && (
            <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
              <div className="mb-6 flex items-center gap-3">
                <LeeWuhAvatar mood="victory" size="md" />
                <div>
                  <h3 className="text-xl font-semibold text-white">Brand Asset Paths</h3>
                  <p className="text-sm text-white/50">Official locations for Windsurf to use or create assets</p>
                </div>
              </div>

              <div className="space-y-4">
                {assetPaths.map((asset) => (
                  <div
                    key={asset.name}
                    className="flex items-center justify-between rounded-2xl bg-white/[0.02] p-4"
                  >
                    <div>
                      <h4 className="font-medium text-white">{asset.name}</h4>
                      <code className="mt-1 block text-xs text-[#E9C77B]">{asset.path}</code>
                    </div>
                    <span className="text-xs text-white/50">{asset.usage}</span>
                  </div>
                ))}
              </div>

              <div className="mt-6 rounded-2xl border border-[#C9A24A]/20 bg-[#C9A24A]/5 p-4">
                <h4 className="mb-2 font-medium text-[#E9C77B]">3D / Rive Roadmap</h4>
                <ol className="space-y-2 text-sm text-white/70">
                  <li>1. <strong className="text-white">Static PNG system</strong> — Use approved 16:9 asset for homepage, Whop, social</li>
                  <li>2. <strong className="text-white">Avatar crops</strong> — Create square, transparent, small loading-state versions</li>
                  <li>3. <strong className="text-white">Blender blockout</strong> — Create Lee-Wuh model with chibi proportions, dreads, jewelry, hoodie, aura rings</li>
                  <li>4. <strong className="text-white">Web GLB</strong> — Export optimized .glb for lightweight 3D web use</li>
                  <li>5. <strong className="text-white">Rive states</strong> — Idle, analyzing, rendering, complete, victory, error states</li>
                </ol>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Reference */}
      <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
        <h3 className="mb-4 text-lg font-semibold text-white">Quick Reference</h3>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl bg-white/[0.02] p-4 text-center">
            <div className="mb-2 text-2xl">🎨</div>
            <div className="font-medium text-white">Primary</div>
            <code className="text-xs text-[#C9A24A]">#C9A24A</code>
          </div>
          <div className="rounded-2xl bg-white/[0.02] p-4 text-center">
            <div className="mb-2 text-2xl">💜</div>
            <div className="font-medium text-white">Accent</div>
            <code className="text-xs text-[#6D3BFF]">#6D3BFF</code>
          </div>
          <div className="rounded-2xl bg-white/[0.02] p-4 text-center">
            <div className="mb-2 text-2xl">⬛</div>
            <div className="font-medium text-white">Base</div>
            <code className="text-xs text-white/50">#0A0A0F</code>
          </div>
          <div className="rounded-2xl bg-white/[0.02] p-4 text-center">
            <div className="mb-2 text-2xl">◻️</div>
            <div className="font-medium text-white">Text</div>
            <code className="text-xs text-white/50">#F5F1E8</code>
          </div>
        </div>
      </div>
    </div>
  );
}
