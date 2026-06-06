# W1 — Scope Lock

## Trigger
Say "Run W1" in Claude Code.

## Purpose
Lock the scope on Day 1. No building until W1 is done.

## Steps

### 1. Read Context
- Read CLAUDE.md (you are the orchestrator)
- Read PLAN.md (5-day plan and rubric map)
- Confirm: we are building Sentinel for Google Cloud Rapid Agent Hackathon

### 2. Resolve Devpost Unknowns
Go to the Devpost hackathon page and find:
- [ ] Exact track names for submission
- [ ] GCP credit situation (confirm we use your own account)
Document findings in a new file: docs/devpost-unknowns-resolved.md

### 3. Confirm Tech Stack
Verify these are available and note any version constraints:
- Python 3.12
- google-generativeai (Gemini 2.0 Flash)
- google-adk (Agent Development Kit)
- mcp (Model Context Protocol SDK)
- gitlab MCP server (official)
- streamlit or rich (for demo UI)

Create: docs/tech-stack-confirmed.md

### 4. Create Source Skeleton
Create empty files with stub imports:
- src/__init__.py
- src/sentinel/__init__.py
- src/sentinel/detect.py (stub)
- src/sentinel/diagnose.py (stub)
- src/sentinel/act.py (stub)
- src/sentinel/gate.py (stub)
- src/sentinel/main.py (stub)
- src/mcp/__init__.py
- src/mcp/client.py (stub)
- tests/__init__.py
- tests/test_gate.py (stub)
- requirements.txt (with all dependencies)
- pyproject.toml

### 5. Write ADR-001
Create docs/adr-001-architecture.md:
- Title: Multi-agent Risk Detection Pipeline with Human Gate
- Context: what we're building and why
- Decision: Python + ADK + Gemini + GitLab MCP + human gate
- Consequences: what this enables (rubric coverage)

### 6. Confirm Demo Storyboard
Review docs/demo-script.md
- Confirm the golden path runs through gate.py
- Note: gate is THE differentiator — the demo lives or dies here

## Done When
- [ ] docs/devpost-unknowns-resolved.md exists
- [ ] docs/tech-stack-confirmed.md exists
- [ ] All src/ stub files exist
- [ ] requirements.txt exists
- [ ] docs/adr-001-architecture.md exists
- [ ] python -c "import src.sentinel.main" runs without errors

## Hand Off
When done, say: "W1 complete. Ready for W2."
