# ADR-001 — Multi-agent Risk Detection Pipeline with Human Gate

- **Status:** Accepted
- **Date:** 2026-06-06 (W1, Day 1)
- **Owners:** architect subagent
- **Supersedes:** none

## Context

Sentinel is our submission to the Google Cloud Rapid Agent Hackathon. The
problem: AI agents that take CI/CD actions (rollback, redeploy, patch) can act
on production **autonomously** — which is exactly when you least want a fully
autonomous agent. We need an agent that detects deployment risk, reasons about
it, proposes an action, and then **stops and asks a human** before doing
anything destructive.

We need an architecture that is:
- Demo-able in 3 minutes (terminal recording — see `docs/demo-script.md`).
- Mapped to every rubric criterion (Google Cloud, multi-agent, MCP,
  Responsible AI, technical depth, originality).
- Buildable in a 5-day sprint with no placeholders in `src/`.

## Decision

Build a **linear pipeline** with a **blocking human gate** before execution:

```
[Trigger: CI / PR / deploy signal]
        |
  DETECT     (RiskDetector.scan -> RiskReport)
        |
  DIAGNOSE   (GeminiDiagnoser.diagnose -> Diagnosis)   <- Gemini 2.0 Flash
        |
  ACT        (ActionOrchestrator.propose_action -> ProposedAction)  <- GitLab MCP
        |
  GATE       (RiskGate.request_approval -> ApprovalResult)   <- HUMAN, differentiator
        |
  EXECUTE    (ActionOrchestrator.execute -> ExecutionResult) <- only if approved
```

Concrete decisions:

1. **Language/runtime:** Python 3.12.
2. **Reasoning:** Gemini 2.0 Flash via `google-generativeai` (Google Cloud).
3. **Agent framework:** Google ADK for multi-agent orchestration.
4. **Actions:** GitLab MCP (official partner) as primary, GitHub MCP fallback,
   via the official `mcp` SDK.
5. **Gate (the soul):** placed **after** `act` proposes and **before**
   `execute`. Any action with `destructive=True` must pass `RiskGate`.
   The gate serializes the action + evidence + risk score + alternatives,
   presents a Rich-rendered sign-off panel, waits for a human decision, and
   logs it to an audit trail before anything runs.
6. **Gate transport (ADR-002):** blocking CLI input for the hackathon, not an
   async webhook — chosen for demo clarity. Webhook/Slack is post-hackathon.
7. **Demo mode (ADR-003):** `SENTINEL_DEMO=true` swaps in mock clients
   everywhere so the full pipeline runs without real API keys or live infra.
8. **Fail-safe default:** the gate denies by default. An action is only
   executed on an explicit, logged human approval.
9. **Deployment:** Google Cloud Run (W3).

Data contracts live in `src/sentinel/models.py`: `RiskSignal`, `RiskReport`,
`Diagnosis`, `ProposedAction`, `ApprovalResult`, `ExecutionResult`,
`SentinelResult`. Models are stdlib-only dataclasses so every module imports
them without pulling heavy SDKs.

## Consequences

**Enables (rubric coverage):**

| Rubric criterion | How this architecture satisfies it |
|------------------|------------------------------------|
| Uses Google Cloud | Gemini 2.0 Flash in DIAGNOSE; Cloud Run deploy |
| Multi-agent | 7 subagents + orchestrator; ADK |
| MCP integration | GitLab MCP in ACT/EXECUTE via official SDK |
| Responsible AI | Human risk-gate before destructive actions — THE feature |
| Technical depth | Async pipeline, streaming diagnosis, mockable clients |
| Demo quality | Linear pipeline reads cleanly in a 3-min terminal demo |
| Originality | Human-in-the-loop gate few competitors will build |

**Trade-offs:**
- Linear pipeline (not a graph) — simpler and more demo-able; we lose
  parallel branch evaluation, acceptable for the hackathon scope.
- Blocking CLI gate — not production-grade transport, but unambiguous on
  screen. Migration path to webhook/Slack is noted (ADR-002).
- Demo mode means two code paths (real vs mock); kept behind one env flag and
  one factory boundary to limit divergence.

**Follow-ups:** ADR-002 (gate transport) and ADR-003 (demo mode) are recorded
inline above and in `agents/architect.md`; promote to standalone ADR files if
they grow.
