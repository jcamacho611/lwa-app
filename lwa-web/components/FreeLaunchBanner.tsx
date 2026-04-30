import Link from "next/link";

export function FreeLaunchBanner() {
  if (process.env.NEXT_PUBLIC_FREE_LAUNCH_MODE !== "true") {
    return null;
  }

  return (
    <aside className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-black/80 px-4 py-3 text-center text-sm text-white shadow-[0_12px_40px_rgba(0,0,0,0.35)] backdrop-blur-xl">
      <span className="font-semibold text-white">Free launch mode is live.</span>{" "}
      <span className="text-white/72">Generate and review LWA clip packages while public launch access is open.</span>{" "}
      <Link href="/generate" className="font-semibold text-white underline decoration-white/35 underline-offset-4 hover:decoration-white">
        Forge clips
      </Link>
    </aside>
  );
}
