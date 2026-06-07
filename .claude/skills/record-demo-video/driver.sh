#!/usr/bin/env bash
# Record a Sentinel demo video end-to-end, against the LIVE stack.
#
# Pipeline: start the live web UI -> trigger two real GitLab pipelines ->
# Playwright records the gate flow (Deny=HOLD, Approve=real cancel) with baked-in
# captions -> ffmpeg encodes an MP4. Output: docs/demo/sentinel-demo.mp4.
#
# Usage (from repo root, with .env containing GITLAB_TOKEN + Vertex creds):
#   ./.claude/skills/record-demo-video/driver.sh [output.mp4]
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
OUT="${1:-docs/demo/sentinel-demo.mp4}"

# --- deps / env ---------------------------------------------------------------
[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -c "import playwright" 2>/dev/null || pip install -q playwright
if ! command -v ffmpeg >/dev/null; then
  SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
  $SUDO apt-get update -qq && $SUDO apt-get install -y ffmpeg
fi
[ -n "$(ls /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null)" ] \
  || python -m playwright install chromium

[ -f .env ] || { echo "ERROR: .env missing (need GITLAB_TOKEN, Vertex creds)"; exit 1; }
set -a; # shellcheck disable=SC1091
source .env; set +a
export SENTINEL_DEMO=false SENTINEL_GITLAB_MCP="${SENTINEL_GITLAB_MCP:-stdio}" USE_PIPELINE=true
: "${GITLAB_TOKEN:?set GITLAB_TOKEN in .env}"
: "${GITLAB_PROJECT_ID:?set GITLAB_PROJECT_ID in .env}"
GITLAB_URL="${GITLAB_URL:-https://gitlab.com}"

# --- live web UI (reuse if already up) ---------------------------------------
if ! curl -sf localhost:8080/health >/dev/null 2>&1; then
  nohup python -m src.sentinel.web > /tmp/sentinel-web.log 2>&1 &
  for _ in $(seq 1 15); do curl -sf localhost:8080/health >/dev/null 2>&1 && break; sleep 1; done
fi
curl -sf localhost:8080/health >/dev/null || { echo "web UI failed to start"; cat /tmp/sentinel-web.log; exit 1; }

# --- two real running pipelines (one to deny, one to approve) -----------------
for _ in 1 2; do
  curl -s -X POST -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/api/v4/projects/$GITLAB_PROJECT_ID/pipeline?ref=main" >/dev/null
done
echo "Triggered 2 pipelines; waiting for 'running'..."; sleep 10

# --- record + encode ----------------------------------------------------------
rm -rf docs/demo/raw; mkdir -p docs/demo "$(dirname "$OUT")"
python scripts/record_demo.py
WEBM="$(ls -t docs/demo/raw/*.webm | head -1)"
ffmpeg -y -i "$WEBM" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -movflags +faststart -r 30 "$OUT" >/dev/null 2>&1

DUR="$(ffprobe -v error -show_entries format=duration -of default=nokey=1:noprint_wrappers=1 "$OUT")"
echo "WROTE $OUT  (${DUR}s, $(du -h "$OUT" | cut -f1))"
