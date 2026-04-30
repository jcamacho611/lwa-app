import { LwaShell } from "../../../components/worlds/LwaShell";
import { SafetyNotice } from "../../../components/worlds/SafetyNotice";

export default function CreateUgcPage() {
  return (
    <LwaShell title="Create UGC Asset">
      <div className="space-y-6">
        <form className="hero-card grid gap-4 p-6">
          <label className="grid gap-2">
            <span className="text-sm text-ink/62">Asset title</span>
            <input className="input-surface px-4 py-3 text-sm" placeholder="Gold Thread Hook Pack" />
          </label>

          <label className="grid gap-2">
            <span className="text-sm text-ink/62">Asset type</span>
            <select className="input-surface px-4 py-3 text-sm">
              <option>Hook Pack</option>
              <option>Caption Pack</option>
              <option>Quest Template</option>
              <option>Campaign Template</option>
              <option>Prompt Pack</option>
              <option>Cosmetic Concept</option>
            </select>
          </label>

          <label className="grid gap-2">
            <span className="text-sm text-ink/62">Description</span>
            <textarea
              className="input-surface min-h-32 px-4 py-3 text-sm"
              placeholder="Describe the asset and how creators use it..."
            />
          </label>

          <label className="flex gap-3 rounded-2xl border border-[var(--divider)] bg-[var(--surface-inset)] p-4 text-sm leading-6 text-ink/70">
            <input type="checkbox" className="mt-1" />
            <span>
              I confirm this asset is original or properly licensed and does not copy existing characters,
              brands, worlds, or protected IP.
            </span>
          </label>

          <button type="button" className="primary-button justify-center px-5 py-3 text-sm">
            Save UGC draft
          </button>
        </form>

        <SafetyNotice>
          UGC publishing and selling should require review before marketplace availability.
        </SafetyNotice>
      </div>
    </LwaShell>
  );
}
