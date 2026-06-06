# Devpost Submission Draft

Status: DRAFT - replace all [PLACEHOLDER] values before submitting

---

## Project Name
Sentinel

## Tagline
The AI agent that knows when not to ship.

## Demo Video
[PLACEHOLDER: Upload recording and paste URL here]

## GitHub Repository
https://github.com/RLASAF12/sentinel-hackathon

## Tracks
[PLACEHOLDER: Check Devpost for exact track names]
Expected: "Best Use of Google Cloud" and/or "Best Agent Built with MCP"

---

## What it does

Sentinel is an AI deployment risk guardian. When a developer triggers a deployment:

1. Detects risk signals: file churn, config changes, test coverage drops, production targets
2. Diagnoses root cause using Gemini 2.0 Flash
3. Proposes an action via GitLab MCP tools
4. Gates any destructive action behind human approval
5. Executes only with explicit sign-off, logging every decision

The gate is the differentiator. Most AI agents act autonomously. Sentinel does not.

---

## How it was built

Built with Google ADK for multi-agent orchestration. Seven specialized subagents coordinate via
workflow commands (W1-W5). The orchestrator (CLAUDE.md) drives the entire build.

Tech stack: Python 3.12, Google ADK, Gemini 2.0 Flash, GitLab MCP, Cloud Run, Rich

---

## Challenges

[PLACEHOLDER: Fill after building - what was hard about the MCP integration, gate implementation, etc.]

---

## Accomplishments

The human risk-gate. It is not technically complex, but it is the right design.
An AI agent that halts itself, explains its reasoning, and waits for a human is
more useful in production than one that executes autonomously.

---

## What was learned

[PLACEHOLDER: Fill after building]

---

## What's next

- Slack/webhook integration for the gate (not just CLI)
- Multi-cloud support (GitHub Actions, CircleCI)
- Dashboard for audit log visualization

---

## Built With
Python, Google Generative AI (Gemini 2.0 Flash), Google ADK, MCP,
GitLab MCP Server, Google Cloud Run, Rich, Claude Code
