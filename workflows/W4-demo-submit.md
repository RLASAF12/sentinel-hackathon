# W4 — Demo + Submit

## Trigger
Say "Run W4" after W3 is complete.

## Purpose
Record the demo video and submit to Devpost. Do not skip this.

## Prerequisite
W3 complete: full pipeline runs, Cloud Run URL exists.

## Steps

### 1. Demo Video (demo-director)
Follow docs/demo-script.md exactly. Record a terminal screen capture.

Pre-recording setup:
  export SENTINEL_DEMO=true
  export SENTINEL_SCENARIO=high-risk
  clear

Run: python -m sentinel.main --demo

The gate moment at ~1:30 is the money shot. Let it sit for 2+ seconds.

Upload to YouTube (unlisted) or Loom. Note the URL.

### 2. README Polish (content-positioning)
Update README.md:
- Add demo video link/embed
- Verify all sections present: What it does, Quick Start, Architecture, Gate, GCP, MCP, Responsible AI
- Add architecture diagram if missing

### 3. Devpost Submission (submission-compliance)
Fill docs/submission-draft.md:
- Replace all [PLACEHOLDER] values
- Add demo video URL
- Add lessons learned

Submit on Devpost:
- Project name: Sentinel
- Tagline: The agent that knows when not to ship
- Demo video: [your URL]
- GitHub: https://github.com/RLASAF12/sentinel-hackathon
- Select tracks: [from docs/devpost-unknowns-resolved.md]
- Technologies: Python, Gemini 2.0 Flash, Google ADK, MCP, GitLab, Cloud Run

### 4. Final Rubric Verification
Run through rubric-tracker in agents/submission-compliance.md.
All items must be DONE, not TODO or IN PROGRESS.

## Done When
- [ ] Demo video uploaded, URL available
- [ ] Devpost submission SUBMITTED (not just saved as draft)
- [ ] README has video link
- [ ] Rubric: all 8 criteria green

## Hand Off
Say: "W4 complete. Submitted! Ready for W5."
