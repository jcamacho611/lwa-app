import { PlatformShell } from "../../components/platform/PlatformShell";
import { PlatformCard } from "../../components/platform/PlatformCard";
import { Upload, FileVideo, Link } from "lucide-react";

export default function UploadPage() {
  return (
    <PlatformShell
      title="Upload"
      subtitle="Add content to process"
      variant="default"
    >
      {/* Upload Options */}
      <div className="grid gap-4 sm:grid-cols-2">
        <PlatformCard
          variant="highlight"
          className="cursor-pointer hover:scale-[1.01] transition-transform"
        >
          <div className="text-center py-8">
            <div className="flex justify-center mb-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#C9A24A]/20">
                <FileVideo className="h-8 w-8 text-[#C9A24A]" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-white">Upload Video</h3>
            <p className="text-white/60 mt-2">Drag or select file</p>
          </div>
        </PlatformCard>

        <PlatformCard
          variant="highlight"
          className="cursor-pointer hover:scale-[1.01] transition-transform"
        >
          <div className="text-center py-8">
            <div className="flex justify-center mb-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#9333EA]/20">
                <Link className="h-8 w-8 text-[#9333EA]" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-white">Paste Link</h3>
            <p className="text-white/60 mt-2">YouTube, TikTok, etc.</p>
          </div>
        </PlatformCard>
      </div>

      {/* Recent Uploads */}
      <h3 className="text-lg font-semibold text-white mt-8 mb-4">Recent Uploads</h3>
      <PlatformCard variant="default">
        <div className="flex items-center gap-3">
          <Upload className="h-5 w-5 text-white/40" />
          <span className="text-white/40">No uploads yet.</span>
        </div>
      </PlatformCard>
    </PlatformShell>
  );
}
