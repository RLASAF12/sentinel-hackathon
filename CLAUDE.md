# CLAUDE.md — Sentinel Orchestrator Master Prompt

## Project: Sentinel
### "The agent that knows when not to ship."

Google Cloud Rapid Agent Hackathon submission.

---

## Mission

Build **Sentinel** — an AI agent that detects deployment risk, diagnoses root cause using Gemini, acts via partner MCP tools, then **stops at a human risk-gate before shipping**. The gate is the differentiator.

---

## How Claude Code Uses This Repo

### Quick Start
Open this repo in Claude Code, then say:
```
Run W1.
```

### Workflow Commands
- `Run W1` → Scope Lock (confirm concept, unknowns, tech stack)
- `Run W2` → Parallel Build (architect + builder work simultaneously)
- `Run W3` → Integration (wire MCP + Gemini + gate together)
- `Run W4` → Demo + Submit (record demo, fill Devpost)
- `Run W5` → Content Chain (LinkedIn post, README polish)

### Active Subagents
- **architect** — system design, ADRs, API contracts
- **builder** — writes all source code
- **mcp-integration-engineer** — wires MCP tools
- **safeguard-risk-engineer** — owns the risk gate logic
- **demo-director** — owns the 3-min demo narrative
- **submission-compliance** — tracks rubric coverage
- **content-positioning** — LinkedIn + README tone

---

## Sentinel Architecture

```
[Trigger: CI event / PR / deploy signal]
        |
  DETECT (risk scan)
        |
  DIAGNOSE (Gemini 2.0 Flash — root cause analysis)
        |
  ACT (MCP tools — rollback, alert, patch suggestion)
        |
  GATE  <-- THIS IS THE DIFFERENTIATOR
  (human sign-off required before any destructive action)
        |
  SHIP or HOLD (logged, auditable)
```

### Tech Stack
- **Runtime**: Python 3.12
- **AI**: Gemini 2.0 Flash (google-generativeai)
- **Agent Framework**: Google ADK (Agent Development Kit)
- **MCP**: Model Context Protocol client (official SDK)
- **Partner MCP**: GitLab MCP (primary), GitHub MCP (fallback)
- **Cloud**: Google Cloud Run (deployment)
- **Demo**: Streamlit or simple CLI with rich output

### The Risk Gate (gate.py)
The gate is Sentinel's soul. Before any action tagged destructive=True:
1. Sentinel serializes the proposed action + evidence
2. Presents a structured sign-off request (what, why, risk score, alternatives)
3. Waits for human approval via webhook / CLI / Slack
4. Logs the decision with timestamp and approver
5. Only then executes — or discards with audit trail

---

## Rubric Coverage Map

| Criterion | Sentinel Feature | Confidence |
|-----------|-----------------|------------|
| Uses Google Cloud | Cloud Run + Vertex AI / Gemini | High |
| Multi-agent | 7 subagents + orchestrator | High |
| MCP integration | GitLab MCP (partner) | High |
| Responsible AI | Human risk-gate (THE feature) | High |
| Technical depth | ADK + streaming + async | High |
| Demo quality | 3-min script, live risk gate | High |
| Originality | Risk-gate nobody else builds | High |

---

## 5-Day Sprint

| Day | Goal | Done When |
|-----|------|-----------|
| 1 | Scope Lock + skeleton | W1 complete, ADR written |
| 2 | Core build | detect + diagnose running |
| 3 | Integration | MCP + gate wired, tests pass |
| 4 | Demo + submit | video recorded, Devpost submitted |
| 5 | Buffer / polish | README stellar, LinkedIn drafted |

---

## Rules for All Subagents

1. **Ship working code** — no placeholders in src/
2. **Gate first** — any action touching prod requires gate.py approval
3. **Log everything** — decisions are auditable
4. **Rubric-driven** — every feature must map to a rubric criterion
5. **Demo-first thinking** — if it cannot be shown in 3 min, cut it

---

*Built with Claude Code. Hackathon mode: active.*
