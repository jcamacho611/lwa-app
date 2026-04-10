#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

source .venv/bin/activate
kill -9 $(lsof -ti:8000) 2>/dev/null || true

exec python -m uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --reload \
  --reload-dir app \
  --reload-dir scripts \
  --reload-exclude '.venv/*' \
  --reload-exclude 'generated/*' \
  --reload-exclude 'downloads/*'
