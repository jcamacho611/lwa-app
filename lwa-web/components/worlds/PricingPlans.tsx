import type { BillingPlan, UserEntitlement } from "../../lib/worlds/types";
import { mockEntitlement, mockPlans } from "../../lib/worlds/mock-data";
import { formatMoney } from "../../lib/worlds/utils";
import { SafetyNotice } from "./SafetyNotice";
import { StatPill } from "./StatPill";
import { StatusBadge } from "./StatusBadge";

export function PricingPlans({
  plans = mockPlans,
  entitlement = mockEntitlement,
}: {
  plans?: BillingPlan[];
  entitlement?: UserEntitlement;
}) {
  return (
    <div className="space-y-6">
      <section className="hero-card rounded-[30px] p-6">
        <p className="section-kicker">Plans + Entitlements</p>
        <h2 className="mt-3 text-3xl font-semibold text-ink">
          Credits, marketplace fees, and access levels stay visible before checkout is wired.
        </h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-ink/62">
          Whop and Stripe remain readiness scaffolds. Plan access is tracked server-side so paid features can be gated safely later.
        </p>
      </section>

      <SafetyNotice>
        Plan data is a product foundation, not a live payment promise. Whop entitlement webhooks and Stripe billing must be verified before real purchases are accepted.
      </SafetyNotice>

      <section className="glass-panel rounded-[28px] p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm text-ink/46">Current entitlement</p>
            <h3 className="mt-1 text-2xl font-semibold text-ink">{entitlement.planKey}</h3>
          </div>
          <StatusBadge status={entitlement.status} />
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <StatPill label="Source" value={entitlement.source} />
          <StatPill label="User" value={entitlement.userId} />
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        {plans.map((plan) => (
          <article key={plan.planKey} className="glass-panel rounded-[28px] p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="section-kicker">{plan.planKey}</p>
                <h3 className="mt-2 text-2xl font-semibold text-ink">{plan.name}</h3>
              </div>
              <p className="text-3xl font-semibold text-ink">{formatMoney(plan.monthlyPrice.amount)}</p>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              <StatPill label="Credits" value={plan.monthlyCredits} accent />
              <StatPill label="Fee" value={`${plan.marketplaceFeePercent}%`} />
              <StatPill label="Campaigns" value={plan.maxCampaigns} />
              <StatPill label="UGC" value={plan.maxUgcAssets} />
            </div>

            <div className="mt-5 grid gap-2">
              {plan.features.map((feature) => (
                <p key={feature} className="input-surface rounded-[16px] p-3 text-sm text-ink/62">
                  {feature}
                </p>
              ))}
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
