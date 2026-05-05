import {
  leeWuhAssetFallback,
  leeWuhBlenderNextSteps,
  leeWuhExpectedPublicPaths,
  leeWuhExpectedSourcePaths,
  leeWuhProductionTargets,
  leeWuhReferencePaths,
  leeWuhSeparatedAssets,
} from "../../lib/lee-wuh-assets";
import LeeWuhAssetImage from "./LeeWuhAssetImage";

type AssetCardProps = {
  title: string;
  description: string;
  publicPath: string;
  sourcePath: string;
  expectedUse: string[];
  kind: string;
  status: string;
};

function AssetCard({
  title,
  description,
  publicPath,
  sourcePath,
  expectedUse,
  kind,
  status,
}: AssetCardProps) {
  return (
    <article className="overflow-hidden rounded-[28px] border border-white/10 bg-white/[0.04] shadow-[0_24px_80px_-56px_rgba(201,162,74,0.6)]">
      <div className="relative aspect-[16/10] border-b border-white/10 bg-black/40">
        <LeeWuhAssetImage
          src={publicPath}
          alt={title}
          className="h-full w-full object-contain p-4"
        />
      </div>

      <div className="p-5">
        <div className="flex flex-wrap items-center gap-2">
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#E9C77B]">
            {kind}
          </p>
          <span className="rounded-full border border-white/10 bg-black/35 px-2 py-1 text-[10px] uppercase tracking-[0.18em] text-white/45">
            {status.replaceAll("-", " ")}
          </span>
        </div>

        <h2 className="mt-3 text-2xl font-semibold text-white">{title}</h2>
        <p className="mt-3 text-sm leading-7 text-white/60">{description}</p>

        <div className="mt-5 space-y-3 rounded-2xl border border-white/10 bg-black/25 p-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-white/35">
              Public path
            </p>
            <code className="mt-1 block break-all text-xs text-[#E9C77B]">
              {publicPath}
            </code>
          </div>

          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-white/35">
              Source path
            </p>
            <code className="mt-1 block break-all text-xs text-white/55">
              {sourcePath}
            </code>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          {expectedUse.map((item) => (
            <span
              key={item}
              className="rounded-full border border-[#C9A24A]/20 bg-[#C9A24A]/10 px-3 py-1 text-xs text-[#E9C77B]"
            >
              {item}
            </span>
          ))}
        </div>
      </div>
    </article>
  );
}

function PathGrid({
  title,
  paths,
  tone = "gold",
}: {
  title: string;
  paths: string[];
  tone?: "gold" | "muted";
}) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
      <p className="font-mono text-xs uppercase tracking-[0.28em] text-white/40">
        {title}
      </p>

      <div className="mt-4 grid gap-3 text-sm md:grid-cols-3">
        {paths.map((path) => (
          <code
            key={path}
            className={[
              "break-all rounded-2xl bg-black/30 p-3",
              tone === "gold" ? "text-[#E9C77B]" : "text-white/60",
            ].join(" ")}
          >
            {path}
          </code>
        ))}
      </div>
    </section>
  );
}

export default function LeeWuhAssetShowcase() {
  return (
    <section className="relative mx-auto max-w-7xl px-6 py-12 text-[#F5F1E8]">
      <div className="max-w-4xl">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
          Lee-Wuh separated assets
        </p>

        <h1 className="mt-5 text-[clamp(3rem,7vw,6.5rem)] font-black uppercase leading-[0.92] tracking-normal">
          Character. World. Sword.
        </h1>

        <p className="mt-6 text-lg leading-8 text-[#B8B3A7]">
          These are the production layers needed to turn Lee-Wuh into a living
          visual agent. The character can move separately from the world. The
          sword can become a prop, item, or animation layer. The environment can
          power the site without baking the character into every background.
        </p>
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-3">
        {leeWuhSeparatedAssets.map((asset) => (
          <AssetCard key={asset.id} {...asset} />
        ))}
      </div>

      <section className="mt-12 rounded-[32px] border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-6">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#E9C77B]">
          Production targets
        </p>

        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {leeWuhProductionTargets.map((target) => (
            <div
              key={target.title}
              className="rounded-2xl border border-white/10 bg-black/25 p-4"
            >
              <h3 className="text-base font-semibold text-white">
                {target.title}
              </h3>
              <p className="mt-2 text-sm leading-6 text-white/55">
                {target.detail}
              </p>
            </div>
          ))}
        </div>
      </section>

      <div className="mt-8 grid gap-8">
        <PathGrid
          title="Expected final public paths"
          paths={[
            leeWuhExpectedPublicPaths.character,
            leeWuhExpectedPublicPaths.background,
            leeWuhExpectedPublicPaths.sword,
          ]}
        />

        <PathGrid
          title="Source/archive paths"
          paths={[
            leeWuhExpectedSourcePaths.character,
            leeWuhExpectedSourcePaths.background,
            leeWuhExpectedSourcePaths.sword,
          ]}
          tone="muted"
        />

        <PathGrid
          title="Reference files captured"
          paths={[
            leeWuhReferencePaths.main,
            leeWuhReferencePaths.turnaround,
            leeWuhReferencePaths.threeDReady,
          ]}
          tone="muted"
        />
      </div>

      <section className="mt-8 rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-white/40">
          Fallback rule
        </p>

        <p className="mt-3 text-sm leading-7 text-white/65">
          If a production image is missing, keep the app build-safe by using the
          existing fallback asset:{" "}
          <code className="text-[#E9C77B]">{leeWuhAssetFallback}</code>.
          Replace placeholders only after the generated PNGs are committed to
          the exact paths listed above.
        </p>
      </section>

      <section className="mt-8 rounded-[28px] border border-white/10 bg-white/[0.04] p-6">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-white/40">
          Next Blender/GLB steps
        </p>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {leeWuhBlenderNextSteps.map((step) => (
            <div
              key={step}
              className="rounded-2xl border border-white/10 bg-black/25 p-4 text-sm leading-6 text-white/65"
            >
              {step}
            </div>
          ))}
        </div>
      </section>
    </section>
  );
}
