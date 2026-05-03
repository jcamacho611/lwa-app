import Image from "next/image";
import {
  CompanyOsShell,
  SectionHeader,
  StatusBadge,
} from "../../components/company-os/CompanyOsShell";
import { brandAssets } from "../../lib/company-os";

const mascotRules = [
  "Use LWA for the product, company, app, repo, backend, frontend, and investor materials.",
  "Use Lee-Wuh for mascot, merch, loading states, empty states, social posts, and brand-world surfaces.",
  "Keep Lee-Wuh at the edge of the product experience. Do not block source input, results, or exports.",
  "The mascot should support creator clarity, not replace the actual clipping promise.",
  "The visual language is Afro-futurist, anime-final-boss, cute chibi, flashy, jeweled, and premium.",
];

const roadmap = [
  {
    title: "Static PNG system",
    status: "ready" as const,
    detail: "Use the approved 16:9 asset for homepage, Whop, and social.",
  },
  {
    title: "Avatar crops",
    status: "queued" as const,
    detail: "Create square, transparent, and small loading-state versions.",
  },
  {
    title: "Blender blockout",
    status: "queued" as const,
    detail: "Create Lee-Wuh model with chibi proportions, dreads, jewelry, hoodie, and aura rings.",
  },
  {
    title: "Web GLB",
    status: "queued" as const,
    detail: "Export optimized `.glb` for lightweight 3D web use.",
  },
  {
    title: "Rive states",
    status: "queued" as const,
    detail: "Idle, analyzing, rendering, complete, victory, and error states.",
  },
];

export default function BrandWorldPage() {
  return (
    <CompanyOsShell
      activeHref="/brand-world"
      eyebrow="Lee-Wuh Brand World"
      title="The mascot universe that makes LWA unforgettable without hiding the product."
      description="Lee-Wuh is the brand character and cultural layer. LWA remains the product: the creator engine that turns sources into clips, hooks, captions, and packaging."
    >
      <div className="space-y-12">
        <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
            <SectionHeader
              eyebrow="Character profile"
              title="Lee-Wuh // The Last Creator"
              description="A fictional furry chibi anime-final-boss mascot with dreadlocks, jewelry, African/Japanese fusion, and an American streetwear twist."
            />

            <div className="grid gap-4 md:grid-cols-2">
              <ProfileItem label="Role" value="Mascot / brand guardian" />
              <ProfileItem label="Tone" value="Cute, powerful, premium, flashy" />
              <ProfileItem label="Palette" value="Black, gold, purple, charcoal, white" />
              <ProfileItem label="Promise" value="Final boss of lazy content" />
            </div>

            <div className="mt-6 rounded-2xl border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-5">
              <p className="font-mono text-xs uppercase tracking-[0.2em] text-[#E9C77B]">
                Core line
              </p>
              <p className="mt-3 text-xl font-semibold text-white">
                Feed Lee-Wuh one source. Let LWA find the moments worth posting.
              </p>
            </div>
          </div>

          <div className="overflow-hidden rounded-[28px] border border-[#C9A24A]/25 bg-[#111116]">
            <Image
              src="/brand/lee-wuh-hero-16x9.png"
              alt="Lee-Wuh mascot hero"
              width={1600}
              height={900}
              className="h-full min-h-[320px] w-full object-cover"
            />
          </div>
        </section>

        <section>
          <SectionHeader
            eyebrow="Mascot rules"
            title="Use the character without confusing the product"
          />
          <div className="grid gap-4 md:grid-cols-2">
            {mascotRules.map((rule) => (
              <div
                key={rule}
                className="rounded-[20px] border border-white/10 bg-white/[0.04] p-5 text-sm leading-7 text-white/70"
              >
                {rule}
              </div>
            ))}
          </div>
        </section>

        <section>
          <SectionHeader
            eyebrow="Assets"
            title="Brand asset paths"
            description="These paths are the official places Windsurf should use or create assets."
          />
          <div className="grid gap-4 md:grid-cols-2">
            {brandAssets.map((asset) => (
              <div
                key={asset.path}
                className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5"
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold text-white">
                    {asset.name}
                  </h3>
                  <StatusBadge status={asset.status} />
                </div>
                <p className="mt-3 font-mono text-xs text-[#E9C77B]">
                  {asset.path}
                </p>
                <p className="mt-3 text-sm leading-6 text-white/60">
                  {asset.use}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <SectionHeader
            eyebrow="3D / Rive roadmap"
            title="Turn Lee-Wuh into a real app character"
          />
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {roadmap.map((item) => (
              <div
                key={item.title}
                className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5"
              >
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold text-white">
                    {item.title}
                  </h3>
                  <StatusBadge status={item.status} />
                </div>
                <p className="mt-3 text-sm leading-6 text-white/60">
                  {item.detail}
                </p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </CompanyOsShell>
  );
}

function ProfileItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-white/40">
        {label}
      </p>
      <p className="mt-2 text-sm font-semibold text-white">{value}</p>
    </div>
  );
}
