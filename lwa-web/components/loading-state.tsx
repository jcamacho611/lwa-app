export function LoadingState() {
  return (
    <section className="glass-panel rounded-[1.75rem] px-5 py-10 text-center sm:px-6">
      <div className="mx-auto flex w-full max-w-sm flex-col items-center gap-4">
        <div className="relative flex h-14 w-14 items-center justify-center">
          <div className="absolute inset-0 animate-spin rounded-full border border-white/10 border-t-accent" />
          <div className="h-7 w-7 rounded-full bg-accent/20 blur-sm" />
        </div>
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-white">Analyzing video...</h3>
          <p className="text-sm text-muted">
            Pulling the source, identifying highlights, and packaging the best
            moments for posting.
          </p>
        </div>
      </div>
    </section>
  );
}
