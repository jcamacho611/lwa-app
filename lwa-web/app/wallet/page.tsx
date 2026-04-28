import type { Metadata } from "next";
import { RoutePlaceholder } from "../../components/RoutePlaceholder";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Wallet",
  description: "Track balance, manual payout readiness, and approved output value.",
  path: "/wallet",
  keywords: ["creator wallet", "manual payout readiness", "clip workflow ledger", "content rewards workflow"],
});

export default function WalletPage() {
  return <RoutePlaceholder title="Wallet" />;
}
