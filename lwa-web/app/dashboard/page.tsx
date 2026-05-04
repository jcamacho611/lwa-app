import type { Metadata } from "next";
import { PlatformShell } from "../../components/platform/PlatformShell";
import { PlatformCard } from "../../components/platform/PlatformCard";
import { buildPageMetadata } from "../../lib/seo";
import { Clapperboard, Gamepad2, Store, Wallet } from "lucide-react";
import Link from "next/link";

export const metadata: Metadata = buildPageMetadata({
  title: "Dashboard | LWA",
  description: "Your creator command center. Decision hub, not data dump.",
  path: "/dashboard",
  keywords: ["creator dashboard", "command center", "clip workflow"],
});

export default function DashboardPage() {
  return (
    <PlatformShell
      title="Dashboard"
      subtitle="Your command center"
      variant="dashboard"
    >
      {/* Quick Actions Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Link href="/generate">
          <PlatformCard
            title="Generate Clips"
            subtitle="Create new content"
            variant="gold"
            className="h-32 cursor-pointer hover:scale-[1.02]"
          >
            <Clapperboard className="h-8 w-8 text-[#C9A24A]" />
          </PlatformCard>
        </Link>

        <Link href="/realm">
          <PlatformCard
            title="Game Realm"
            subtitle="Enter the world"
            variant="purple"
            className="h-32 cursor-pointer hover:scale-[1.02]"
          >
            <Gamepad2 className="h-8 w-8 text-[#9333EA]" />
          </PlatformCard>
        </Link>

        <Link href="/marketplace">
          <PlatformCard
            title="Marketplace"
            subtitle="Browse content"
            variant="highlight"
            className="h-32 cursor-pointer hover:scale-[1.02]"
          >
            <Store className="h-8 w-8 text-white/60" />
          </PlatformCard>
        </Link>

        <Link href="/wallet">
          <PlatformCard
            title="Wallet"
            subtitle="View earnings"
            variant="highlight"
            className="h-32 cursor-pointer hover:scale-[1.02]"
          >
            <Wallet className="h-8 w-8 text-white/60" />
          </PlatformCard>
        </Link>
      </div>

      {/* Main Content Area */}
      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <PlatformCard
            title="Recent Activity"
            subtitle="Your latest work"
          >
            <p className="text-white/40">No recent activity yet.</p>
          </PlatformCard>
        </div>

        <div>
          <PlatformCard
            title="Quick Stats"
            subtitle="At a glance"
          >
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-white/60">Total Clips</span>
                <span className="font-semibold text-white">0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/60">Campaigns</span>
                <span className="font-semibold text-white">0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/60">Earnings</span>
                <span className="font-semibold text-[#C9A24A]">$0.00</span>
              </div>
            </div>
          </PlatformCard>
        </div>
      </div>
    </PlatformShell>
  );
}
