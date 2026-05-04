import type { Metadata } from "next";
import { PlatformShell } from "../../components/platform/PlatformShell";
import { PlatformCard } from "../../components/platform/PlatformCard";
import { buildPageMetadata } from "../../lib/seo";
import { Target, Plus } from "lucide-react";

export const metadata: Metadata = buildPageMetadata({
  title: "Campaigns | LWA",
  description: "Manage clip campaigns and assignments.",
  path: "/campaigns",
  keywords: ["campaigns", "clip workflow", "assignments"],
});

export default function CampaignsPage() {
  return (
    <PlatformShell
      title="Campaigns"
      subtitle="Manage assignments and delivery"
      variant="default"
    >
      {/* New Campaign Button */}
      <PlatformCard variant="gold" className="mb-6 cursor-pointer hover:scale-[1.01] transition-transform">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#C9A24A]/20">
            <Plus className="h-6 w-6 text-[#C9A24A]" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">New Campaign</h2>
            <p className="text-white/60">Create a new clip assignment</p>
          </div>
        </div>
      </PlatformCard>

      {/* Active Campaigns */}
      <h3 className="text-lg font-semibold text-white mb-4">Active Campaigns</h3>
      <div className="space-y-3">
        <PlatformCard variant="default">
          <div className="flex items-center gap-3">
            <Target className="h-5 w-5 text-[#C9A24A]" />
            <span className="text-white/60">No active campaigns yet.</span>
          </div>
        </PlatformCard>
      </div>
    </PlatformShell>
  );
}
