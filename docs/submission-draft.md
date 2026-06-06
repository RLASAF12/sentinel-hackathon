# Devpost Submission Draft

Status: READY — fill the two human-only items (video URL, exact track names),
then submit on Devpost. Everything else is final.

---

## Project Name
Sentinel

## Tagline
The AI agent that knows when not to ship.

## Demo Video
[TODO — human: upload the recording (unlisted YouTube or Loom) and paste URL.
Recording guide: docs/demo-script.md. Captured terminal run: docs/demo-capture.txt]

## GitHub Repository
https://github.com/RLASAF12/sentinel-hackathon

## Tracks
Working selection (confirm exact spelling on the live Devpost page — see
docs/devpost-unknowns-resolved.md):
- Best Use of Google Cloud
- Best Agent Built with MCP

## Technologies
Python 3.12, Google Generative AI (Gemini 2.0 Flash), Google ADK, Model Context
Protocol (MCP), GitLab MCP Server, Google Cloud Run, Rich, Claude Code

---

## What it does

Sentinel is an AI deployment risk guardian. When a developer triggers a
deployment, Sentinel:

1. **Detects** risk signals — file churn, config/infra changes, test-coverage
   drops, breaking-change patterns, and production targets — and computes an
   aggregate 0–1 risk score.
2. **Diagnoses** the root cause with Gemini 2.0 Flash (with a deterministic
   heuristic fallback so it never hard-fails).
3. **Proposes** an action via GitLab MCP tools (rollback, alert, hold, patch).
4. **Gates** any destructive action behind explicit human approval.
5. **Executes** only with sign-off — and appends every decision to an
   auditable log.

The gate is the differentiator. Most AI agents act autonomously. Sentinel
deliberately stops and asks a human before doing anything destructive.

---

## How it was built

Built with Google ADK for multi-agent orchestration. Seven specialized
subagents (architect, builder, MCP integration, safeguard/risk, demo director,
submission compliance, content/positioning) coordinate through five workflow
commands (W1–W5). The orchestrator prompt (CLAUDE.md) drives the entire build
in Claude Code.

The pipeline is a clean linear flow — `detect → diagnose → act → GATE →
execute` — chosen for testability and demo clarity (ADR-001). The gate sits
**after** the agent proposes and **before** anything runs. Destructive tools
(GitLab `cancel_pipeline`) are the only ones routed through it. A demo mode
(`SENTINEL_DEMO=true`) swaps in a mock MCP client and heuristic diagnosis so
the whole thing runs with zero credentials — essential for a reliable demo.

Tech stack: Python 3.12, Google ADK, Gemini 2.0 Flash, GitLab MCP, Cloud Run, Rich.

---

## Challenges

- **Making the demo b/ CI deterministic.** Gemini and live GitLab can't be
  guaranteed during a recording or in tests. We made every external dependency
  lazily imported and gave each a mock/heuristic path behind one env flag, so
  the full pipeline runs identically with or without credentials.
- **Designing the gate to be safe by default.** The gate must never let a
  destructive action through by accident. We made non-interactive contexts
  (piped input, CI, EOF) fail-safe to *deny*, with an explicit opt-in
  (`SENTINEL_AUTO_APPROVE`) only for unattended recordings.
- **Avoiding an import collision.** Our internal `src/mcp` package shares a name
  with the official `mcp` SDK; we kept the SDK import lazy and inside the
  real-mode code path so the two never clash.

---

## Accomplishments

The human risk-gate. It is not technically complex, but it is the right design.
An AI agent that halts itself, explains its reasoning (what, why, risk score,
alternatives), waits for a human, and logs the decision permanently is more
trustworthy in production than one that executes autonomously. The pipeline is
fully working end-to-end with tests, an audit trail, and a Cloud Run image.

---

## What was learned

- A small, well-placed human checkpoint changes the trust profile of an agent
  far more than additional autonomy does.
- "Demo-safe by construction" (mock + heuristic fallbacks behind one flag) is
  worth designing in from day one — it doubles as the testing strategy.
- Fail-safe defaults belong at the gate boundary, not in the caller.

---

## What's next

- Slack / webhook approval transport for the gate (not just CLI) — ADR-002.
- Multi-provider CI support (GitHub Actions, CircleCI) behind the same client interface.
- A dashboard to visualize the audit log and risk trends over time.

---

## Built With
Python, Google Generative AI (Gemini 2.0 Flash), Google ADK, MCP,
GitLab MCP Server, Google Cloud Run, Rich, Claude Code
