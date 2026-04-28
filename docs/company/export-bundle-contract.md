# Export Bundle Contract

## Purpose
Define the backend deliverable contract for clip packages and manifests.

## Implemented
- JSON manifest generation for clip packs
- ZIP bundle generation for export route
- per-clip package metadata including:
  - title
  - hook
  - caption
  - thumbnail text
  - CTA
  - post rank
  - platform fit
  - rendered status
  - score
  - why this matters
- URL-only asset references in manifests

## Important Safety Rules
- manifests must not include local filesystem paths
- package text must remain creator-facing, not internal-path-facing
- export metadata must succeed nonfatally where possible

## Current Truth
- export bundles are a real backend artifact
- they are not a full creative asset management system
- they do not imply direct publishing

## Related Fields
- `export_bundle_available`
- `export_bundle_format`
- `export_bundle_manifest_url`
- `export_bundle_notes`
- `package_text`
- `asset_manifest`
- `export_ready`

## Future Work
- richer bundle variants per platform
- optional Cloudinary or R2 offload
- batch-level export dashboards
