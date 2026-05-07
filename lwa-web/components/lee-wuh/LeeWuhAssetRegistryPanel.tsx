"use client";

import {
  getApprovedLeeWuhAssets,
  getLeeWuhAssetsByKind,
  leeWuhAssetRegistry,
  type LeeWuhAssetKind,
  validateLeeWuhAssetLayerTruth,
} from "../../lib/lee-wuh-asset-registry";

const registryKinds: LeeWuhAssetKind[] = [
  "character",
  "sword",
  "background",
  "aura",
  "combined_reference",
  "blender_source",
  "glb_runtime",
  "spine_source",
  "ui_reference",
];

function kindLabel(kind: LeeWuhAssetKind) {
  return kind.replaceAll("_", " ");
}

function AssetCard({ kind }: { kind: LeeWuhAssetKind }) {
  const items = getLeeWuhAssetsByKind(kind);

  return (
    <section className="rounded-[24px] border border-white/10 bg-black/25 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-white/35">
            {kindLabel(kind)}
          </p>
          <h3 className="mt-2 text-xl font-semibold text-white">
            {items.length} asset{items.length === 1 ? "" : "s"}
          </h3>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {items.map((asset) => {
          const validation = validateLeeWuhAssetLayerTruth(asset);
          return (
            <article
              key={asset.id}
              className="rounded-2xl border border-white/10 bg-white/[0.04] p-4"
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full border border-[#C9A24A]/25 bg-[#C9A24A]/10 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-[#E9C77B]">
                  {asset.status}
                </span>
                <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-white/45">
                  {validation.safety}
                </span>
                {validation.isValid ? (
                  <span className="rounded-full border border-emerald-400/25 bg-emerald-400/10 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-emerald-200">
                    valid
                  </span>
                ) : (
                  <span className="rounded-full border border-amber-400/25 bg-amber-400/10 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-amber-200">
                    mixed
                  </span>
                )}
              </div>
              <h4 className="mt-3 text-lg font-semibold text-white">{asset.title}</h4>
              <p className="mt-2 text-sm leading-6 text-white/60">{asset.description}</p>

              <div className="mt-4 grid gap-2 text-xs text-white/58 sm:grid-cols-2">
                <div>character: {asset.hasCharacter ? "yes" : "no"}</div>
                <div>sword: {asset.hasSword ? "yes" : "no"}</div>
                <div>aura: {asset.hasAura ? "yes" : "no"}</div>
                <div>transparent: {asset.transparent ? "yes" : "no"}</div>
                <div>runtime ready: {asset.runtimeReady ? "yes" : "no"}</div>
                <div>blender ready: {asset.blenderReady ? "yes" : "no"}</div>
                <div>spine ready: {asset.spineReady ? "yes" : "no"}</div>
              </div>

              <div className="mt-4 rounded-2xl border border-white/10 bg-black/25 p-3">
                <p className="text-[10px] uppercase tracking-[0.2em] text-white/35">
                  Accepted use
                </p>
                <p className="mt-2 text-sm leading-6 text-white/65">
                  {asset.acceptedUse.join(", ")}
                </p>
              </div>

              {validation.warnings.length ? (
                <div className="mt-4 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-3">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-amber-200">
                    Layer warnings
                  </p>
                  <ul className="mt-2 space-y-1 text-sm leading-6 text-amber-50/80">
                    {validation.warnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              <div className="mt-4 space-y-2 text-xs text-white/45">
                <div className="break-all">public: {asset.publicPath}</div>
                <div className="break-all">source: {asset.sourcePath}</div>
                <div>rejection risk: {asset.rejectionRisk}</div>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

export default function LeeWuhAssetRegistryPanel() {
  const approvedCount = getApprovedLeeWuhAssets().length;
  const runtimeReadyCount = leeWuhAssetRegistry.filter((asset) => asset.runtimeReady).length;

  return (
    <section className="relative mx-auto max-w-7xl px-6 py-12 text-[#F5F1E8]">
      <div className="max-w-4xl">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-[#C9A24A]">
          Asset registry engine
        </p>
        <h2 className="mt-5 text-[clamp(2.4rem,5vw,5rem)] font-black uppercase leading-[0.92] tracking-normal text-white">
          Layer truth, runtime safety, source discipline.
        </h2>
        <p className="mt-6 text-base leading-8 text-white/62">
          This registry keeps character, sword, background, aura, Blender,
          GLB, Spine, and reference assets separated so the frontend can
          compose them safely.
        </p>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">
            approved
          </p>
          <p className="mt-2 text-3xl font-black text-white">{approvedCount}</p>
        </div>
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">
            runtime ready
          </p>
          <p className="mt-2 text-3xl font-black text-white">{runtimeReadyCount}</p>
        </div>
        <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-white/35">
            total assets
          </p>
          <p className="mt-2 text-3xl font-black text-white">{leeWuhAssetRegistry.length}</p>
        </div>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-2">
        {registryKinds.map((kind) => (
          <AssetCard key={kind} kind={kind} />
        ))}
      </div>
    </section>
  );
}

