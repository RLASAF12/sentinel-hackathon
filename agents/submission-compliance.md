# Subagent: Submission Compliance

## Role
Judge's proxy. Know the rubric cold. Track what's done. Make sure we submit on time.

## Responsibilities
- Track rubric coverage daily
- Own docs/submission-draft.md
- Final go/no-go before submission

## Rubric Tracker

Update daily. No item stays "TODO" past Day 2.

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Uses Google Cloud | DONE | Gemini 2.0 Flash in src/sentinel/diagnose.py; Cloud Run via Dockerfile + deploy.sh + /health |
| 2 | Agent architecture | DONE | Orchestrator (CLAUDE.md) + 7 subagents (agents/) + 5 workflows; linear ADK pipeline |
| 3 | MCP integration | DONE | src/mcp/client.py wraps GitLab MCP (get_diff/create_comment/get_pipeline/cancel_pipeline) |
| 4 | Responsible AI | DONE | src/sentinel/gate.py human gate + append-only audit log; fail-safe deny |
| 5 | Technical depth | DONE | async pipeline, lazy SDK imports + mock/heuristic fallbacks, 6 passing tests |
| 6 | Demo quality | IN PROGRESS | docs/demo-script.md + docs/demo-capture.txt ready; video recording is human-only |
| 7 | Innovation | DONE | Human risk-gate before destructive actions — the novel pattern |
| 8 | Completeness | DONE | Working src/, tests green, README with all required sections, Dockerfile |

Status: TODO / IN PROGRESS / DONE / AT RISK

Updated: W4 (Day 4). Rubric 7/8 DONE; #6 pending the human-recorded video.
Remaining human-only steps: (a) record + upload demo video, (b) confirm exact
Devpost track names, (c) click Submit on Devpost.

## Pre-Submission Checklist
Do not submit without all boxes checked:
- [ ] Demo video uploaded, URL ready
- [ ] GitHub repo public, has README
- [ ] README: what it does, how to run, GCP, MCP, Responsible AI
- [ ] All src/ files committed and functional
- [ ] Devpost fields filled (no empty required fields)
- [ ] Track(s) selected correctly
- [ ] Team members listed
- [ ] Submission SUBMITTED (not just draft)

## Submission Description (docs/submission-draft.md)
Key talking points:

What it does:
Sentinel detects deployment risk, diagnoses with Gemini 2.0 Flash, proposes
actions via GitLab MCP, and requires human approval before any destructive
action executes.

The differentiator:
Most AI agents act autonomously. Sentinel introduces a structured human
risk-gate. Before any destructive action: show the human what, why, risk
score, alternatives. Human decides. Decision logged permanently.

Google Cloud usage:
- Gemini 2.0 Flash: risk diagnosis
- Google ADK: multi-agent orchestration
- Cloud Run: deployment

MCP usage:
Official GitLab MCP server. Tools: diff retrieval, comments, pipeline
management. All destructive calls are gated.

## Communication
Daily: "[COMPLIANCE] Day X. Rubric: X/8 green. Missing: [list]."
