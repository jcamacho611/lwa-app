import {
  leeWuhProductionCandidateAssets,
  leeWuhVisualAssets,
  type LeeWuhVisualAsset,
} from "../../lib/lee-wuh-visual-assets";
import LeeWuhAssetImage from "./LeeWuhAssetImage";

function AssetRoleCard({
  asset,
  imageClassName = "object-cover object-center",
}: {
  asset: LeeWuhVisualAsset;
  imageClassName?: string;
}) {
  return (
    <article className="overflow-hidden rounded-[28px] border border-white/10 bg-black/35 shadow-[0_24px_80px_-56px_rgba(126,58,242,0.7)]">
      <div className="relative aspect-[16/10] border-b border-white/10 bg-black/50">
        <LeeWuhAssetImage
          src={asset.publicPath}
          alt={asset.title}
          className={["h-full w-full", imageClassName].join(" ")}
        />
      </div>

      <div className="p-5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full border border-[#C9A24A]/25 bg-[#C9A24A]/10 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#E9C77B]">
            {asset.role.replaceAll("-", " ")}
          </span>
          <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-white/45">
            {asset.status.replaceAll("-", " ")}
          </span>
        </div>

        <h2 className="mt-4 text-2xl font-semibold text-white">
          {asset.title}
        </h2>
        <p className="mt-3 text-sm leading-7 text-white/62">{asset.note}</p>

        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-[#E9C77B]">
              Use as
            </p>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-white/65">
              {asset.useAs.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-white/35">
              Do not use as
            </p>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-white/48">
              {asset.doNotUseAs.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-5 space-y-3 rounded-2xl border border-white/10 bg-black/35 p-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-white/35">
              Public path
            </p>
            <code className="mt-1 block break-all text-xs text-[#E9C77B]">
              {asset.publicPath}
            </code>
          </div>

          {asset.sourcePath ? (
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-white/35">
                Source path
              </p>
              <code className="mt-1 block break-all text-xs text-white/55">
                {asset.sourcePath}
              </code>
            </div>
          ) : null}
        </div>
      </div>
    </article>
  );
}

function MissingRequirementCard({
  title,
  detail,
}: {
  title: string;
  detail: string;
}) {
  return (
    <div className="rounded-[24px] border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-5">
      <p className="text-sm font-semibold text-[#F2D48A]">{title}</p>
      <p className="mt-2 text-sm leading-6 text-white/58">{detail}</p>
    </div>
  );
}

export default function LeeWuhReferencePanel() {
  return (
    <section className="relative mx-auto max-w-7xl px-6 py-12 text-[#F5F1E8]">
      <div className="max-w-4xl">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
          Lee-Wuh visual system
        </p>
        <h1 className="mt-5 text-[clamp(2.6rem,6vw,5.8rem)] font-black uppercase leading-[0.92] tracking-normal">
          References, not screenshots.
        </h1>
        <p className="mt-6 text-lg leading-8 text-[#B8B3A7]">
          The world, character, sword, and UI composition are separate product
          assets. The live frontend should compose real React surfaces over the
          world background instead of pasting one large image as the app.
        </p>
      </div>

      <div className="mt-10 grid gap-6">
        <AssetRoleCard asset={leeWuhVisualAssets.emptyWorldBackground} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <AssetRoleCard asset={leeWuhVisualAssets.masterCharacterWorld} />
        <AssetRoleCard
          asset={leeWuhVisualAssets.mobileUiReference}
          imageClassName="object-contain object-center p-4"
        />
      </div>

      <section className="mt-8 rounded-[32px] border border-white/10 bg-white/[0.04] p-6">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-white/40">
          Production candidates now present
        </p>
        <div className="mt-5 grid gap-6 lg:grid-cols-2">
          {leeWuhProductionCandidateAssets.map((asset) => (
            <AssetRoleCard
              key={asset.id}
              asset={asset}
              imageClassName="object-contain object-center p-4"
            />
          ))}
        </div>
      </section>

      <section className="mt-8 rounded-[32px] border border-[#7E3AF2]/25 bg-[#7E3AF2]/10 p-6">
        <p className="font-mono text-xs uppercase tracking-[0.28em] text-[#C9A24A]">
          Asset discipline
        </p>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <MissingRequirementCard
            title="Character remains separate"
            detail="Use the no-sword/no-aura Lee-Wuh PNG as the foreground candidate. Do not bake it into every world background."
          />
          <MissingRequirementCard
            title="Sword remains separate"
            detail="Use the Realm Blade prop independently for animation and power states. Do not merge it into the mascot source."
          />
          <MissingRequirementCard
            title="UI remains functional"
            detail="Use the mobile mockup as layout direction only. Build the real generate flow with inputs, buttons, and result states."
          />
        </div>
      </section>
    </section>
  );
}
