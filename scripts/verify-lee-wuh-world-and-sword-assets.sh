#!/usr/bin/env bash
set -euo pipefail

required_files=(
  "brand-source/lee-wuh/separated-assets/lee-wuh-world-background.glb"
  "brand-source/lee-wuh/separated-assets/README-lee-wuh-world-background.txt"
  "brand-source/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb"
  "brand-source/lee-wuh/models/weapons/README-lwa-fantasy-sword-no-aura.txt"
  "lwa-web/public/brand/lee-wuh/backgrounds/lee-wuh-world-background.glb"
  "lwa-web/public/brand/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb"
  "scripts/blender/create_lwa_lee_wuh_world_background_blend.py"
  "scripts/blender/create_lwa_fantasy_sword_no_aura_blend.py"
  "docs/brand/LWA_LEE_WUH_WORLD_BACKGROUND_ASSET.md"
  "docs/brand/LWA_FANTASY_SWORD_NO_AURA_ASSET.md"
  "docs/brand/LWA_LEE_WUH_3D_ASSET_INDEX.md"
)

missing=0
for f in "${required_files[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "Missing: $f"
    missing=1
  else
    echo "Found:   $f"
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "Lee-Wuh world/sword asset verification failed."
  exit 1
fi

if [[ ! -s "brand-source/lee-wuh/separated-assets/lee-wuh-world-background.glb" ]]; then
  echo "World background GLB is empty."
  exit 1
fi

if [[ ! -s "brand-source/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb" ]]; then
  echo "Sword GLB is empty."
  exit 1
fi

echo "Lee-Wuh world/sword asset verification passed."
