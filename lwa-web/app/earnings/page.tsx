import { EconomyLedger } from "../../components/worlds/EconomyLedger";
import { LwaShell } from "../../components/worlds/LwaShell";

export default function EarningsPage() {
  return (
    <LwaShell title="Earnings">
      <EconomyLedger />
    </LwaShell>
  );
}
