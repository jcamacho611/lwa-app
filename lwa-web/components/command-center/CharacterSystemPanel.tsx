"use client";

import { useState } from "react";
import { LeeWuhCharacter, LeeWuhAvatar } from "../lee-wuh";

interface CharacterAttribute {
  name: string;
  value: number;
  max_value: number;
  description: string;
}

interface CharacterSkill {
  name: string;
  level: number;
  max_level: number;
  experience: number;
  description: string;
}

interface CharacterProfile {
  id: string;
  name: string;
  display_name: string;
  level: number;
  experience: number;
  next_level_exp: number;
  attributes: CharacterAttribute[];
  skills: CharacterSkill[];
  state: {
    mood: string;
    energy: number;
    focus: number;
    creativity: number;
  };
}

const mockCharacter: CharacterProfile = {
  id: "char_lee_wuh_001",
  name: "lee_wuh",
  display_name: "Lee-Wuh",
  level: 42,
  experience: 87500,
  next_level_exp: 100000,
  attributes: [
    { name: "creativity", value: 95, max_value: 100, description: "Creative capacity" },
    { name: "focus", value: 88, max_value: 100, description: "Focus ability" },
    { name: "energy", value: 92, max_value: 100, description: "Energy level" },
    { name: "analytical", value: 85, max_value: 100, description: "Problem-solving" },
    { name: "social", value: 78, max_value: 100, description: "Audience connection" },
  ],
  skills: [
    { name: "clip_generation", level: 15, max_level: 20, experience: 7500, description: "Identify and package video moments" },
    { name: "hook_writing", level: 12, max_level: 20, experience: 6000, description: "Craft compelling openings" },
    { name: "caption_optimization", level: 11, max_level: 20, experience: 5500, description: "Perfect text overlays" },
    { name: "thumbnail_design", level: 10, max_level: 20, experience: 5000, description: "Create scroll-stopping visuals" },
    { name: "platform_strategy", level: 13, max_level: 20, experience: 6500, description: "Optimize per platform" },
  ],
  state: {
    mood: "inspired",
    energy: 0.92,
    focus: 0.88,
    creativity: 0.95,
  },
};

