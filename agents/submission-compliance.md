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
| 1 | Uses Google Cloud | TODO | Gemini + Cloud Run |
| 2 | Agent architecture | TODO | ADK + 7 subagents |
| 3 | MCP integration | TODO | GitLab MCP |
| 4 | Responsible AI | TODO | Risk gate |
| 5 | Technical depth | TODO | |
| 6 | Demo quality | TODO | 3-min video |
| 7 | Innovation | TODO | |
| 8 | Completeness | TODO | |

Status: TODO / IN PROGRESS / DONE / AT RISK

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
