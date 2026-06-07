---
name: record-demo-video
description: Record / create / regenerate a demo video (screencast) of Sentinel — the live web-UI risk-gate flow (Deny = HOLD, Approve = real GitLab pipeline cancel) driven by Playwright and encoded to MP4 with ffmpeg. Use when asked to make a demo video, record the demo, screencast the app, or produce demo footage for Sentinel.
---

# Record a Sentinel demo video

Produces `docs/demo/sentinel-demo.mp4` — a ~50s captioned screencast of the
**live** stack: the web UI lands on the hero, Gemini 3 (Vertex AI) diagnoses a
real GitLab pipeline, the risk gate appears, **Deny** holds the pipeline, then
**Approve** cancels a (different) pipeline *for real*. Everything on screen is
real output — no mocks.

How it's driven: a headless Chromium (Playwright) drives the local web UI and
**records video**, with captions injected onto the page at each beat; then
`ffmpeg` transcodes the `.webm` to MP4. The whole thing is one script.

Paths below are relative to the repo root.

## Prerequisites

Secrets in `.env` (real stack — the video proves real effects):
- `GITLAB_TOKEN` (PAT, `api` scope), `GITLAB_PROJECT_ID` (a project whose
  default branch has a long-running `.gitlab-ci.yml` job, so a pipeline stays
  "running" long enough to cancel), `GITLAB_URL` (default `https://gitlab.com`).
- Vertex AI / Gemini 3: `GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_CLOUD_PROJECT`,
  `GOOGLE_CLOUD_LOCATION=global`, `GOOGLE_APPLICATION_CREDENTIALS=<sa-key.json>`,
  `SENTINEL_MODEL=gemini-3.1-pro-preview`.

Tools (the web-video path needs only these — it talks to GitLab over REST, so no
Node/MCP server is required; that's only for the CLI agent path):

```bash
apt-get install -y ffmpeg          # bundled Playwright ffmpeg CANNOT mux mp4
. .venv/bin/activate && pip install -q playwright
# Chromium: this container ships one at /opt/pw-browsers; otherwise:
# python -m playwright install chromium
```

## Run (agent path) — one command

```bash
fuser -k 8080/tcp 2>/dev/null; sleep 1            # free the port if something's on it
./.claude/skills/record-demo-video/driver.sh docs/demo/sentinel-demo.mp4
```

`driver.sh` (committed next to this file) does it all: starts the live web UI on
`:8080` (reuses it if already up), triggers **two** real pipelines, runs the
Playwright recorder, and encodes the MP4. On success it prints:

```
WROTE docs/demo/sentinel-demo.mp4  (52.2s, 1.3M)
```

Verify the real effect and eyeball a frame:

```bash
set -a; . ./.env; set +a
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/$GITLAB_PROJECT_ID/pipelines?per_page=3" \
  | python3 -c "import sys,json;[print(p['id'],p['status']) for p in json.load(sys.stdin)]"
# expect one 'canceled' (the Approve) and one 'running' (the Deny held it)
ffmpeg -y -ss 40 -i docs/demo/sentinel-demo.mp4 -frames:v 1 /tmp/frame.png
```

## Customize the footage

- **Captions / pacing / beats:** edit `scripts/record_demo.py` (the recorder).
  Captions are injected via `cap(page, "...")`; `wait_for_gate(...)` cycles
  "thinking" lines while Gemini 3 runs so the latency reads as intentional.
- **Output size:** `record_video_size` / `viewport` in `scripts/record_demo.py`
  (currently 1280x800).
- **Output path / target:** `SENTINEL_DEMO_OUT`, `SENTINEL_URL` env, or the
  first arg to `driver.sh`.

## Gotchas (learned the hard way)

- **Never `pkill -f "src.sentinel.web"`** — the pattern matches the killing
  shell's own command line and kills it (exit 144). Stop the server by port:
  `fuser -k 8080/tcp`.
- **The bundled Playwright ffmpeg can't write MP4** (webm-only, and it rejects
  `-movflags`). You need a real ffmpeg: `apt-get install -y ffmpeg`.
- **Live Gemini 3 adds ~10s of latency per scan.** Without filler that's dead
  air; the recorder rotates progress captions during the wait. Keep that.
- **The container can't reach the public Cloud Run URL** (network allowlist) but
  it *can* run the same web UI on `localhost` and hit gitlab.com's API — so
  always record `http://localhost:8080`, never the hosted URL.
- **The video is silent with baked-in captions.** Upload as-is, or record a
  voiceover over it. To make a voiceover-friendly cut, remove the `cap(...)`
  calls in `scripts/record_demo.py`.
- **GitLab needs identity verification** for pipelines to actually run; if the
  triggered pipelines go straight to `failed` with 0 jobs, that account isn't
  verified and there's nothing to cancel.

## Troubleshooting

- `web UI failed to start` → check `/tmp/sentinel-web.log`; usually a missing
  Vertex/GitLab env var (web live mode imports `src/sentinel/live.py`).
- Recorder times out waiting for `#gate` → no pipeline was running. Confirm a
  pipeline is `running` (see verify command) before recording; the demo project
  needs a long job (e.g. `sleep 600`) in `.gitlab-ci.yml`.
- Blank/loading-only frames → that's the Gemini wait; check a frame at ~40s, not
  ~15s.
