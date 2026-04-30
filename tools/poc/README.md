# Source POC Matrix

`source_matrix_runner.py` proves which any-source inputs work against a running LWA backend.

It checks:

- upload acceptance for video, audio, and image fixtures
- `/v1/generate` acceptance
- returned `source_type`
- rendered/playable media URLs when rendering is expected
- prompt, music, and campaign strategy-only package paths
- optional public URL fallback behavior without leaking raw extractor errors

Run it from the repo root:

```bash
python3 tools/poc/source_matrix_runner.py --base-url http://127.0.0.1:8000
```

Optional public-source fallback checks:

```bash
python3 tools/poc/source_matrix_runner.py \
  --base-url http://127.0.0.1:8000 \
  --youtube-url "https://www.youtube.com/watch?v=..." \
  --twitch-url "https://www.twitch.tv/videos/..." \
  --unsupported-url "https://example.com/not-a-supported-source"
```

The runner creates generated fixtures and reports under `poc/`. Those outputs are ignored by git.
