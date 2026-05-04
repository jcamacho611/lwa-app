import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Wallet",
  description: "Track balance, manual payout readiness, and approved output value.",
  path: "/wallet",
  keywords: ["creator wallet", "manual payout readiness", "clip workflow ledger", "content rewards workflow"],
});

export default function WalletPage() {
  return (
    <PlatformShell
      title="Wallet"
      subtitle="Earnings and transactions"
      variant="default"
    >
      {/* Balance Card */}
      <PlatformCard variant="gold" className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-white/60">Total Balance</p>
            <p className="text-4xl font-bold text-white mt-1">$0.00</p>
          </div>
          <Wallet className="h-16 w-16 text-[#C9A24A]/40" />
        </div>
      </PlatformCard>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-3">
        <PlatformCard title="Earnings" subtitle="This month" variant="highlight">
          <TrendingUp className="h-8 w-8 text-[#C9A24A]" />
        </PlatformCard>
        <PlatformCard title="Pending" subtitle="Processing" variant="highlight">
          <Clock className="h-8 w-8 text-[#9333EA]" />
        </PlatformCard>
        <PlatformCard title="Transactions" subtitle="History" variant="highlight">
          <Wallet className="h-8 w-8 text-white/60" />
        </PlatformCard>
      </div>

      {/* Empty State */}
      <div className="mt-8 text-center">
        <p className="text-white/40">No transactions yet.</p>
      </div>
    </PlatformShell>
  );
}
