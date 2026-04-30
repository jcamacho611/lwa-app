import { SafetyNotice } from "./SafetyNotice";

export function PostJobForm() {
  return (
    <div className="space-y-6">
      <section className="hero-card rounded-[32px] p-6 sm:p-8">
        <p className="section-kicker">Post a Job</p>
        <h2 className="page-title mt-3 text-3xl font-semibold">Create a clipping campaign</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/62">
          This first version is a frontend foundation. Backend persistence comes next. Every campaign should include
          budget, deadline, source, target platform, requirements, and content rights language.
        </p>
      </section>

      <form className="glass-panel grid gap-4 rounded-[28px] p-6">
        <label className="grid gap-2">
          <span className="text-sm font-medium text-ink/70">Campaign title</span>
          <input className="input-surface rounded-[20px] px-4 py-3 text-sm" placeholder="Turn this podcast into 12 TikTok-ready clips" />
        </label>
        <label className="grid gap-2">
          <span className="text-sm font-medium text-ink/70">Description</span>
          <textarea className="input-surface min-h-[128px] rounded-[20px] px-4 py-3 text-sm" placeholder="Explain what kind of clips you want..." />
        </label>
        <div className="grid gap-4 md:grid-cols-3">
          <label className="grid gap-2">
            <span className="text-sm font-medium text-ink/70">Budget</span>
            <input className="input-surface rounded-[20px] px-4 py-3 text-sm" placeholder="$300" />
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-medium text-ink/70">Clip count</span>
            <input className="input-surface rounded-[20px] px-4 py-3 text-sm" placeholder="12" />
          </label>
          <label className="grid gap-2">
            <span className="text-sm font-medium text-ink/70">Deadline</span>
            <input type="date" className="input-surface rounded-[20px] px-4 py-3 text-sm" />
          </label>
        </div>
        <label className="grid gap-2">
          <span className="text-sm font-medium text-ink/70">Requirements</span>
          <textarea className="input-surface min-h-[96px] rounded-[20px] px-4 py-3 text-sm" placeholder="9:16 vertical, captions, hook in first 2 seconds..." />
        </label>
        <label className="flex gap-3 rounded-[18px] border border-[var(--divider)] bg-[var(--surface-inset)] p-4 text-sm leading-7 text-ink/70">
          <input type="checkbox" className="mt-1 h-4 w-4 accent-[var(--gold)]" />
          <span>
            I confirm I own or have rights to the content/source and understand approved work may be reviewed for rights
            and policy compliance.
          </span>
        </label>
        <button type="button" className="primary-button rounded-full px-5 py-3 text-sm font-semibold">
          Save campaign draft
        </button>
      </form>

      <SafetyNotice>
        This first form should save as draft or pending review. Do not release payouts or accept final work without
        review states and audit logs.
      </SafetyNotice>
    </div>
  );
}
