# LWA Recovery Engine

The recovery engine turns failures, strategy-only results, missing previews, provider issues, and export problems into useful next actions.

This is important because LWA should not convert every failure into a dead end. If rendering fails, the strategy pack can still be useful. If a provider is unavailable, the user should be guided to a fallback path. If a preview asset is missing, the run should still explain what to do next.

## Recovery Issue Types

- `render_failed`
- `strategy_only`
- `missing_preview`
- `provider_unavailable`
- `export_failed`
- `asset_missing`
- `invalid_source`
- `unknown_error`

## Recovery Actions

- `retry_render`
- `export_strategy`
- `use_fallback_provider`
- `save_as_proof_idea`
- `open_support_context`
- `downgrade_quality`
- `copy_package_only`
- `reset_run`

## Frontend Role

- classify the current issue
- show the Lee-Wuh recovery line
- present primary and secondary actions
- keep strategy-only output useful
- avoid pretending that a failure is terminal when a fallback exists

## Backend Role Later

- return structured recovery codes
- suggest rerender or downgrade paths
- expose queue and provider retry states
- preserve recovery events for proof and history

