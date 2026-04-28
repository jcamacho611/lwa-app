# Backend Caption And Export Foundation

## Current truth

The backend now returns truthful caption and export contract fields for each clip:

- `caption_txt_url`
- `caption_srt_url`
- `caption_vtt_url`
- `subtitle_url`
- `captions_burned_in`
- `rendered_status`
- `render_quality`
- `render_notes`
- `export_profile`
- `export_ready`
- `thumbnail_preview_url`

## Important truth boundary

`captions_burned_in` stays `false` unless real burned-in captions exist.

Current rendered exports may include overlay support, but they should not be marketed as full phrase-by-phrase OpusClip-style caption burn-in yet.

## Current profiles

- `tiktok_reels_9_16`
- `shorts_9_16`
- `podcast_clean_9_16`
- `strategy_only_package`

These are contract and packaging profiles, not a promise that multiple rendered files are created for every profile yet.

## Caption styles surfaced

The backend exposes caption style foundations from the intelligence tables, including presets such as:

- `karaoke_bold`
- `block_punch`
- `clean_editorial`
- `beauty_minimal`
- `data_emphasis`
- `tabloid_punch`
- `clinical_safe`

## Safe claims

Say:

- LWA can return subtitle sidecars and caption-style metadata.
- LWA distinguishes rendered clips from strategy-only clips truthfully.

Do not say:

- all rendered clips include full burned-in captions
- every export profile creates a separate render today

## Future work

- selectable caption style rendering
- true burned-in phrase timing
- richer multi-profile exports