export function CharacterSystemPanel() {
  const [activeTab, setActiveTab] = useState<"profile" | "skills" | "progression">("profile");
  const [character] = useState<CharacterProfile>(mockCharacter);

  const progressPercentage = (character.experience / character.next_level_exp) * 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div className="flex items-center gap-4">
          <LeeWuhCharacter 
            mood={character.state.mood === "inspired" ? "victory" : "idle"} 
            size="lg" 
            showMessage={false} 
          />
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h3 className="text-xl font-semibold text-white">{character.display_name}</h3>
              <span className="rounded-full bg-[#C9A24A]/20 px-3 py-1 text-sm font-medium text-[#E9C77B]">
                Level {character.level}
              </span>
            </div>
            <p className="text-sm text-white/50">Character ID: {character.id}</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-white/50">Current State</div>
            <div className="flex items-center gap-2 text-lg font-medium capitalize text-[#E9C77B]">
              <span className="inline-block h-2 w-2 rounded-full bg-green-400"></span>
              {character.state.mood}
            </div>
          </div>
        </div>

        {/* XP Bar */}
        <div className="mt-6">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="text-white/70">Experience</span>
            <span className="text-white/50">
              {character.experience.toLocaleString()} / {character.next_level_exp.toLocaleString()} XP
            </span>
          </div>
          <div className="h-3 rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#C9A24A] to-[#E9C77B] transition-all"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
          <p className="mt-2 text-right text-sm text-[#E9C77B]">
            {progressPercentage.toFixed(1)}% to Level {character.level + 1}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: "profile", label: "Profile", icon: "👤" },
          { id: "skills", label: "Skills", icon: "⚡" },
          { id: "progression", label: "Progression", icon: "📈" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${
              activeTab === tab.id
                ? "bg-[#C9A24A] text-black"
                : "border border-white/10 bg-white/[0.04] text-white/70 hover:bg-white/[0.08]"
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "profile" && (
        <div className="grid gap-4 md:grid-cols-2">
          {/* State Panel */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Current State</h4>
            <div className="space-y-4">
              {[
                { label: "Energy", value: character.state.energy, color: "bg-green-400" },
                { label: "Focus", value: character.state.focus, color: "bg-blue-400" },
                { label: "Creativity", value: character.state.creativity, color: "bg-purple-400" },
              ].map((stat) => (
                <div key={stat.label}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-white/70">{stat.label}</span>
                    <span className="text-white/50">{(stat.value * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10">
                    <div
                      className={`h-full rounded-full ${stat.color} transition-all`}
                      style={{ width: `${stat.value * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Attributes Panel */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Attributes</h4>
            <div className="space-y-3">
              {character.attributes.map((attr) => (
                <div key={attr.name} className="flex items-center gap-3">
                  <div className="w-24 text-sm capitalize text-white/70">{attr.name}</div>
                  <div className="flex-1">
                    <div className="h-2 rounded-full bg-white/10">
                      <div
                        className="h-full rounded-full bg-[#C9A24A] transition-all"
                        style={{ width: `${(attr.value / attr.max_value) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="w-12 text-right text-sm text-white/50">
                    {attr.value}/{attr.max_value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === "skills" && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {character.skills.map((skill) => (
            <div key={skill.name} className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
              <div className="mb-3 flex items-center justify-between">
                <h4 className="font-medium capitalize text-white">{skill.name.replace("_", " ")}</h4>
                <span className="rounded-full bg-[#C9A24A]/20 px-2 py-1 text-xs text-[#E9C77B]">
                  Lv.{skill.level}
                </span>
              </div>
              <p className="mb-4 text-sm text-white/50">{skill.description}</p>
              <div className="mb-2 flex items-center justify-between text-xs text-white/50">
                <span>Level Progress</span>
                <span>{skill.experience.toLocaleString()} XP</span>
              </div>
              <div className="h-2 rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-[#6D3BFF] transition-all"
                  style={{ width: `${(skill.level / skill.max_level) * 100}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-white/30">
                Max Level: {skill.max_level}
              </p>
            </div>
          ))}
        </div>
      )}

      {activeTab === "progression" && (
        <div className="space-y-4">
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Level Progression</h4>
            <div className="space-y-4">
              {[
                { level: 42, title: "Master Creator", unlocked: true },
                { level: 43, title: "AI Virtuoso", unlocked: false },
                { level: 44, title: "Content Legend", unlocked: false },
                { level: 45, title: "Platform Deity", unlocked: false },
                { level: 50, title: "The Last Creator", unlocked: false },
              ].map((lvl, idx) => (
                <div
                  key={lvl.level}
                  className={`flex items-center gap-4 rounded-xl p-3 ${
                    lvl.unlocked ? "bg-[#C9A24A]/10" : "bg-white/[0.02]"
                  }`}
                >
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-full ${
                      lvl.unlocked ? "bg-[#C9A24A] text-black" : "bg-white/10 text-white/30"
                    }`}
                  >
                    {lvl.unlocked ? "✓" : idx + 1}
                  </div>
                  <div className="flex-1">
                    <div className={`font-medium ${lvl.unlocked ? "text-white" : "text-white/50"}`}>
                      Level {lvl.level}: {lvl.title}
                    </div>
                    <div className="text-sm text-white/30">
                      {lvl.unlocked ? "Unlocked" : "Locked"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Recent Activity</h4>
            <div className="space-y-3">
              {[
                { action: "Generated clip pack", xp: 500, time: "2 hours ago" },
                { action: "Created campaign", xp: 1000, time: "5 hours ago" },
                { action: "Optimized captions", xp: 250, time: "1 day ago" },
                { action: "Completed batch review", xp: 750, time: "2 days ago" },
              ].map((activity, idx) => (
                <div key={idx} className="flex items-center justify-between rounded-xl bg-white/[0.02] p-3">
                  <div>
                    <div className="text-sm text-white/70">{activity.action}</div>
                    <div className="text-xs text-white/30">{activity.time}</div>
                  </div>
                  <div className="text-sm font-medium text-[#E9C77B]">+{activity.xp} XP</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
          Train Skills
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          View Templates
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Character History
        </button>
      </div>
    </div>
  );
}
