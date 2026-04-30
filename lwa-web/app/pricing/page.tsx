import { LwaShell } from "../../components/worlds/LwaShell";
import { PricingPlans } from "../../components/worlds/PricingPlans";
import { getMyEntitlement, listPlans } from "../../lib/worlds/api";
import { mockEntitlement, mockPlans } from "../../lib/worlds/mock-data";

async function getPricingData() {
  try {
    const [plans, entitlement] = await Promise.all([listPlans(), getMyEntitlement()]);
    return { plans: plans.length > 0 ? plans : mockPlans, entitlement };
  } catch {
    return { plans: mockPlans, entitlement: mockEntitlement };
  }
}

export default async function PricingPage() {
  const data = await getPricingData();

  return (
    <LwaShell title="Pricing">
      <PricingPlans {...data} />
    </LwaShell>
  );
}
