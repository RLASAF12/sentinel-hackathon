# Sentinel — 3-Minute Demo Script

Total time: 3:00 max
Format: Terminal screen recording
Key moment: The gate at 1:30 — let it breathe (2+ seconds)

---

## Pre-Recording Setup

Font: Menlo or JetBrains Mono, 18pt
Theme: Dark (Dracula or One Dark)
Window: Large but not full screen

Commands to run before recording:
  export SENTINEL_DEMO=true
  export SENTINEL_SCENARIO=high-risk
  clear

---

## Recording Timeline

### [0:00] Start
Type and press Enter:
  python -m src.sentinel.main --demo

### [0:05] Header
  SENTINEL - Risk Guardian for CI/CD
  Google Cloud Rapid Agent Hackathon

### [0:15] DETECT phase (show scanner running)
  [DETECT] Scanning merge request #1847... target: production
  Signal: FILES_CHANGED = 47 files           [HIGH]
  Signal: CONFIG_MODIFIED: k8s/prod.yaml     [HIGH]
  Signal: COVERAGE_DELTA: -12.3%             [MEDIUM]
  Risk score: 0.87    STATUS: HIGH RISK

### [0:45] DIAGNOSE phase (stream from Gemini or mock)
  [DIAGNOSE] Sending to Gemini 2.0 Flash...
  Root cause: Large deployment scope with infrastructure changes
  Severity: HIGH
  Recommended: Delay, restore coverage first

### [1:15] ACT phase
  [ACT] Proposed: ROLLBACK pipeline #12345
  Type: DESTRUCTIVE ACTION

### [1:30] THE GATE — MONEY SHOT
  PAUSE 2+ SECONDS. Let audience read this.

  +--------------------------------------------------+
  |         SENTINEL RISK GATE                       |
  +--------------------------------------------------+
  |  Action:      ROLLBACK pipeline #12345           |
  |  Risk Score:  87% (HIGH)                         |
  |  Evidence:    47 files, config change,           |
  |               coverage -12.3%                    |
  |  Alternative: Delay 2h + notify team             |
  +--------------------------------------------------+
  Human approval required. AI cannot proceed alone.

  Approve? (y)es / (n)o / (d)etails:

  [Speak or caption]: "No AI agent in this competition stops here and asks you. Sentinel does."

### [2:00] Approval
Type: y

  Approved by: human-operator
  Executing ROLLBACK via GitLab MCP...
  Pipeline #12345 cancelled.
  Audit entry written to sentinel-audit.log
  Deployment held. Team notified. Production protected.

### [2:20] Architecture flash (3 seconds)
  Detect -> Diagnose (Gemini) -> Act (GitLab MCP) -> GATE -> Execute
                                                      ^
                                                 Human required

### [2:45] Close
  Sentinel — the agent that knows when not to ship.
  Google ADK | Gemini 2.0 Flash | GitLab MCP | Cloud Run

### [3:00] End

---

## After Recording
- Upload to YouTube (unlisted) or Loom
- Note URL for Devpost
- Thumbnail: screenshot of the gate panel
