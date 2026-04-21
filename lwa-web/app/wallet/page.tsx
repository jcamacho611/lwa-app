import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Wallet",
  description: "Track balance, payout readiness, and approved output value.",
  path: "/wallet",
  keywords: ["creator wallet", "payout readiness", "clip workflow ledger", "content rewards workflow"],
});

export default function WalletPage() {
  return <ClipStudio initialSection="wallet" />;
}
