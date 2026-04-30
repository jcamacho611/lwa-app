# LWA Engine CLI Prototype

This is a small standalone prototype for source metadata extraction and short-form content ideation.

It intentionally lives outside the production runtime:

- not imported by `lwa-backend`
- not imported by `lwa-web`
- not used by `lwa-ios`
- safe to delete or replace later

## What it does

1. Accepts a public video URL from the terminal.
2. Uses `yt-dlp --dump-json` to read metadata.
3. Sends metadata to Claude.
4. Returns:
   - 5 hooks
   - 5 short-form clip ideas
   - TikTok / Reels / Shorts captions
   - 5 titles
   - short posting strategy

If transcript data is not present, the model is instructed to infer from metadata and say that clearly.

## Setup

```bash
cd tools/lwa-engine
python3 -m venv venv
source venv/bin/activate
pip install anthropic yt-dlp
export ANTHROPIC_API_KEY=your_key_here
```

Optional model override:

```bash
export ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

## Run

```bash
python3 engine.py
```

Then paste a public video URL.

## Safety notes

- Do not paste secrets into the source URL input.
- Do not claim generated ideas guarantee views, revenue, or virality.
- This prototype does not download or render clips.
- This prototype does not bypass private, gated, or login-restricted sources.
- Production implementation belongs in `lwa-backend`, not here.
