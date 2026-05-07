# Codex Prompt: Install and Use Lee-Wuh Assets Safely

Repo: `/Users/bdm/LWA/lwa-app`

You are working on the LWA repo. Preserve existing backend, iOS, API contracts, and current clipping-engine behavior. Do not delete or rewrite unrelated systems.

The Lee-Wuh visual assets have been inserted at:

- `lwa-web/public/brand/lee-wuh/backgrounds/lee-wuh-empty-world-background.png`
- `lwa-web/public/brand/lee-wuh/characters/lee-wuh-transparent-with-sword-aura.png`
- `lwa-web/public/brand/lee-wuh/characters/lee-wuh-transparent-aura.png`
- `lwa-web/public/brand/lee-wuh/characters/lee-wuh-transparent-clean.png`
- `lwa-web/public/brand/lee-wuh/weapons/lee-wuh-sword-transparent-aura.png`
- `lwa-web/public/brand/lee-wuh/ui/lee-wuh-mobile-ui-reference.png`
- `lwa-web/public/brand/lee-wuh/references/lee-wuh-master-character-world.png`

Read first:

- `docs/brand/LEE_WUH_ASSET_MAP.md`

Build a safe frontend slice that uses the assets correctly:

1. Create or update a Lee-Wuh world hero component.
2. Use the background image as the full scene/world layer.
3. Use transparent Lee-Wuh PNG as a separate overlay so the character can float and animate.
4. Use the sword PNG as a separate optional effect layer only when appropriate.
5. Use the UI composition image as a reference only; do not use it as a final baked UI background.
6. Keep the existing generate/clipping flow intact.
7. Do not touch backend, iOS, env files, or deployment config unless absolutely required.
8. Add responsive CSS and keep mobile-first layout.
9. Add a basic reduced-motion fallback.
10. Run the build/typecheck/lint commands that already exist in the repo and report exact results.

Acceptance criteria:

- Assets resolve from the Next.js `public` URLs.
- The page shows a layered Lee-Wuh world, not a flat screenshot.
- Existing clip-generation UI remains reachable.
- No secrets, build folders, or heavy generated files are added beyond the provided image assets.
