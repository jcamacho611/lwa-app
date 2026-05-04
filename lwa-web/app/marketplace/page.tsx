import { PlatformShell } from "../../components/platform/PlatformShell";
import { PlatformCard } from "../../components/platform/PlatformCard";
import { Store, Package, TrendingUp } from "lucide-react";
import { MarketplaceOverview } from "../../components/worlds/MarketplaceOverview";

export default function MarketplacePage() {
  return (
    <PlatformShell
      title="Marketplace"
      subtitle="Browse creator content"
      variant="marketplace"
    >
      {/* Featured Section */}
      <PlatformCard variant="gold" className="mb-6">
        <div className="flex items-center gap-4">
          <Store className="h-12 w-12 text-[#C9A24A]" />
          <div>
            <h2 className="text-xl font-semibold text-white">Creator Marketplace</h2>
            <p className="text-white/60">Discover and share content packs</p>
          </div>
        </div>
      </PlatformCard>

      {/* Categories */}
      <div className="grid gap-4 sm:grid-cols-3">
        <PlatformCard title="Clip Packs" subtitle="Ready-to-post content" variant="highlight">
          <Package className="h-8 w-8 text-[#9333EA]" />
        </PlatformCard>
        <PlatformCard title="Trending" subtitle="Popular right now" variant="highlight">
          <TrendingUp className="h-8 w-8 text-[#C9A24A]" />
        </PlatformCard>
        <PlatformCard title="New Arrivals" subtitle="Fresh uploads" variant="highlight">
          <Store className="h-8 w-8 text-white/60" />
        </PlatformCard>
      </div>

      {/* Empty State */}
      <div className="mt-8 text-center">
        <p className="text-white/40">Marketplace content coming soon.</p>
      </div>
    </PlatformShell>
  );
}
