# LWA Source, Output, and Event Protocols

## Purpose
This document defines the typed protocol layer for the God App spine:

> sources in -> protocol layer -> AI/video engine -> output package protocol -> monetization, guild, reward, and connector systems

Every new feature must map here before it gets built.

## 1. Source Protocol

### Allowed source types

```text
video
audio
music
prompt
twitch
stream
campaign
upload
url
unknown
```

### Source protocol goals

- identify source type early
- preserve source limitations
- route to the correct AI and processing path
- avoid fake video assumptions
- remain backward-compatible

### Example source record

```json
{
  "source_type": "audio",
  "source_url": null,
  "uploaded_file_ref": "upl_123",
  "creator_objective": "Turn this podcast segment into short-form hooks",
  "target_platform": "TikTok",
  "source_metadata": {
    "duration_seconds": 1820,
    "has_transcript": false
  }
}
```

## 2. Output Package Protocol

### Expected output directions

```text
clips
hooks
captions
thumbnail_text
scores
post_order
visuals
rendered_assets
strategy_only_packages
campaign_notes
source_metadata
```

### Rules

- rendered assets must be truthful
- strategy-only packages must remain useful
- output fields must stay typed and optional-field-safe
- local filesystem paths must never leak into creator-facing output

## 3. Event Protocol

### Core events

```text
generation_started
source_ingested
clip_ranked
render_ready
package_copied
cta_clicked
guild_task_completed
reward_earned
```

### Event protocol goals

- power analytics without product drift
- support future guild and reward systems
- keep event naming stable
- stay testable and versionable

## 4. Capability Protocol

Every capability must map to:

- source expectations
- output expectations
- event emissions
- connector dependencies
- claim-safe labels

Example:

`Twitch` is not just “add Twitch.”

It means:

- source type
- metadata path
- event source
- fallback behavior
- output package rules

## 5. Current Repo Alignment

Current repo alignment is partial:

- output package fields exist in backend/frontend foundations
- score transparency fields exist
- campaign notes and packaging concepts exist
- rendered vs strategy-only distinction exists

Not fully aligned yet:

- canonical any-source request schema
- canonical event schema across all layers
- explicit versioned protocol docs in code

## 6. Safety Rules

- no hidden compute
- no hidden mining
- no hidden training
- no undisclosed resource use
- no guaranteed viral or money claims
- no fake rendered assets

## 7. Testing Expectations

Every protocol addition should verify:

- typed source handling
- typed output handling
- event naming consistency
- backward compatibility
- safe fallback output

