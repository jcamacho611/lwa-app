# Install Lee-Wuh World + Sword Assets

Run from the repo root:

```bash
cd /Users/bdm/LWA/lwa-app
unzip -o ~/Downloads/lwa-lee-wuh-world-and-sword-repo-patch.zip -d .
bash scripts/verify-lee-wuh-world-and-sword-assets.sh
git status --short
```

Then commit:

```bash
git add \
  brand-source/lee-wuh/separated-assets/lee-wuh-world-background.glb \
  brand-source/lee-wuh/separated-assets/README-lee-wuh-world-background.txt \
  brand-source/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb \
  brand-source/lee-wuh/models/weapons/README-lwa-fantasy-sword-no-aura.txt \
  lwa-web/public/brand/lee-wuh/backgrounds/lee-wuh-world-background.glb \
  lwa-web/public/brand/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb \
  scripts/blender/create_lwa_lee_wuh_world_background_blend.py \
  scripts/blender/create_lwa_fantasy_sword_no_aura_blend.py \
  scripts/verify-lee-wuh-world-and-sword-assets.sh \
  docs/brand/LWA_LEE_WUH_WORLD_BACKGROUND_ASSET.md \
  docs/brand/LWA_FANTASY_SWORD_NO_AURA_ASSET.md \
  docs/brand/LWA_LEE_WUH_3D_ASSET_INDEX.md \
  README-INSTALL-LEE-WUH-WORLD-AND-SWORD-ASSETS.md

git commit -m "assets(lee-wuh): add separated world and sword assets"
git push origin main
```
