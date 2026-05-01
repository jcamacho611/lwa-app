import Link from "next/link";

type PathStatus = "live" | "preview" | "soon";

const paths: ReadonlyArray<{
  href: string;
  eyebrow: string;
  title: string;
  body: string;
  status: PathStatus;
}> = [
  {
    href: "/generate",
    eyebrow: "Engine",
    title: "Clip Engine",
    body: "One source in. The recommended cut, rendered. The lead clip leads.",
    status: "live",
  },
  {
    href: "/opportunities",
    eyebrow: "Signal",
    title: "Opportunities",
    body: "Curated openings for creators — every path starts with a compliant inquiry.",
    status: "live",
  },
  {
    href: "/realm",
    eyebrow: "World",
    title: "The Realm",
    body: "The Seven Agents. In-world guides. Tomorrow, your base models.",
    status: "live",
  },
  {
    href: "/marketplace",
    eyebrow: "Trade",
    title: "Marketplace",
    body: "Where renders meet buyers. Listings ledger and proof of work.",
    status: "preview",
  },
  {
    href: "/social",
    eyebrow: "Command",
    title: "Social",
    body: "One panel for every channel. No fake posting until the rails are live.",
    status: "preview",
  },
  {
    href: "/proof",
    eyebrow: "Ledger",
    title: "Proof",
    body: "On-chain receipts of rendered output. Roadmap, not theater.",
    status: "soon",
  },
  {
    href: "/operator",
    eyebrow: "Founder",
    title: "Operator",
    body: "The view from the desk. Council ops, system health, queues.",
    status: "live",
  },
  {
    href: "/history",
    eyebrow: "History",
    title: "Vault",
    body: "Every render, every strategy note, every link you made money on.",
    status: "live",
  },
] as const;

const statusTone: Record<PathStatus, string> = {
  live: "text-[#5BA88A] border-[#5BA88A]/30 bg-[#5BA88A]/10",
  preview: "text-[#D9A441] border-[#D9A441]/30 bg-[#D9A441]/10",
  soon: "text-[#7A7568] border-[#23232C] bg-[#1D1D24]",
};

const statusLabel: Record<PathStatus, string> = {
  live: "Live",
  preview: "Preview",
  soon: "Soon",
};

export default function PathPortal() {
  return (
    <section className="relative py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex items-end justify-between gap-6 flex-wrap">
          <div>
            <div className="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-[#7A7568]">
              Path Portal
            </div>
            <h2 className="mt-2 text-[clamp(2rem,4vw,3.25rem)] font-semibold leading-[1.05] tracking-[-0.015em] text-[#F5F1E8]">
              Pick the door.
            </h2>
          </div>
          <p className="max-w-md text-[#B8B3A7]">
            Every path is the same product, framed for a different job. The
            center of the screen stays sacred.
          </p>
        </div>

        <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {paths.map((p) => (
            <Link
              key={p.href}
              href={p.href}
              className="group relative block rounded-[14px] p-6 bg-[#16161B] ring-1 ring-[#23232C] transition-all duration-200 hover:ring-[#C9A24A]/40 hover:-translate-y-px hover:shadow-[0_0_0_1px_rgba(201,162,74,0.18),0_18px_60px_-24px_rgba(201,162,74,0.35)]"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-[#7A7568]">
                  {p.eyebrow}
                </span>
                <span
                  className={[
                    "font-mono text-[0.65rem] uppercase tracking-[0.16em] px-2 py-0.5 rounded-full border",
                    statusTone[p.status],
                  ].join(" ")}
                >
                  {statusLabel[p.status]}
                </span>
              </div>
              <h3 className="mt-6 text-3xl font-semibold tracking-[-0.01em] text-[#F5F1E8] transition-colors duration-200 group-hover:text-[#E9C77B]">
                {p.title}
              </h3>
              <p className="mt-3 text-[0.95rem] leading-relaxed text-[#B8B3A7]">
                {p.body}
              </p>
              <div className="mt-6 flex items-center gap-2 text-[#B8B3A7] transition-colors duration-200 group-hover:text-[#E9C77B]">
                <span className="text-sm font-medium">Enter</span>
                <span
                  aria-hidden
                  className="transition-transform duration-200 group-hover:translate-x-1"
                >
                  →
                </span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
