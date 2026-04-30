import { LwaShell } from "../../components/worlds/LwaShell";
import { UgcStudio } from "../../components/worlds/UgcStudio";
import { listUgcAssets } from "../../lib/worlds/api";
import { mockUgcAssets } from "../../lib/worlds/mock-data";

async function getUgcAssets() {
  try {
    const assets = await listUgcAssets();
    return assets.length > 0 ? assets : mockUgcAssets;
  } catch {
    return mockUgcAssets;
  }
}

export default async function UgcPage() {
  const assets = await getUgcAssets();

  return (
    <LwaShell title="UGC Studio">
      <UgcStudio assets={assets} />
    </LwaShell>
  );
}
