# PLAN.md — Sentinel 5-Day Hackathon Plan

## Concept
**Sentinel** — AI agent that detects deployment risk, diagnoses with Gemini 2.0 Flash, acts via MCP tools, then blocks at a human risk-gate.

**Core differentiator**: The risk gate. Almost no other submission will have human-in-the-loop approval for destructive actions.

---

## Rubric Map

| Rubric Criterion | Our Answer | Evidence |
|-----------------|------------|---------|
| Google Cloud usage | Gemini 2.0 Flash + Cloud Run | src/sentinel/diagnose.py |
| Agent architecture | Multi-agent with ADK | agents/ directory |
| MCP integration | GitLab MCP (official partner) | src/mcp/client.py |
| Responsible AI | Human risk-gate | src/sentinel/gate.py |
| Innovation | Risk-gate pattern | NOVEL: nobody builds this |
| Demo quality | 3-min narrative | docs/demo-script.md |
| Technical execution | Working code, tests | src/ + tests/ |

---

## 5-Day Sprint Plan

### Day 1 — Scope Lock (W1)
- [ ] Run W1 workflow
- [ ] Confirm tech stack (Python + ADK + Gemini + GitLab MCP)
- [ ] Resolve Devpost unknowns: track name, GCP credits
- [ ] Create src/ skeleton with empty files
- [ ] Write ADR-001: Architecture Decision Record
- [ ] Confirm demo golden path storyboard

**Done when**: ADR-001 exists, all src/ files created, skeleton imports work

### Day 2 — Core Build (W2)
- [ ] Run W2 workflow
- [ ] detect.py: scan for risk signals in a PR/commit
- [ ] diagnose.py: call Gemini 2.0 Flash with context
- [ ] gate.py: implement approval request + wait loop
- [ ] Basic CLI test: can run detect -> diagnose -> gate

**Done when**: python -m sentinel.main --demo runs without errors

### Day 3 — Integration (W3)
- [ ] Run W3 workflow
- [ ] Wire GitLab MCP client
- [ ] act.py: rollback + alert via MCP
- [ ] gate.py: full approval flow (CLI approval for demo)
- [ ] test_gate.py: tests pass
- [ ] Deploy skeleton to Cloud Run

**Done when**: Full pipeline runs, tests pass, Cloud Run URL exists

### Day 4 — Demo + Submit (W4)
- [ ] Run W4 workflow
- [ ] Record 3-minute demo video
- [ ] Write Devpost submission
- [ ] README with architecture diagram
- [ ] Submit before deadline

**Done when**: Devpost submitted with video link

### Day 5 — Buffer / Polish (W5)
- [ ] Run W5 workflow
- [ ] Polish README
- [ ] Draft LinkedIn post
- [ ] Final rubric check
- [ ] Fix any last-minute issues

---

## Devpost Unknowns (Resolve Day 1)

1. **Track names** — Check Devpost for exact track names. Default: "Best Use of Google Cloud", "Best Use of MCP"
2. **GCP Credits** — Use your own GCP account. Non-blocking.

---

## Golden Path Demo Storyboard (3 minutes)

**Scene 1** (0:00-0:30) — Problem statement
"You're about to deploy. Sentinel detects 3 risk signals."

**Scene 2** (0:30-1:15) — Detect + Diagnose
Show Sentinel running: risk scan output, then Gemini diagnosis appears

**Scene 3** (1:15-2:00) — Act + Gate
MCP proposes rollback. Gate appears: "APPROVAL REQUIRED. Risk: HIGH. Approve? [Y/N]"
Audience sees the gate block. This is the moment.

**Scene 4** (2:00-2:30) — Approve and ship
Human approves. Action executes. Audit log appears.

**Scene 5** (2:30-3:00) — Architecture + wrap
Quick architecture diagram. "Sentinel: the agent that knows when not to ship."

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| GitLab MCP API changes | Low | High | Pin version, test Day 1 |
| Gemini quota exceeded | Medium | High | Set rate limits, cache responses |
| Cloud Run deploy fails | Low | Medium | Test deploy Day 3 |
| Demo video quality poor | Medium | High | Practice 3x, use rich CLI output |
| Devpost deadline missed | Low | Critical | Submit Day 4, buffer Day 5 |

---

## Submission Checklist

- [ ] Devpost submission complete
- [ ] Video demo uploaded (3 min max)
- [ ] GitHub repo public
- [ ] README with: what it does, how to run, architecture
- [ ] GCP usage documented
- [ ] MCP integration documented
- [ ] Responsible AI section in README
- [ ] Team members listed
- [ ] Track(s) selected

---

*This plan is owned by the submission-compliance subagent. Update daily.*
