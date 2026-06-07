# Sentinel → Hackathon-Winning Build Prompt

> Paste this as the opening prompt of a Claude Code session opened on the
> `RLASAF12/sentinel-hackathon` repo **with Google Cloud + GitLab access**.
> It is self-contained: context, requirements, the winning strategy, and every
> fix with acceptance criteria.

## ROLE

You are a senior agent engineer. Take the existing Sentinel prototype and turn
it into a **qualifying, competitive** submission for the Google Cloud Rapid
Agent Hackathon, targeting the **GitLab partner bucket**. Work in small,
verified increments. Do not change the core idea — deepen the implementation
onto the required stack.

## CONTEXT — what Sentinel is

Sentinel is an AI agent for software delivery safety: "an agent that knows when
not to ship." It inspects a proposed change (merge request / pipeline),
diagnoses blast radius, proposes an action (e.g. rollback), and — critically —
requires explicit **human approval** before executing any destructive action,
writing an append-only audit trail of every decision. The human risk-gate is
the differentiator and maps onto the hackathon theme: "reason, plan, and
execute tasks under your oversight … while keeping you in control."

Current repo state (verified, runs, 6/6 tests, both gate paths, `/health` 200):
- `src/sentinel/detect.py` — `RiskDetector`: files changed, coverage delta,
  config/infra files, prod target; soft-OR risk score.
- `src/sentinel/diagnose.py` — `GeminiDiagnoser` (uses `gemini-2.0-flash`) +
  deterministic heuristic fallback.
- `src/sentinel/gate.py` — Rich CLI risk gate, append-only JSON audit log,
  fail-safe deny when non-interactive.
- `src/sentinel/act.py` — `ActionOrchestrator`: destructive actions HELD until
  approved, routed to GitLab MCP when approved.
- `src/sentinel/main.py` — async pipeline + `--serve` exposing `GET /health`.
- `src/mcp/client.py` — `GitLabMCPClient` (real, lazy mcp SDK) +
  `MockGitLabMCPClient` (default in demo mode).
- `tests/test_gate.py` — 6 passing tests. Plus `Dockerfile`, `deploy.sh`, docs,
  `README`, `LICENSE`.

**Preserve all of the above.** The gate + audit log are the differentiator.

## THE HACKATHON — rules that decide qualification & score

- **Deadline:** June 12, 2026 @ 00:00 GMT+3. Hosted on Devpost. Public repo required.
- **Must build (qualification):** a functional agent — powered by **Gemini 3**
  and **Google Cloud Agent Builder** — that integrates a **Partner Entity's MCP
  server** (→ GitLab) to solve a real challenge.
- **Must submit:** hosted project URL · public repo with a detectable OSS
  LICENSE visible in About · ~3-min demo video · selected track (GitLab) ·
  completed Devpost form.
- **Judging (equal weight):** Technological Implementation (Google Cloud +
  Partner interaction) · Design (UX) · Potential Impact · Quality of the Idea.
- **Buckets:** compete only vs other GitLab-track entries. 🥇 $5,000 · 🥈 $3,000
  · 🥉 $2,000. Two judges are GitLab staff — build something a GitLab DevSecOps
  person respects.

## PROGRESS (already done from the build container — no cloud access)

- **Fix 1 — LICENSE: DONE.** MIT at repo root.
- **Fix 2/3 — DRAFTED, needs cloud to run.** `src/sentinel/agent.py` implements
  the ADK `LlmAgent` (Gemini 3), the GitLab `McpToolset`, and the human gate as
  a `before_tool_callback`, written against the **verified June-2026 ADK API**
  (`McpToolset(connection_params=StdioConnectionParams(server_params=...))`;
  `before_tool_callback(tool, args, tool_context)` returning a dict to HOLD /
  None to proceed). The cloud session must: `pip install "google-adk>=1.14.0"`,
  confirm the live **Gemini 3 model id** (`SENTINEL_MODEL`, default
  `gemini-3-pro-preview`; docs point to `gemini-3.1-pro-preview`), provide
  `GITLAB_TOKEN` + confirm the GitLab MCP server command/tool names, then run
  and verify. Gate-callback logic is unit-tested without ADK (5 tests).
