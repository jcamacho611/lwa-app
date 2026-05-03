import {
  CompanyOsShell,
  SectionHeader,
  StatusBadge,
} from "../../components/company-os/CompanyOsShell";
import { revenuePipeline, revenueTiers } from "../../lib/company-os";

const scripts = [
  {
    title: "Short outreach",
    body: "We built LWA, an AI creator engine that turns long videos into short-form clip packs with hooks, captions, timestamps, and posting angles. Want a 10-minute demo?",
  },
  {
    title: "Creator angle",
    body: "Send us one public video URL. We'll show how LWA finds the strongest moments and packages them for TikTok, Instagram, YouTube, and Facebook.",
  },
  {
    title: "Investor angle",
    body: "LWA is becoming a full creator company OS: clipping engine, brand world, campaign marketplace, revenue workflows, and automation dashboard.",
  },
];

export default function RevenuePage() {
  return (
    <CompanyOsShell
      activeHref="/revenue"
      eyebrow="Revenue OS"
      title="The money movement dashboard for Whop, sales, investors, demos, and onboarding."
      description="This route turns revenue from scattered notes into an operating surface: pricing, pipeline, scripts, demos, and next actions."
    >
      <div className="space-y-12">
        <section>
          <SectionHeader
            eyebrow="Pricing"
            title="Launch tier hypotheses"
            description="These are v0 working tiers. Adjust after Whop checkout and customer feedback."
          />
          <div className="grid gap-5 lg:grid-cols-3">
            {revenueTiers.map((tier) => (
              <div
                key={tier.name}
                className="rounded-[26px] border border-white/10 bg-white/[0.04] p-6"
              >
                <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#C9A24A]">
                  {tier.target}
                </p>
                <h2 className="mt-4 text-2xl font-semibold text-white">
                  {tier.name}
                </h2>
                <p className="mt-2 text-3xl font-bold text-[#E9C77B]">
                  {tier.price}
                </p>
                <p className="mt-4 text-sm leading-6 text-white/65">
                  {tier.promise}
                </p>
                <ul className="mt-5 space-y-2">
                  {tier.included.map((item) => (
                    <li key={item} className="text-sm text-white/70">
                      • {item}
                    </li>
                  ))}
                </ul>
                <div className="mt-5 rounded-2xl border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-4">
                  <p className="font-mono text-xs uppercase tracking-[0.2em] text-[#E9C77B]">
                    Next action
                  </p>
                  <p className="mt-2 text-sm text-white/75">{tier.nextAction}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section>
          <SectionHeader
            eyebrow="Pipeline"
            title="Revenue motion cards"
          />
          <div className="grid gap-4 md:grid-cols-2">
            {revenuePipeline.map((item) => (
              <div
                key={item.title}
                className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5"
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {item.title}
                    </h3>
                    <p className="mt-1 text-sm text-white/45">{item.owner}</p>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
                <p className="mt-4 text-sm leading-6 text-white/65">
                  {item.nextAction}
                </p>
                <p className="mt-3 text-xs uppercase tracking-[0.2em] text-[#E9C77B]">
                  {item.value}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <SectionHeader
            eyebrow="Scripts"
            title="Copy/paste selling scripts"
            description="Keep this simple. The goal is demos and payments, not perfect copy."
          />
          <div className="grid gap-4 lg:grid-cols-3">
            {scripts.map((script) => (
              <div
                key={script.title}
                className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5"
              >
                <h3 className="text-lg font-semibold text-white">
                  {script.title}
                </h3>
                <p className="mt-3 text-sm leading-7 text-white/70">
                  {script.body}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-[28px] border border-[#C9A24A]/20 bg-[#C9A24A]/10 p-6">
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#E9C77B]">
            Demo flow
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            One public URL → clip pack → hooks/captions → close.
          </h2>
          <ol className="mt-5 grid gap-3 text-sm leading-6 text-white/75 md:grid-cols-2">
            <li>1. Ask for one public video URL.</li>
            <li>2. Generate clip pack in `/generate` or Command Center.</li>
            <li>3. Show best clip first and explain why.</li>
            <li>4. Copy hook/caption/CTA package.</li>
            <li>5. Send Whop checkout link.</li>
            <li>6. Follow up with &quot;want us to process your next source?&quot;</li>
          </ol>
        </section>
      </div>
    </CompanyOsShell>
  );
}
