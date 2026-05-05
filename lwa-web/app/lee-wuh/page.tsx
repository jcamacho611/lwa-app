import Link from "next/link";
import LeeWuh3DViewer from "../../components/lee-wuh/LeeWuh3DViewer";
import LivingLeeWuhAgent from "../../components/lee-wuh/LivingLeeWuhAgent";
import LeeWuhWorldBackdrop from "../../components/lee-wuh/LeeWuhWorldBackdrop";

const routes = [
  { label: "Generate clips", href: "/generate", detail: "Paste one source and let LWA find the strongest clips." },
  { label: "Marketplace", href: "/marketplace", detail: "Find paid creative work, campaign tasks, and creator offers." },
  { label: "Post a job", href: "/marketplace/post-job", detail: "Create a prepaid or partially paid task for creators." },
  { label: "Campaigns", href: "/campaigns", detail: "Package briefs, submissions, review, and exports." },
  { label: "Enter realm", href: "/realm", detail: "Open the game/world layer around Lee-Wuh." },
  { label: "Asset pipeline", href: "/lee-wuh/assets", detail: "Inspect separated character, world, and sword layers." },
  { label: "Company OS", href: "/company-os", detail: "See the full LWA operating system." },
];

const buildTargets = [
  "Floating clickable living agent",
  "Speech bubble with route choices",
  "World backdrop matching black/gold/purple concept art",
  "Blender source pipeline",
  "Web GLB target for future full 3D body",
  "Marketplace guidance for money-flow actions",
];

export default function LeeWuhLivingAgentPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#050506] text-[#F5F1E8]">
      <LeeWuhWorldBackdrop />
      <LivingLeeWuhAgent />

      <section className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col justify-center px-6 py-20">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">Pronounced lee-wuh</p>
        <h1 className="mt-5 max-w-5xl text-[clamp(3rem,8vw,7.5rem)] font-black uppercase leading-[0.9] tracking-[-0.06em] text-[#F5F1E8]">
          Lee-Wuh is the living agent.
        </h1>
        <p className="mt-7 max-w-3xl text-lg leading-8 text-[#B8B3A7]">
          This is the first live shell for Lee-Wuh as LWA’s clickable visual intelligence: part mascot, part guide, part marketplace router, part world portal. The full Blender/GLB body upgrades behind this shell next.
        </p>

        <div className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 transition hover:-translate-y-1 hover:border-[#C9A24A]/40 hover:bg-[#C9A24A]/10"
            >
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-[#E9C77B]">Action</p>
              <h2 className="mt-3 text-xl font-semibold text-white">{route.label}</h2>
              <p className="mt-2 text-sm leading-6 text-white/55">{route.detail}</p>
            </Link>
          ))}
        </div>

        <section className="mt-12 rounded-[32px] border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-6">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#E9C77B]">Build targets</p>
          <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {buildTargets.map((target) => (
              <div key={target} className="rounded-2xl border border-white/10 bg-black/25 p-4 text-sm text-white/75">
                • {target}
              </div>
            ))}
          </div>
        </section>

        <section className="mt-12">
          <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#E9C77B]">3D shell</p>
          <h2 className="mt-3 text-3xl font-semibold text-white">GLB-ready viewer with fallback</h2>
          <div className="mt-5">
            <LeeWuh3DViewer />
          </div>
        </section>
      </section>
    </main>
  );
}
