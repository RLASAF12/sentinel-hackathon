# Sentinel
### The AI agent that knows when not to ship.

> Google Cloud Rapid Agent Hackathon submission

---

## What It Does

Sentinel is a deployment risk guardian. When a developer opens a PR or triggers a deployment, Sentinel:

1. **Detects** risk signals: file churn, config changes, test regressions, production targets
2. **Diagnoses** root cause with Gemini 2.0 Flash
3. **Proposes** actions via GitLab MCP tools (rollback, alert, hold)
4. **Gates** any destructive action behind human approval
5. **Executes** only with explicit sign-off — every decision logged

**The gate is the differentiator.** AI suggests. You decide. Sentinel remembers.

---

## Quick Start

```bash
git clone https://github.com/RLASAF12/sentinel-hackathon
cd sentinel-hackathon
pip install -r requirements.txt

# Demo mode (no API keys required)
python -m sentinel.main --demo

# With real APIs
export GEMINI_API_KEY=your_key
export GITLAB_TOKEN=your_token
python -m sentinel.main
```

---

## Architecture

```
[PR / Deploy Event]
        |
   [DETECT]    Risk signal scanner
        |
   [DIAGNOSE]  Gemini 2.0 Flash root cause analysis
        |
   [ACT]       GitLab MCP tool selection
        |
   [GATE]  <-- HUMAN APPROVAL REQUIRED (if destructive)
        |
[SHIP / HOLD]  Logged, auditable
```

Multi-agent system (Google ADK): Orchestrator + 7 specialized subagents + 5 workflow commands.

---

## The Risk Gate

```
+--------------------------------------------------+
|         SENTINEL RISK GATE                       |
+--------------------------------------------------+
|  Action:      ROLLBACK pipeline #12345           |
|  Risk Score:  87% (HIGH)                         |
|  Evidence:    47 files changed, config modified  |
|  Alternative: Delay 2h + notify team             |
+--------------------------------------------------+
  Approve? (y)es / (n)o / (d)etails:
```

Before any destructive action runs, Sentinel shows you what, why, risk score, and alternatives. You decide. No autonomous destructive actions — ever.

---

## Google Cloud

| Component | Role |
|-----------|------|
| Gemini 2.0 Flash | Risk diagnosis, root cause analysis |
| Google ADK | Multi-agent orchestration |
| Cloud Run | Deployment target |

---

## MCP Integration

Uses the official **GitLab MCP server**. Wrapped tools:
- `get_merge_request_diff` — fetch diff for analysis
- `create_merge_request_note` — post risk assessment comment
- `cancel_pipeline` — rollback (always gated before execution)

---

## Responsible AI

The gate is a design principle, not a UI checkbox:
- AI cannot execute destructive actions without human approval
- Every decision is logged: timestamp, approver, risk score, context
- Audit log is append-only
- Demo and production mode both enforce the gate

---

## Using This Repo with Claude Code

Clone this repo, open in Claude Code, then:
```
Run W1.
```

W1 locks scope. W2 builds the core. W3 wires integrations. W4 records demo and submits. W5 polishes.

---

## Repo Structure

```
sentinel-hackathon/
+-- CLAUDE.md          Orchestrator master prompt (start here for Claude Code)
+-- PLAN.md            5-day sprint plan + rubric map
+-- agents/            7 subagent definitions
+-- workflows/         W1-W5 Claude Code workflow commands
+-- src/sentinel/      Core source code
+-- docs/              Demo script, submission draft
+-- tests/             Test suite
```

---

## Demo

[Video link added after recording]

---

*Google Cloud Rapid Agent Hackathon | 2026*
