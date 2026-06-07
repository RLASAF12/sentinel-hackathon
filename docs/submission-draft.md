# Devpost Submission Draft

Status: READY — fill the one human-only item (demo video URL), confirm the exact
track name on the live Devpost page, then submit.

---

## Project Name
Sentinel

## Tagline
The AI agent that knows when not to ship.

## Hosted Project URL
https://sentinel-258340350085.us-central1.run.app  (Google Cloud Run, public)

## Demo Video
[TODO — human: upload the recording (unlisted YouTube or Loom) and paste URL.
Recording guide: docs/demo-script.md. Phase-by-phase stills: scripts/shots/]

## GitHub Repository
https://github.com/RLASAF12/sentinel-hackathon  (MIT licensed)

## Track
GitLab partner track. (Also relevant: Best Use of Google Cloud. Confirm exact
spelling on the live Devpost page.)

## Technologies
Python 3.12, Gemini 3 (`gemini-3.1-pro-preview`) on Vertex AI, Google Agent
Development Kit (ADK), Model Context Protocol (MCP), GitLab MCP server, Google
Cloud Run, Google Cloud Vertex AI, Rich, Claude Code

---

## What it does

Sentinel is an AI deployment-safety agent for GitLab — "an agent that knows when
not to ship." It guards a GitLab project's deploy pipeline:

1. **Detects** risk on a live pipeline — production target, pipeline state, and a
   sharp test-coverage drop — and computes an aggregate 0–1 risk score.
2. **Diagnoses** blast radius with **Gemini 3** (`gemini-3.1-pro-preview` on
   Vertex AI), reasoning over the real pipeline metadata pulled through GitLab's
   MCP server.
3. **Proposes** a destructive action when warranted — e.g. `cancel_pipeline`.
4. **Gates** that action behind explicit human approval. The gate is enforced
   *inside the agent loop* via an ADK `before_tool_callback`: a destructive tool
   call is intercepted before it can run.
5. **Executes** only on sign-off — the real GitLab pipeline is cancelled through
   the MCP server — and appends every decision (Approve **and** Deny) to an
   append-only audit log.

The gate is the differentiator. Most AI agents act autonomously. Sentinel
deliberately stops and asks a human before doing anything destructive — the
hackathon theme of "reason, plan, and execute under your oversight" made literal.

---

## How it was built

The agent's brain is a Google **ADK `LlmAgent` running Gemini 3** on Vertex AI.
Its tools are the **real GitLab MCP server** (pipelines, merge requests) plus a
`risk_scan` function tool. Every destructive tool call is routed through the
human risk-gate by an ADK `before_tool_callback` — return a value to HOLD,
return `None` to proceed — so the gate lives in the agent loop, not bolted on
beside it. Approve and Deny both write to one append-only JSON audit trail.

The same gated flow is exposed two ways: a Rich CLI and a dependency-free web UI
(stdlib `http.server`) whose centerpiece is the approval moment — change under
review → Gemini 3 reasoning → Approve/Deny → executed action + audit entry. The
web UI is deployed to **Cloud Run** and authenticates to Vertex via the runtime
service account (no key material in the image).

Verified live, end-to-end against GitLab.com: Gemini 3 read a real running
pipeline through MCP, proposed `cancel_pipeline`, the gate held it until a human
approved, and the pipeline was then **cancelled for real** — with the deny path
leaving the pipeline running, both logged.

Tech stack: Python 3.12, Google ADK, Gemini 3 (Vertex AI), GitLab MCP, Cloud Run.

---

## Challenges

- **Building on a fast-moving stack.** ADK and the Gemini 3 model ids shifted;
  we verified every import and confirmed the live model (`gemini-3.1-pro-preview`
  serves on the Vertex *global* endpoint) against the running API rather than
  guessing — and kept the gate-callback logic unit-tested without ADK installed.
- **Designing the gate to be safe by default.** It must never let a destructive
  action through by accident: non-interactive contexts fail-safe to *deny*, with
  an explicit opt-in for unattended recordings.
- **A real partner integration, not a mock.** The destructive action cancels a
  real GitLab pipeline through the MCP server. (The official GitLab MCP server
  needs paid Duo; we use the PAT-based GitLab MCP so any account can run it.)

---

## Accomplishments

The human risk-gate, enforced inside a real ADK + Gemini 3 agent, acting on real
GitLab infrastructure through MCP. An agent that halts itself, explains its
reasoning (what, why, risk score, alternatives), waits for a human, logs the
decision permanently, and only then acts is more trustworthy in production than
one that executes autonomously. Fully working end-to-end, hosted on Cloud Run,
with tests and an audit trail.

---

## What was learned

- A small, well-placed human checkpoint changes the trust profile of an agent
  far more than additional autonomy does.
- Putting the gate *inside* the agent loop (ADK `before_tool_callback`) rather
  than beside it means no tool — present or future — can bypass it.
- Fail-safe defaults belong at the gate boundary, not in the caller.

---

## What's next

- Slack / webhook approval transport for the gate (not just CLI/web).
- Multi-provider CI support (GitHub Actions, CircleCI) behind the same interface.
- A dashboard to visualize the audit log and risk trends over time.

---

## Built With
Python, Gemini 3 (Vertex AI), Google ADK, MCP, GitLab MCP Server,
Google Cloud Run, Google Cloud Vertex AI, Rich, Claude Code
