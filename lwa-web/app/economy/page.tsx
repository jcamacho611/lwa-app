import { LwaShell } from "../../components/worlds/LwaShell";
import { WalletView } from "../../components/worlds/WalletView";

export default function EconomyPage() {
  return (
    <LwaShell title="Economy Ledger">
      <WalletView />
    </LwaShell>
  );
}
