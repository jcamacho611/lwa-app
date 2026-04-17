import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Vault",
  description:
    "Track ledger movement, payout readiness, and approved output value from the same creator workflow control room.",
  path: "/wallet",
  keywords: ["creator wallet", "payout readiness", "clip workflow ledger", "content rewards workflow"],
});

export default function WalletPage() {
  return <ClipStudio initialSection="wallet" />;
}