- **Fix 5 — Web UI: DONE locally.** `src/sentinel/web.py` (stdlib, zero new
  deps) renders the gate as the visual centerpiece; Approve executes + audits,
  Deny HOLDs + audits. Currently drives the existing pipeline; swap `_scan()` for
  an `agent.run_agent()` call once Fix 2 runs.
- Remaining blocked here: **G2 live Gemini 3, G3 live GitLab effect, G5 deploy**
  (no cloud / keys / gcloud in the container) and **G6 video / G7 submit**.

## CURRENT GAPS

| # | Gap | Severity |
|---|-----|----------|
| G1 | No Google Cloud Agent Builder / ADK — `google-adk` in requirements but never imported; orchestration is a hand-rolled loop. | 🔴 central requirement + criterion #1 |
| G2 | Wrong model — uses `gemini-2.0-flash`, brief requires **Gemini 3**. | 🔴 qualification |
| G3 | Partner integration is mocked by default (`MockGitLabMCPClient`); no real GitLab MCP effect. | 🔴 criterion #1 |
| G4 | No LICENSE file. | 🔴 hard gate (DONE — MIT added) |
| G5 | Not deployed — no hosted URL. | 🔴 submission requirement |
| G6 | Bare CLI UX. | 🟡 Design score |
| G7 | Demo + Devpost narrative not finalized around the "human oversight" thesis. | 🟡 score |

## WINNING STRATEGY (do not deviate)

Keep the idea. Re-architect the orchestration so the agent's brain is a **Google
ADK / Agent Builder agent running Gemini 3**, whose **tools are the real GitLab
MCP server**, and whose destructive actions are blocked by the human risk-gate.
This single move fixes G1+G2+G3 and turns the differentiator into a textbook
example of the brief's "keep you in control" theme.

Target use case: *Sentinel guards a GitLab project's deploy pipeline — reads the
MR and pipeline state via GitLab's MCP server, reasons about blast radius with
Gemini 3, and when it wants a destructive action (rollback / cancel deploy /
revert), it stops and requires human approval, logging an immutable audit trail.*

## THE FIXES — implement in order, verify each before moving on

### FIX 1 — LICENSE (G4) · ⏱ 2 min · DONE
- [x] OSS LICENSE (MIT) at repo root, canonical text so GitHub detects it.
- Acceptance: repo About shows the license name.

### FIX 2 — Rebuild orchestration on Agent Builder / ADK (G1, G2) · 🔴 biggest lift
- [ ] **Verify the exact current ADK API and Gemini 3 model id from official
  Google docs before coding** — do not guess import paths or model strings.
- [ ] Build an ADK agent (e.g. `google.adk.agents.LlmAgent`) with: `model` =
  current Gemini 3 id; `instruction` = Sentinel's mandate (assess blast radius,
  never execute destructive without human approval); `tools` = (a) risk-signal
  tool wrapping `RiskDetector`, (b) GitLab MCP toolset (Fix 3), (c) action tools
  (read = free, destructive = gated).
- [ ] Wire a `Runner` + session so it plans multi-step (detect → diagnose →
  propose → [gate] → act).
