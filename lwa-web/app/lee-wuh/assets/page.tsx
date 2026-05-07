import Link from "next/link";
import type { Metadata } from "next";
import LeeWuhAssetShowcase from "../../../components/lee-wuh/LeeWuhAssetShowcase";
import LeeWuhAssetRegistryPanel from "../../../components/lee-wuh/LeeWuhAssetRegistryPanel";
import LeeWuhEngineMapPanel from "../../../components/lee-wuh/LeeWuhEngineMapPanel";
import LeeWuhExperienceController from "../../../components/lee-wuh/LeeWuhExperienceController";
import LwaRecoveryPanel from "../../../components/recovery/LwaRecoveryPanel";
import LeeWuhLayeredStage from "../../../components/lee-wuh/LeeWuhLayeredStage";
import LeeWuhReferencePanel from "../../../components/lee-wuh/LeeWuhReferencePanel";
import { PlatformShell } from "../../../components/platform/PlatformShell";
import { buildPageMetadata } from "../../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Lee-Wuh Separated Assets | LWA",
  description:
    "Character, world, and Realm Blade production paths for the Lee-Wuh living agent asset pipeline.",
  path: "/lee-wuh/assets",
  keywords: ["Lee-Wuh", "LWA brand assets", "living agent", "Blender", "GLB"],
});

export default function LeeWuhAssetsPage() {
  return (
    <PlatformShell
      title="Lee-Wuh Asset Pipeline"
      subtitle="Separated production layers for the living visual agent."
      variant="game"
    >
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <Link
          href="/brand-world"
          className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white/70 transition hover:border-[#C9A24A]/40 hover:text-white"
        >
          Back to Brand World
        </Link>

        <div className="flex flex-wrap gap-3">
          <Link
            href="/realm"
            className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white/70 transition hover:border-[#C9A24A]/40 hover:text-white"
          >
            Realm
          </Link>
          <Link
            href="/marketplace"
            className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-white/70 transition hover:border-[#C9A24A]/40 hover:text-white"
          >
            Marketplace
          </Link>
          <Link
            href="/generate"
            className="rounded-full border border-[#C9A24A]/30 bg-[#C9A24A]/10 px-4 py-2 text-sm text-[#E9C77B] transition hover:bg-[#C9A24A]/20"
          >
            Generate clips
          </Link>
        </div>
      </div>

      <LeeWuhReferencePanel />

      <LeeWuhEngineMapPanel />

      <LeeWuhExperienceController />

      <LeeWuhAssetRegistryPanel />

      <LwaRecoveryPanel />

      <div className="mt-8">
        <LeeWuhLayeredStage />
      </div>

      <LeeWuhAssetShowcase />
    </PlatformShell>
  );
}
