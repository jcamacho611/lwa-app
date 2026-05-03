"use client";

import { useState } from "react";

interface WorldZone {
  id: string;
  name: string;
  description: string;
  zone_type: string;
  theme: string;
  difficulty: number;
  is_unlocked: boolean;
  completion_percentage: number;
  metadata?: { icon?: string; color?: string };
}

interface WorldLocation {
  id: string;
  name: string;
  description: string;
  location_type: string;
  metadata?: { icon?: string; services?: string[] };
}

interface WorldEvent {
  id: string;
  name: string;
  description: string;
  event_type: string;
  status: string;
  rewards?: { experience?: number; credits?: number };
}

const mockZones: WorldZone[] = [
  {
    id: "zone_creator_hub",
    name: "Creator Hub",
    description: "The central nexus where all creators begin their journey.",
    zone_type: "hub",
    theme: "afro_futurist_tech",
    difficulty: 1,
    is_unlocked: true,
    completion_percentage: 75,
    metadata: { icon: "🏠", color: "#C9A24A" },
  },
  {
    id: "zone_brand_world",
    name: "Lee-Wuh Brand World",
    description: "The mascot universe where brand identity and creative spirit converge.",
    zone_type: "creative",
    theme: "anime_afro_fusion",
    difficulty: 2,
    is_unlocked: true,
    completion_percentage: 45,
    metadata: { icon: "🦁", color: "#6D3BFF" },
  },
  {
    id: "zone_marketplace",
    name: "Opportunity Marketplace",
    description: "Where creators find jobs, campaigns, and collaboration opportunities.",
    zone_type: "commercial",
    theme: "neon_night_market",
    difficulty: 3,
    is_unlocked: false,
    completion_percentage: 0,
    metadata: { icon: "💼", color: "#00D9FF" },
  },
  {
    id: "zone_creative_lab",
    name: "Creative Laboratories",
    description: "Advanced research facilities where new AI tools are developed.",
    zone_type: "research",
    theme: "futuristic_lab",
    difficulty: 5,
    is_unlocked: false,
    completion_percentage: 0,
    metadata: { icon: "🔬", color: "#FF6B35" },
  },
];

const mockLocations: WorldLocation[] = [
  {
    id: "loc_command_center",
    name: "Command Center",
    description: "Central operations hub for all clipping and generation activities.",
    location_type: "facility",
    metadata: { icon: "🎮", services: ["clip_generation", "batch_processing"] },
  },
  {
    id: "loc_clip_engine",
    name: "Clip Engine Core",
    description: "The heart of LWA's AI clipping technology.",
    location_type: "facility",
    metadata: { icon: "✂️", services: ["video_analysis", "moment_detection"] },
  },
  {
    id: "loc_mascot_temple",
    name: "Lee-Wuh Temple",
    description: "Sacred grounds honoring the brand mascot and creative spirit.",
    location_type: "landmark",
    metadata: { icon: "🦁", services: ["brand_guidance", "inspiration"] },
  },
  {
    id: "loc_design_studio",
    name: "Brand Design Studio",
    description: "Creative workspace for brand assets and visual identity.",
    location_type: "facility",
    metadata: { icon: "🎨", services: ["asset_creation", "brand_consultation"] },
  },
];

const mockEvents: WorldEvent[] = [
  {
    id: "event_daily_clip_challenge",
    name: "Daily Clip Challenge",
    description: "Create and submit your best clip from a trending source.",
    event_type: "daily",
    status: "active",
    rewards: { experience: 300, credits: 50 },
  },
  {
    id: "event_weekly_campaign",
    name: "Weekly Campaign Sprint",
    description: "Join forces with other creators for a major brand campaign.",
    event_type: "weekly",
    status: "upcoming",
    rewards: { experience: 1500, credits: 200 },
  },
  {
    id: "event_brand_world_festival",
    name: "Lee-Wuh Brand Festival",
    description: "Celebrate the mascot and explore the brand universe.",
    event_type: "special",
    status: "upcoming",
    rewards: { experience: 800 },
  },
];

