# LWA CHUNK 8 — FULL EDITOR AND iOS REBUILD ALGORITHMS

This chunk defines the full editor and full iOS rebuild plan. These are not mixed into backend algorithm work. They require dedicated branches and feature gates.

## Full editor truth

A full editor is not a media preview. A full editor is a timeline system with versioned commands and export jobs.

## Editor objects

```text
project
timeline
track
item
caption_layer
text_layer
broll_layer
audio_layer
effect_layer
export_job
version
command_history
```

## Editor project lifecycle

```text
draft
editing
exporting
exported
failed
archived
```

## Timeline validation rules

```text
- Every item must have start < end.
- No negative start time.
- Required source asset exists.
- Export preset exists.
- Captions stay inside platform safe area.
- Audio/video assets are available.
- Timeline version increments after every command.
```

## Editor command types

```text
trim_clip
split_clip
move_item
delete_item
add_caption
edit_caption_text
change_caption_style
add_text_overlay
add_broll
change_crop
change_export_preset
save_version
export_timeline
```

## Editor command algorithm

```python
def apply_editor_command(project, timeline, command):
    if command.type == 'trim_clip':
        return trim_clip(timeline, command.payload)
    if command.type == 'split_clip':
        return split_clip(timeline, command.payload)
    if command.type == 'move_item':
        return move_item(timeline, command.payload)
    if command.type == 'delete_item':
        return delete_item(timeline, command.payload)
    if command.type == 'add_caption':
        return add_caption(timeline, command.payload)
    if command.type == 'edit_caption_text':
        return edit_caption_text(timeline, command.payload)
    if command.type == 'change_caption_style':
        return change_caption_style(timeline, command.payload)
    if command.type == 'add_broll':
        return add_broll(timeline, command.payload)
    raise ValueError('unsupported_editor_command')
```

## Export pipeline

```text
Load project
→ load current timeline
→ validate timeline
→ build media filtergraph/render plan
→ create export job
→ render preview/export
→ persist clip asset
→ attach asset to editor project
→ update export status
```

## Editor feature flag rules

```text
- If full_editor is planned, hide editor routes from normal users.
- If full_editor is beta, show only to beta/admin.
- If full_editor is live, show only after export tests pass.
```

## Editor Codex prompt

```text
Implement editor scaffold only.

Rules:
- Do not touch current generation route.
- Do not claim full editor is live.
- Add timeline schemas and pure command functions first.
- Keep routes behind feature flag.
- Do not touch iOS in this backend prompt.
```

---

# Full iOS rebuild plan

## iOS truth

The iOS app should not be changed accidentally during backend or web tasks. The full rebuild requires a dedicated branch.

## iOS modules

```text
AuthModule
SourceInputModule
UploadModule
GenerationModule
ClipReviewModule
EditorLiteModule
CampaignModule
SocialPostingModule
MarketplaceModule
RealmsModule
ProofModule
SettingsModule
OfflineHistoryModule
ShareSheetModule
```

## iOS data model goals

The iOS app must understand:

```text
- Director Brain fields
- render_status
- strategy_only
- reason_not_rendered
- quality_gate_status
- campaign_role
- funnel_stage
- asset URLs
- upload status
- social posting status later
- marketplace product summaries later
- Realms profile later
```

## Swift clip model sketch

```swift
struct LWAClipResult: Identifiable, Codable {
    let id: String
    let rank: Int
    let postRank: Int
    let title: String
    let hook: String
    let caption: String?
    let score: Int
    let confidenceScore: Int
    let recommendedPlatform: String?
    let renderStatus: String
    let strategyOnly: Bool
    let reasonNotRendered: String?
    let previewURL: URL?
    let downloadURL: URL?
    let campaignRole: String?
    let funnelStage: String?
}
```

## iOS rebuild phases

```text
Phase 1: preserve current preview/share/history flow.
Phase 2: add Director Brain response field support.
Phase 3: add upload from camera roll and Files.
Phase 4: add clip review queue.
Phase 5: add lightweight editor.
Phase 6: add campaign manager views.
Phase 7: add social account connections.
Phase 8: add Realms profile.
Phase 9: add marketplace browsing.
Phase 10: add optional proof/cosmetic identity.
```

## iOS safety rule

```text
Never mix iOS rebuild with backend algorithm work.
Never mix iOS rebuild with frontend web work.
Use a dedicated iOS branch and dedicated verification.
```

## iOS Codex prompt

```text
Dedicated iOS branch only.

Task:
Add Director Brain response field support to iOS models and views without changing backend or web.

Rules:
- Preserve existing preview/share/history flow.
- Do not build full editor in this prompt.
- Do not build marketplace in this prompt.
- Do not build direct social posting in this prompt.
- Do not touch backend.
- Do not touch lwa-web.

Verification:
- build Debug
- build Release if available
- confirm existing generation preview still works
```
