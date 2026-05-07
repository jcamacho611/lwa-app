#!/usr/bin/env bash
# Launch LWA backend + web in one terminal.
#
# This is a thin developer convenience script. It does not install
# packages, mutate data, or touch production config. It simply starts
# the existing local backend and frontend dev servers with sensible
# default ports and tears them down together on exit.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/lwa-backend"
WEB_DIR="$ROOT_DIR/lwa-web"
BACKEND_PORT="${BACKEND_PORT:-8000}"
WEB_PORT="${WEB_PORT:-3000}"

backend_pid=""
web_pid=""

cleanup() {
  local code=$?
  if [[ -n "${web_pid}" ]] && kill -0 "${web_pid}" >/dev/null 2>&1; then
    kill "${web_pid}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${backend_pid}" ]] && kill -0 "${backend_pid}" >/dev/null 2>&1; then
    kill "${backend_pid}" >/dev/null 2>&1 || true
  fi
  wait >/dev/null 2>&1 || true
  exit "$code"
}

trap cleanup EXIT INT TERM

if [[ ! -d "$BACKEND_DIR" ]]; then
  echo "Missing backend directory: $BACKEND_DIR" >&2
  exit 1
fi
if [[ ! -d "$WEB_DIR" ]]; then
  echo "Missing web directory: $WEB_DIR" >&2
  exit 1
fi

echo "Starting LWA backend on :${BACKEND_PORT}"
(cd "$BACKEND_DIR" && PORT="$BACKEND_PORT" uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT") &
backend_pid=$!

echo "Starting LWA web on :${WEB_PORT}"
(cd "$WEB_DIR" && PORT="$WEB_PORT" npm run dev) &
web_pid=$!

echo "Backend PID: ${backend_pid}"
echo "Web PID: ${web_pid}"
echo "Press Ctrl+C to stop both servers."

wait -n "$backend_pid" "$web_pid"
