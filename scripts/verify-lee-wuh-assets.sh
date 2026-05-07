#!/usr/bin/env bash
set -euo pipefail

REQUIRED=(
  "brand-source/lee-wuh/references/lee-wuh-empty-world-background.png"
  "brand-source/lee-wuh/references/lee-wuh-master-character-world.png"
  "brand-source/lee-wuh/references/lee-wuh-mobile-ui-reference.png"
  "brand-source/lee-wuh/cutouts/lee-wuh-transparent-with-sword-aura.png"
  "brand-source/lee-wuh/cutouts/lee-wuh-transparent-aura.png"
  "brand-source/lee-wuh/cutouts/lee-wuh-transparent-clean.png"
  "brand-source/lee-wuh/cutouts/lee-wuh-sword-transparent-aura.png"
  "lwa-web/public/brand/lee-wuh/backgrounds/lee-wuh-empty-world-background.png"
  "lwa-web/public/brand/lee-wuh/references/lee-wuh-master-character-world.png"
  "lwa-web/public/brand/lee-wuh/ui/lee-wuh-mobile-ui-reference.png"
  "lwa-web/public/brand/lee-wuh/characters/lee-wuh-transparent-with-sword-aura.png"
  "lwa-web/public/brand/lee-wuh/characters/lee-wuh-transparent-aura.png"
  "lwa-web/public/brand/lee-wuh/characters/lee-wuh-transparent-clean.png"
  "lwa-web/public/brand/lee-wuh/weapons/lee-wuh-sword-transparent-aura.png"
  "docs/brand/LEE_WUH_ASSET_MAP.md"
  "brand-source/lee-wuh/asset-manifest.json"
)

missing=0
for f in "${REQUIRED[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "MISSING: $f"
    missing=1
  fi
done

if [[ "$missing" -eq 0 ]]; then
  echo "✅ Lee-Wuh assets are installed in the repo."
else
  echo "❌ Some Lee-Wuh assets are missing."
  exit 1
fi