export function GameWorldPanel() {
  const [activeTab, setActiveTab] = useState<"map" | "events" | "progress">("map");
  const [selectedZone, setSelectedZone] = useState<string | null>("zone_creator_hub");

  const selectedZoneData = mockZones.find((z) => z.id === selectedZone);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#6D3BFF]/20 text-3xl">
            🌍
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white">LWA Creator Realm</h3>
            <p className="text-sm text-white/50">Afro-futurist creator economy world</p>
          </div>
          <div className="ml-auto text-right">
            <div className="text-sm text-white/50">Active Players</div>
            <div className="text-2xl font-bold text-[#6D3BFF]">127</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: "map", label: "World Map", icon: "🗺️" },
          { id: "events", label: "Events", icon: "📅" },
          { id: "progress", label: "My Progress", icon: "🏆" },
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

      {/* Map Tab */}
      {activeTab === "map" && (
        <div className="grid gap-4 lg:grid-cols-[1fr_300px]">
          {/* Zones Grid */}
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              {mockZones.map((zone) => (
                <button
                  key={zone.id}
                  onClick={() => setSelectedZone(zone.id)}
                  className={`rounded-2xl border p-5 text-left transition-all ${
                    selectedZone === zone.id
                      ? "border-[#C9A24A] bg-[#C9A24A]/10"
                      : "border-white/10 bg-white/[0.04] hover:bg-white/[0.08]"
                  }`}
                >
                  <div className="mb-3 flex items-center gap-3">
                    <span className="text-2xl">{zone.metadata?.icon || "📍"}</span>
                    <div className="flex-1">
                      <h4 className="font-medium text-white">{zone.name}</h4>
                      <p className="text-xs capitalize text-white/50">{zone.zone_type} • Difficulty {zone.difficulty}</p>
                    </div>
                    {!zone.is_unlocked && (
                      <span className="rounded-full bg-white/10 px-2 py-1 text-xs text-white/50">🔒</span>
                    )}
                  </div>
                  <p className="mb-3 text-sm text-white/50">{zone.description}</p>
                  {zone.is_unlocked && (
                    <div>
                      <div className="mb-1 flex items-center justify-between text-xs">
                        <span className="text-white/50">Completion</span>
                        <span className="text-[#E9C77B]">{zone.completion_percentage}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/10">
                        <div
                          className="h-full rounded-full bg-[#C9A24A]"
                          style={{ width: `${zone.completion_percentage}%` }}
                        />
                      </div>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Zone Details Sidebar */}
          <div className="space-y-4">
            {selectedZoneData && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
                <div className="mb-4 flex items-center gap-3">
                  <span className="text-3xl">{selectedZoneData.metadata?.icon || "📍"}</span>
                  <div>
                    <h4 className="font-semibold text-white">{selectedZoneData.name}</h4>
                    <p className="text-xs text-white/50">{selectedZoneData.theme.replace(/_/g, " ")}</p>
                  </div>
                </div>

                <p className="mb-4 text-sm text-white/50">{selectedZoneData.description}</p>

                {selectedZoneData.is_unlocked ? (
                  <>
                    <div className="mb-4">
                      <div className="mb-1 flex items-center justify-between text-xs">
                        <span className="text-white/50">Completion</span>
                        <span className="text-[#E9C77B]">{selectedZoneData.completion_percentage}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/10">
                        <div
                          className="h-full rounded-full bg-[#C9A24A]"
                          style={{ width: `${selectedZoneData.completion_percentage}%` }}
                        />
                      </div>
                    </div>

                    <h5 className="mb-2 text-sm font-medium text-white">Locations</h5>
                    <div className="space-y-2">
                      {mockLocations
                        .filter((loc) => {
                          const zoneKey = selectedZoneData.id.replace("zone_", "");
                          if (selectedZoneData.id === "zone_creator_hub") {
                            return loc.id.includes("command") || loc.id.includes("clip");
                          }
                          if (selectedZoneData.id === "zone_brand_world") {
                            return loc.id.includes("mascot") || loc.id.includes("design") || loc.id.includes("brand");
                          }
                          return loc.id.includes(zoneKey);
                        })
                        .slice(0, 3)
                        .map((loc) => (
                          <div
                            key={loc.id}
                            className="flex items-center gap-2 rounded-xl bg-white/[0.02] p-2 text-sm"
                          >
                            <span>{loc.metadata?.icon || "📍"}</span>
                            <span className="flex-1 text-white/70">{loc.name}</span>
                            <span className="text-xs capitalize text-white/30">{loc.location_type}</span>
                          </div>
                        ))}
                    </div>
                  </>
                ) : (
                  <div className="rounded-xl bg-white/[0.02] p-4 text-center">
                    <p className="mb-2 text-sm text-white/50">Zone Locked</p>
                    <p className="text-xs text-white/30">Complete previous zones to unlock</p>
                  </div>
                )}
              </div>
            )}

            {/* Quick Stats */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
              <h4 className="mb-3 font-medium text-white">World Stats</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Zones Unlocked</span>
                  <span className="text-white">
                    {mockZones.filter((z) => z.is_unlocked).length}/{mockZones.length}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Locations Visited</span>
                  <span className="text-white">6/{mockLocations.length}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Total Completion</span>
                  <span className="text-[#E9C77B]">
                    {Math.round(mockZones.reduce((acc, z) => acc + z.completion_percentage, 0) / mockZones.length)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Events Tab */}
      {activeTab === "events" && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {mockEvents.map((event) => (
              <div
                key={event.id}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-5"
              >
                <div className="mb-3 flex items-center justify-between">
                  <span
                    className={`rounded-full px-2 py-1 text-xs ${
                      event.status === "active"
                        ? "bg-green-400/20 text-green-400"
                        : event.status === "upcoming"
                        ? "bg-blue-400/20 text-blue-400"
                        : "bg-white/10 text-white/50"
                    }`}
                  >
                    {event.status}
                  </span>
                  <span className="text-xs capitalize text-white/30">{event.event_type}</span>
                </div>
                <h4 className="mb-2 font-medium text-white">{event.name}</h4>
                <p className="mb-4 text-sm text-white/50">{event.description}</p>

                {event.rewards && (
                  <div className="flex flex-wrap gap-2">
                    {event.rewards.experience && (
                      <span className="rounded-full bg-[#C9A24A]/20 px-2 py-1 text-xs text-[#E9C77B]">
                        +{event.rewards.experience} XP
                      </span>
                    )}
                    {event.rewards.credits && (
                      <span className="rounded-full bg-[#6D3BFF]/20 px-2 py-1 text-xs text-[#6D3BFF]">
                        +{event.rewards.credits} Credits
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Event Calendar</h4>
            <div className="space-y-3">
              {[
                { day: "Today", events: ["Daily Clip Challenge"] },
                { day: "Tomorrow", events: ["Caption Workshop", "Brand Guidelines Review"] },
                { day: "This Week", events: ["Weekly Campaign Sprint", "Creator Meetup"] },
                { day: "This Month", events: ["Lee-Wuh Brand Festival"] },
              ].map((day, idx) => (
                <div key={idx} className="flex gap-4">
                  <div className="w-20 text-sm font-medium text-white/50">{day.day}</div>
                  <div className="flex-1 space-y-1">
                    {day.events.map((evt, eidx) => (
                      <div key={eidx} className="text-sm text-white/70">
                        • {evt}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Progress Tab */}
      {activeTab === "progress" && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 text-center">
              <div className="mb-2 text-3xl">🏆</div>
              <div className="text-2xl font-bold text-white">12</div>
              <div className="text-sm text-white/50">Achievements</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 text-center">
              <div className="mb-2 text-3xl">📍</div>
              <div className="text-2xl font-bold text-white">6</div>
              <div className="text-sm text-white/50">Locations Visited</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 text-center">
              <div className="mb-2 text-3xl">⭐</div>
              <div className="text-2xl font-bold text-white">3</div>
              <div className="text-sm text-white/50">Challenges Won</div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Recent Achievements</h4>
            <div className="space-y-3">
              {[
                { name: "First Steps", desc: "Visit your first location", unlocked: true, date: "2 days ago" },
                { name: "Clip Creator", desc: "Generate your first clip pack", unlocked: true, date: "3 days ago" },
                { name: "Brand Explorer", desc: "Visit 3 locations in Brand World", unlocked: true, date: "5 days ago" },
                { name: "Campaign Starter", desc: "Join your first campaign", unlocked: false, progress: "0/1" },
                { name: "Master Creator", desc: "Reach Level 50", unlocked: false, progress: "42/50" },
              ].map((ach) => (
                <div
                  key={ach.name}
                  className={`flex items-center gap-4 rounded-xl p-3 ${
                    ach.unlocked ? "bg-[#C9A24A]/10" : "bg-white/[0.02]"
                  }`}
                >
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-full ${
                      ach.unlocked ? "bg-[#C9A24A] text-black" : "bg-white/10 text-white/30"
                    }`}
                  >
                    {ach.unlocked ? "✓" : "○"}
                  </div>
                  <div className="flex-1">
                    <div className={`font-medium ${ach.unlocked ? "text-white" : "text-white/50"}`}>
                      {ach.name}
                    </div>
                    <div className="text-xs text-white/30">{ach.desc}</div>
                  </div>
                  <div className="text-right">
                    {ach.unlocked ? (
                      <div className="text-xs text-white/30">{ach.date}</div>
                    ) : (
                      <div className="text-xs text-white/50">{ach.progress}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
          Explore World
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Join Event
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          World Map
        </button>
      </div>
    </div>
  );
}
