import Link from "next/link";

const surfaces = [
  { title: "Command Center", href: "/generate", detail: "Run the creator clipping engine and review outputs." },
  { title: "Council", href: "/company-os#council", detail: "Senior expert operating roles and next actions." },
  { title: "Brand World", href: "/company-os#brand-world", detail: "Lee-Wuh mascot system, assets, and 3D roadmap." },
  { title: "Revenue OS", href: "/company-os#revenue", detail: "Whop, pricing, sales, demos, investor and onboarding motion." },
  { title: "Campaigns", href: "/campaigns", detail: "Campaign briefs, submissions, reviews, and exports." },
  { title: "Operations", href: "https://github.com/jcamacho611/lwa-app/issues/146", detail: "Master execution gate: no docs-only, no stalling." },
];

const council = [
  "Founder / Operator-in-Chief",
  "CEO Execution Strategist",
  "CTO / Principal Architect",
  "Frontend Creative Director",
  "Backend Systems Lead",
  "AI/ML Clipping Intelligence Lead",
  "Video Systems Engineer",
  "3D / Blender / Rive Creative Technologist",
  "Brand Universe Director",
  "Whop / Revenue Lead",
  "Investor Relations Lead",
  "Sales Operations Lead",
  "QA / Release Lead",
  "Automation / Windsurf Release Operator",
];

const revenue = [
  "Confirm Whop checkout and product page copy.",
  "Package Starter, Pro, and Agency tiers.",
  "Use one public URL demo to close customers.",
  "Track investor targets, demos, and follow-ups.",
];

export default function CompanyOsPage() {
  return (
    <main className="min-h-screen bg-[#08080A] text-[#F5F1E8]">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-[-12%] top-[-12%] h-[520px] w-[520px] rounded-full bg-[#C9A24A]/10 blur-[120px]" />
        <div className="absolute right-[-12%] top-[18%] h-[520px] w-[520px] rounded-full bg-purple-600/15 blur-[130px]" />
      </div>

      <div className="relative z-10 mx-auto max-w-7xl px-6 py-8">
        <header className="flex flex-col gap-4 rounded-[24px] border border-white/10 bg-white/[0.04] p-4 md:flex-row md:items-center md:justify-between">
          <Link href="/" className="flex items-center gap-3">
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-[#16161B] ring-1 ring-[#2E2E38]">
              <span className="text-lg font-bold text-[#C9A24A]">L</span>
            </span>
            <div>
              <p className="text-sm font-semibold text-white">LWA Company OS</p>
              <p className="text-xs text-white/45">lee-wuh operating layer</p>
            </div>
          </Link>
          <nav className="flex flex-wrap gap-2">
            <Link className="rounded-full border border-[#C9A24A]/30 bg-[#C9A24A]/15 px-3 py-2 text-xs font-semibold text-[#E9C77B]" href="/company-os">Company OS</Link>
            <Link className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-white/65" href="/generate">Generate</Link>
            <Link className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-white/65" href="/campaigns">Campaigns</Link>
          </nav>
        </header>

        <section className="py-12">
          <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">LWA Company OS</p>
          <h1 className="mt-4 max-w-5xl text-[clamp(2.5rem,6vw,5.6rem)] font-semibold leading-[1.02] tracking-[-0.04em]">
            One system for the app, company, brand, money, council, and execution.
          </h1>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-[#B8B3A7]">
            LWA is the full creator company operating system: clipping engine, Lee-Wuh brand world, revenue motion, campaigns, marketplace, expert council, automation, and release control.
          </p>
        </section>

        <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {surfaces.map((surface) => (
            <Link key={surface.title} href={surface.href} className="rounded-[24px] border border-white/10 bg-white/[0.04] p-6 transition hover:-translate-y-0.5 hover:border-[#C9A24A]/35 hover:bg-[#C9A24A]/[0.06]">
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#C9A24A]">Surface</p>
              <h2 className="mt-3 text-2xl font-semibold text-white">{surface.title}</h2>
              <p className="mt-3 text-sm leading-6 text-white/60">{surface.detail}</p>
              <p className="mt-5 text-sm font-semibold text-[#E9C77B]">Open →</p>
            </Link>
          ))}
        </section>

        <section id="council" className="mt-14 rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
          <p className="font-mono text-xs uppercase tracking-[0.25em] text-[#C9A24A]">Council OS</p>
          <h2 className="mt-3 text-3xl font-semibold text-white">Senior expert council</h2>
          <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {council.map((role) => <div key={role} className="rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-white/75">{role}</div>)}
          </div>
        </section>

        <section id="brand-world" className="mt-8 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-[28px] border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-6">
            <p className="font-mono text-xs uppercase tracking-[0.25em] text-[#E9C77B]">Lee-Wuh Brand World</p>
            <h2 className="mt-3 text-3xl font-semibold text-white">Mascot, not replacement.</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">Use LWA for the company/product. Use Lee-Wuh for mascot, loading, empty states, social, merch, and brand-world energy.</p>
          </div>
          <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
            <p className="font-mono text-xs uppercase tracking-[0.25em] text-[#C9A24A]">3D Roadmap</p>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-white/70">
              <li>• Static SVG/PNG hero live first.</li>
              <li>• Add avatar, loading, and empty-state crops.</li>
              <li>• Build Blender blockout and export optimized GLB.</li>
              <li>• Add Rive states: idle, analyzing, rendering, complete, victory.</li>
            </ul>
          </div>
        </section>

        <section id="revenue" className="mt-8 rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
          <p className="font-mono text-xs uppercase tracking-[0.25em] text-[#C9A24A]">Revenue OS</p>
          <h2 className="mt-3 text-3xl font-semibold text-white">Money movement next actions</h2>
          <div className="mt-6 grid gap-3 md:grid-cols-2">
            {revenue.map((item) => <div key={item} className="rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-white/75">• {item}</div>)}
          </div>
        </section>
      </div>
    </main>
  );
}
