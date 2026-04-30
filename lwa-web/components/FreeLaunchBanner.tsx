export function FreeLaunchBanner() {
  if (process.env.NEXT_PUBLIC_FREE_LAUNCH_MODE !== "true") {
    return null;
  }

  return (
    <div className="relative z-[60] border-b border-emerald-300/20 bg-[#07130f]/95 px-4 py-2 text-center text-xs font-semibold text-emerald-100 shadow-lg shadow-black/20">
      Free launch mode is open. Upload or paste a source and generate a ranked clip package without signing in.
    </div>
  );
}
