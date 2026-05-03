"use client";

import { useState } from "react";

interface ExportPackage {
  id: string;
  campaign_name: string;
  status: string;
  created_at: string;
  completed_at?: string;
  file_count: number;
  total_size: number;
  formats: string[];
  platforms: string[];
}

const mockPackages: ExportPackage[] = [
  {
    id: "pkg_001",
    campaign_name: "Podcast Series Q2",
    status: "ready",
    created_at: "2025-05-01T10:30:00Z",
    completed_at: "2025-05-01T11:15:00Z",
    file_count: 24,
    total_size: 245.5,
    formats: ["mp4", "mov"],
    platforms: ["tiktok", "instagram", "youtube"],
  },
  {
    id: "pkg_002",
    campaign_name: "Tutorial Shorts Batch",
    status: "processing",
    created_at: "2025-05-02T14:00:00Z",
    file_count: 12,
    total_size: 128.3,
    formats: ["mp4"],
    platforms: ["youtube_shorts", "tiktok"],
  },
  {
    id: "pkg_003",
    campaign_name: "Brand Launch Assets",
    status: "ready",
    created_at: "2025-04-28T09:00:00Z",
    completed_at: "2025-04-28T09:45:00Z",
    file_count: 36,
    total_size: 412.8,
    formats: ["mp4", "mov", "webm"],
    platforms: ["tiktok", "instagram", "youtube", "facebook"],
  },
];

