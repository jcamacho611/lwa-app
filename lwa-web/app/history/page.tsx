import type { Metadata } from "next";
import { ClipStudio } from "../../components/clip-studio";
import { buildPageMetadata } from "../../lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Archive",
  description: "Reopen saved clip packs and keep review continuity intact.",
  path: "/history",
  keywords: ["clip archive", "saved clip packs", "history workflow", "clip history"],
});

export default function HistoryPage() {
  return (
    <PlatformShell
      title="History"
      subtitle="Your past work"
      variant="default"
    >
      {/* Stats Row */}
      <div className="grid gap-4 sm:grid-cols-3 mb-6">
        <PlatformCard title="Total Clips" subtitle="All time" variant="highlight">
          <History className="h-8 w-8 text-[#C9A24A]" />
        </PlatformCard>
        <PlatformCard title="Recent" subtitle="Last 30 days" variant="highlight">
          <Clock className="h-8 w-8 text-[#9333EA]" />
        </PlatformCard>
        <PlatformCard title="Favorites" subtitle="Saved clips" variant="highlight">
          <Star className="h-8 w-8 text-white/60" />
        </PlatformCard>
      </div>

      {/* Empty State */}
      <PlatformCard variant="default" className="text-center py-12">
        <History className="h-16 w-16 text-white/20 mx-auto mb-4" />
        <p className="text-white/40">No history yet.</p>
        <p className="text-white/30 text-sm mt-2">Generated clips will appear here.</p>
      </PlatformCard>
    </PlatformShell>
  );
}