- [ ] Implement the HITL gate as an ADK guard — `before_tool_callback` (or
  ADK's tool-confirmation / long-running-tool HITL pattern; verify current API)
  — intercept any destructive tool call, route to `gate.py`, allow only on
  approval. Deny = fail-safe HOLD, logged. Preserve audit log on both paths.
- [ ] Keep the 6 tests green; add tests for the destructive-tool callback
  (HOLDs without approval; proceeds with it).
- Acceptance: one agent run plans + executes the flow; a **real Gemini 3**
  response drives diagnosis (not heuristic fallback); destructive calls blocked
  unless approved; pytest green.

### FIX 3 — Real GitLab MCP integration (G3)
- [ ] Connect the agent to the real GitLab MCP server via ADK's MCP toolset
  (e.g. `McpToolset`; verify current class/params). GitLab token via env
  (`.env.example`).
- [ ] Demonstrate meaningful use: read real MR metadata / pipeline status, and
  perform a real destructive action on approval (cancel a running pipeline /
  open a revert MR) against a **throwaway GitLab project** so it's safe + real.
- [ ] Keep `MockGitLabMCPClient` only as test/offline fallback — the default
  demo hits the real server.
- Acceptance: demo shows a real GitLab effect executed through the partner MCP
  server after human approval.

### FIX 4 — Deploy to Google Cloud → hosted URL (G5)
- [ ] Deploy on Google Cloud — preferred: **Vertex AI Agent Engine** (Agent
  Builder runtime); acceptable: Cloud Run hosting the agent service. Keep `/health`.
- [ ] Produce a reachable hosted URL.
- Acceptance: public URL responds; agent invokable there.

### FIX 5 — Web UI above a bare CLI (G6)
- [ ] Minimal web UI (single page is enough): change under review → agent's
  reasoning → risk-gate prompt (Approve / Deny / Details) → executed action +
  audit entry. **The approval moment is the visual centerpiece.**
- Acceptance: a non-engineer can watch the agent reason, hit the gate, and see
  the logged outcome without a terminal.

### FIX 6 — Demo video + narrative (G7)
- [ ] ~3-min video. Cold open: "AI agents that act are dangerous without a
  brake. Sentinel is the brake." Show both paths live (Deny = HOLD, Approve =
  real GitLab effect via MCP), the audit trail, and explicitly call out
  **Gemini 3 + Agent Builder + GitLab MCP**.
- Acceptance: ≤3 min, shows real partner effect + the human-control moment.

### FIX 7 — Devpost submission
- [ ] Hosted URL + public repo (with LICENSE) + video + GitLab track + form.
  Fill from `docs/submission-draft.md`, updated to the new architecture.
- [ ] Submit before June 12 00:00 GMT+3 — not at the deadline.
- Acceptance: Devpost shows "Submitted" to the GitLab track.

## DEFINITION OF DONE

- [ ] Agent built with Agent Builder / ADK (not a hand-rolled loop)
- [ ] Reasoning runs on **Gemini 3** (real call, verified in logs/demo)
- [ ] Real GitLab MCP integration with a demonstrable live effect
- [ ] HITL gate enforced **inside** the agent + append-only audit log
- [ ] LICENSE present and detected in About
- [ ] Hosted on Google Cloud, public URL works
- [ ] Web UI showing the approval moment
- [ ] ≤3-min demo video
- [ ] Devpost submitted to the GitLab track before the deadline
- [ ] pytest green

## GUARDRAILS — do NOT break these

1. Keep the human risk-gate and append-only audit log. The agent must **never**
   execute a destructive action without explicit human approval.
2. Do **not** silently fall back to the heuristic diagnoser or the GitLab mock
   in the demo path — the submission must exercise real Gemini 3 + real GitLab MCP.
3. Verify ADK imports, the HITL/tool-confirmation API, the MCP toolset class,
   and the Gemini 3 model id against current official docs **before coding** —
   no hardcoded guesses.
4. Commit in small steps; keep tests green throughout.
5. This is the GitLab bucket — make it credible to a GitLab DevSecOps engineer.

## REALITY CHECK

A real weekend of work on an unfamiliar stack (Agent Builder/ADK + live GitLab
MCP), not a polish pass — with ~5 days. The idea is winner-grade for the GitLab
bucket; the gap is implementation depth on the required stack. Do Fixes 1–4 or
don't submit: a polished demo that skips Agent Builder / Gemini 3 / real MCP
does not qualify, no matter how clean it looks.
