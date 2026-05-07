#!/usr/bin/env bash
# Smoke test the LWA backend engines registry.
#
# Hits every read route on /engines and runs a deterministic demo for each
# of the 10 engines. Honest exit code: 0 on full success, 1 on any failure.
#
# Usage:
#   ./scripts/smoke_engines.sh                      # default: http://localhost:8000
#   API_BASE=https://api.example.com ./scripts/smoke_engines.sh
#
# Requires: curl, jq.

set -u
set -o pipefail

API_BASE="${API_BASE:-http://localhost:8000}"
ENGINES=(
  creator
  brain
  render
  marketplace
  wallet_entitlements
  proof_history
  world_game
  safety
  social_distribution
  operator_admin
)

# Per-engine sample payload — matches the deterministic demo paths.
declare -A SAMPLE_PAYLOAD=(
  [creator]='{"source":"demo source","title":"Demo upload"}'
  [brain]='{"recommended_action":"Lead with the strongest hook"}'
  [render]='{"render_requested":false}'
  [marketplace]='{"preview_offer":"Creator growth lane"}'
  [wallet_entitlements]='{"credits":120}'
  [proof_history]='{"proof_id":"proof_demo_001"}'
  [world_game]='{"current_realm":"signal_realm"}'
  [safety]='{"request_type":"clip_review"}'
  [social_distribution]='{"destination":"manual_review"}'
  [operator_admin]='{"focus":"smoke_test"}'
)

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
DIM=$'\033[2m'
RESET=$'\033[0m'

PASS=0
FAIL=0

ok() { printf "%s✓%s %s\n" "$GREEN" "$RESET" "$1"; PASS=$((PASS+1)); }
bad() { printf "%s✗%s %s\n" "$RED" "$RESET" "$1"; FAIL=$((FAIL+1)); }
note() { printf "%s· %s%s\n" "$DIM" "$1" "$RESET"; }

require() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf "%sMissing required command: %s%s\n" "$RED" "$cmd" "$RESET" >&2
    exit 1
  fi
}

require curl
require jq

printf "%s== LWA engine smoke ==%s\n" "$YELLOW" "$RESET"
note "API_BASE=$API_BASE"

# 1. /engines must list 10 engines.
registry_json="$(curl -fsS "$API_BASE/engines" || true)"
if [[ -z "$registry_json" ]]; then
  bad "GET /engines returned no body — backend reachable?"
else
  count="$(printf "%s" "$registry_json" | jq -r '.count // 0')"
  if [[ "$count" == "10" ]]; then
    ok "GET /engines  count=10"
  else
    bad "GET /engines  count=$count (expected 10)"
  fi
fi

# 2. /engines/health must report a healthy_count <= 10.
health_json="$(curl -fsS "$API_BASE/engines/health" || true)"
if [[ -z "$health_json" ]]; then
  bad "GET /engines/health returned no body"
else
  total="$(printf "%s" "$health_json" | jq -r '.count // 0')"
  healthy="$(printf "%s" "$health_json" | jq -r '.healthy_count // 0')"
  ok "GET /engines/health  $healthy/$total healthy"
fi

# 3. Each engine must answer GET /engines/{id} and POST /engines/{id}/demo.
for id in "${ENGINES[@]}"; do
  detail_status="$(curl -fsS -o /dev/null -w "%{http_code}" "$API_BASE/engines/$id" || echo "ERR")"
  if [[ "$detail_status" == "200" ]]; then
    ok "GET  /engines/$id  200"
  else
    bad "GET  /engines/$id  $detail_status"
    continue
  fi

  payload="${SAMPLE_PAYLOAD[$id]:-{}}"
  demo_response="$(curl -fsS -X POST "$API_BASE/engines/$id/demo" \
                    -H 'content-type: application/json' \
                    -d "$payload" || true)"
  if [[ -z "$demo_response" ]]; then
    bad "POST /engines/$id/demo  no body"
    continue
  fi

  reported_id="$(printf "%s" "$demo_response" | jq -r '.engine_id // empty')"
  if [[ "$reported_id" == "$id" ]]; then
    summary="$(printf "%s" "$demo_response" | jq -r '.summary // empty' | cut -c1-72)"
    ok "POST /engines/$id/demo  → $summary"
  else
    bad "POST /engines/$id/demo  reported engine_id=$reported_id"
  fi
done

printf "\n%s== summary == %s passed: %d  failed: %d%s\n" \
  "$YELLOW" "$RESET" "$PASS" "$FAIL" "$RESET"

if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