export function CampaignExportPanel() {
  const [activeTab, setActiveTab] = useState<"packages" | "create" | "settings">("packages");
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#FF6B35]/20 text-3xl">
            📤
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white">Campaign Export Packager</h3>
            <p className="text-sm text-white/50">Bundle clips, hooks, captions for delivery</p>
          </div>
          <div className="flex gap-4 text-right">
            <div>
              <div className="text-sm text-white/50">Packages</div>
              <div className="text-xl font-bold text-[#FF6B35]">18</div>
            </div>
            <div>
              <div className="text-sm text-white/50">Exported</div>
              <div className="text-xl font-bold text-[#FF6B35]">847</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: "packages", label: "Packages", icon: "📦" },
          { id: "create", label: "Create New", icon: "➕" },
          { id: "settings", label: "Settings", icon: "⚙️" },
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

      {/* Packages Tab */}
      {activeTab === "packages" && (
        <div className="space-y-4">
          {mockPackages.map((pkg) => (
            <div
              key={pkg.id}
              onClick={() => setSelectedPackage(selectedPackage === pkg.id ? null : pkg.id)}
              className={`cursor-pointer rounded-2xl border p-5 transition ${
                selectedPackage === pkg.id
                  ? "border-[#C9A24A] bg-[#C9A24A]/5"
                  : "border-white/10 bg-white/[0.04] hover:border-white/20"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="mb-2 flex items-center gap-2">
                    <span
                      className={`rounded-full px-2 py-1 text-xs ${
                        pkg.status === "ready"
                          ? "bg-green-400/20 text-green-400"
                          : pkg.status === "processing"
                          ? "bg-yellow-400/20 text-yellow-400"
                          : "bg-white/10 text-white/50"
                      }`}
                    >
                      {pkg.status}
                    </span>
                    <span className="text-xs text-white/30">{pkg.id}</span>
                  </div>
                  <h4 className="font-medium text-white">{pkg.campaign_name}</h4>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-white">{pkg.file_count}</div>
                  <div className="text-xs text-white/30">files</div>
                </div>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {pkg.formats.map((fmt) => (
                  <span
                    key={fmt}
                    className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-1 text-xs uppercase text-white/50"
                  >
                    {fmt}
                  </span>
                ))}
                {pkg.platforms.map((plat) => (
                  <span
                    key={plat}
                    className="rounded-full bg-[#C9A24A]/20 px-2 py-1 text-xs capitalize text-[#E9C77B]"
                  >
                    {plat.replace("_", " ")}
                  </span>
                ))}
              </div>

              <div className="mt-4 flex items-center justify-between text-sm">
                <div className="text-white/50">
                  Created: {new Date(pkg.created_at).toLocaleDateString()}
                </div>
                <div className="text-white/50">{pkg.total_size.toFixed(1)} MB</div>
              </div>

              {selectedPackage === pkg.id && pkg.status === "ready" && (
                <div className="mt-4 flex gap-2 border-t border-white/10 pt-4">
                  <button className="flex-1 rounded-lg bg-[#C9A24A] px-4 py-2 text-sm font-medium text-black transition hover:bg-[#E9C77B]">
                    Download
                  </button>
                  <button className="flex-1 rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white transition hover:bg-white/[0.08]">
                    Share Link
                  </button>
                  <button className="rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white transition hover:bg-white/[0.08]">
                    ⋮
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create Tab */}
      {activeTab === "create" && (
        <div className="space-y-4">
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
            <h4 className="mb-6 font-medium text-white">Create Export Package</h4>

            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm text-white/70">Campaign Name</label>
                <input
                  type="text"
                  placeholder="Enter campaign name..."
                  className="w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-white outline-none placeholder:text-white/30"
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm text-white/70">Source Video</label>
                  <select className="w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-white outline-none">
                    <option>Select video...</option>
                    <option>Podcast Episode #42</option>
                    <option>Tutorial Series #3</option>
                    <option>Product Demo v2</option>
                  </select>
                </div>
                <div>
                  <label className="mb-2 block text-sm text-white/70">Packaging Angle</label>
                  <select className="w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-white outline-none">
                    <option>General</option>
                    <option>Viral Hooks</option>
                    <option>Educational</option>
                    <option>Promotional</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="mb-3 block text-sm text-white/70">Target Platforms</label>
                <div className="flex flex-wrap gap-2">
                  {["TikTok", "Instagram Reels", "YouTube Shorts", "Facebook", "Twitter"].map((platform) => (
                    <label
                      key={platform}
                      className="flex cursor-pointer items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 transition hover:bg-white/[0.08]"
                    >
                      <input type="checkbox" className="h-4 w-4 accent-[#C9A24A]" />
                      <span className="text-sm text-white/70">{platform}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-3 block text-sm text-white/70">Include Components</label>
                <div className="space-y-2">
                  {[
                    { label: "Clips (ranked by AI)", checked: true },
                    { label: "Hook variations", checked: true },
                    { label: "Captions with timing", checked: true },
                    { label: "Thumbnail text options", checked: false },
                    { label: "Platform-specific crops", checked: true },
                  ].map((item) => (
                    <label
                      key={item.label}
                      className="flex cursor-pointer items-center gap-3 rounded-lg bg-white/[0.02] p-3 transition hover:bg-white/[0.04]"
                    >
                      <input type="checkbox" defaultChecked={item.checked} className="h-4 w-4 accent-[#C9A24A]" />
                      <span className="text-sm text-white/70">{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button className="flex-1 rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
                  Create Package
                </button>
                <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white transition hover:bg-white/[0.08]">
                  Save as Draft
                </button>
              </div>
            </div>
          </div>

          {/* Preview */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
            <h4 className="mb-4 font-medium text-white">Package Preview</h4>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-xl bg-white/[0.02] p-4 text-center">
                <div className="text-2xl font-bold text-white">--</div>
                <div className="text-sm text-white/50">Clips</div>
              </div>
              <div className="rounded-xl bg-white/[0.02] p-4 text-center">
                <div className="text-2xl font-bold text-white">--</div>
                <div className="text-sm text-white/50">Estimated Size</div>
              </div>
              <div className="rounded-xl bg-white/[0.02] p-4 text-center">
                <div className="text-2xl font-bold text-white">--</div>
                <div className="text-sm text-white/50">Processing Time</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === "settings" && (
        <div className="space-y-4">
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
            <h4 className="mb-6 font-medium text-white">Export Settings</h4>

            <div className="space-y-6">
              <div>
                <label className="mb-3 block text-sm text-white/70">Default Format</label>
                <div className="flex gap-2">
                  {["MP4", "MOV", "WebM"].map((fmt) => (
                    <button
                      key={fmt}
                      className={`rounded-xl px-4 py-2 text-sm transition ${
                        fmt === "MP4"
                          ? "bg-[#C9A24A] text-black"
                          : "border border-white/10 bg-white/[0.04] text-white/70 hover:bg-white/[0.08]"
                      }`}
                    >
                      {fmt}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-3 block text-sm text-white/70">Default Quality</label>
                <div className="flex gap-2">
                  {["720p", "1080p", "4K"].map((res) => (
                    <button
                      key={res}
                      className={`rounded-xl px-4 py-2 text-sm transition ${
                        res === "1080p"
                          ? "bg-[#C9A24A] text-black"
                          : "border border-white/10 bg-white/[0.04] text-white/70 hover:bg-white/[0.08]"
                      }`}
                    >
                      {res}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-3 block text-sm text-white/70">Auto-Expire Packages</label>
                <select className="w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-white outline-none">
                  <option>7 days</option>
                  <option>30 days</option>
                  <option>90 days</option>
                  <option>Never</option>
                </select>
              </div>

              <div>
                <label className="mb-3 block text-sm text-white/70">Notification Preferences</label>
                <div className="space-y-2">
                  {[
                    { label: "Email when package is ready", checked: true },
                    { label: "Notify on processing updates", checked: false },
                    { label: "Alert when near storage limit", checked: true },
                  ].map((pref) => (
                    <label
                      key={pref.label}
                      className="flex cursor-pointer items-center gap-3 rounded-lg bg-white/[0.02] p-3"
                    >
                      <input type="checkbox" defaultChecked={pref.checked} className="h-4 w-4 accent-[#C9A24A]" />
                      <span className="text-sm text-white/70">{pref.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
          Quick Export
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Bulk Export
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Export History
        </button>
      </div>
    </div>
  );
}
