# ADR-001 — Agent pipeline with an in-loop human gate

- **Status:** Accepted
- **Date:** 2026-06-07

## Context

AI agents that take CI/CD actions (cancel a deploy, revert a change, roll back)
can act on production **autonomously** — exactly when you least want full
autonomy. We need an agent that detects deployment risk, reasons about it,
proposes an action, and then **stops and asks a human** before doing anything
destructive — with an auditable record of every decision.

## Decision

The agent is a Google **ADK `LlmAgent` running Gemini 3** whose tools are the
**real GitLab MCP server** plus a `risk_scan` function tool. The flow:

```
   GitLab pipeline (live)
        │
  DETECT     risk_scan / RiskDetector  -> RiskReport
        │
  DIAGNOSE   Gemini 3 over MCP-sourced pipeline metadata -> Diagnosis
        │
  PROPOSE    a tool call, e.g. cancel_pipeline(project, pipeline)
        │
  GATE       before_tool_callback -> human approval   ← differentiator
        │
  EXECUTE    the GitLab MCP tool runs (only if approved); else HOLD
```

Concrete decisions:

1. **Runtime:** Python 3.12.
2. **Reasoning:** Gemini 3 (`gemini-3.1-pro-preview`) on Vertex AI. Verified
   servable on the Vertex *global* endpoint; auth via Application Default
   Credentials (the Cloud Run service account), no key material in the image.
3. **Agent framework:** Google ADK (`LlmAgent`, `Runner`, in-memory sessions).
4. **Actions:** GitLab MCP server (PAT, `api` scope) via the `mcp` SDK / ADK
   `McpToolset`. Reads are free; destructive tools are gated.
5. **Gate (the soul):** enforced *inside the agent loop* via ADK's
   `before_tool_callback`. A destructive tool call is intercepted before it can
   run — return a value to HOLD, return `None` to proceed. This means no tool,
   present or future, can bypass the gate. The decision (Approve and Deny) is
   appended to an audit trail before anything executes.
6. **Fail-safe default:** the gate denies in non-interactive contexts unless
   `SENTINEL_AUTO_APPROVE=true` is set explicitly.
7. **Surfaces:** the same gated flow is exposed via a Rich CLI and a
   dependency-free web UI (the deployed Cloud Run surface).
8. **Deployment:** Google Cloud Run.

Data contracts live in `src/sentinel/models.py` (`RiskSignal`, `RiskReport`,
`Diagnosis`, `ProposedAction`, `ApprovalResult`, `ExecutionResult`) as
stdlib-only dataclasses, so every module imports them without heavy SDKs.

## Consequences

- Putting the gate in `before_tool_callback` (rather than beside the agent)
  guarantees coverage of every destructive tool without per-tool wiring.
- An offline mode (`SENTINEL_DEMO=true`) swaps in a deterministic diagnoser and
  mock client so the flow runs with no credentials — this doubles as the test
  path. Two code paths are kept behind one env flag to limit divergence.
- Blocking gate input is unambiguous on screen but not a production transport;
  a webhook/Slack transport is a natural follow-up.
