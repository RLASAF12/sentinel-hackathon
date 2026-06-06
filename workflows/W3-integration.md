# W3 — Integration

## Trigger
Say "Run W3" after W2 is complete.

## Purpose
Wire all components together: MCP client + Gemini diagnose + gate. Make the full pipeline run end-to-end.

## Prerequisite
W2 complete: detect.py, diagnose.py, gate.py all have working implementations.

## Steps

### 1. MCP Client (mcp-integration-engineer)
File: src/mcp/client.py

Implement GitLab MCP client with these tools:
- get_merge_request_diff(project_id, mr_iid) -> str
- create_merge_request_note(project_id, mr_iid, body) -> bool
- get_pipeline(project_id, pipeline_id) -> dict
- cancel_pipeline(project_id, pipeline_id) -> bool  [DESTRUCTIVE]

Use MockGitLabMCPClient when SENTINEL_DEMO=true.

### 2. Act Module (builder)
File: src/sentinel/act.py

ActionOrchestrator.propose_action(diagnosis) -> ProposedAction
ActionOrchestrator.execute(action, approval) -> ExecutionResult

Rules:
- Only executes if approval.approved == True
- Tags rollback/cancel as destructive=True
- Tags alerts/comments as destructive=False

### 3. Main Pipeline (builder)
File: src/sentinel/main.py

async def run_sentinel(context: dict) -> SentinelResult:
    report = detector.scan(context)
    if report.score < THRESHOLD: return clear
    diagnosis = diagnoser.diagnose(report, context.diff)
    proposed = orchestrator.propose_action(diagnosis)
    if proposed.destructive:
        approval = gate.request_approval(proposed)
        if not approval.approved: return held
    result = orchestrator.execute(proposed, approval)
    return executed

### 4. Tests
File: tests/test_gate.py
- test_gate_blocks_without_approval()
- test_gate_approves_on_yes()
- test_gate_logs_all_decisions()
- test_pipeline_holds_without_gate_approval()

### 5. Cloud Run Skeleton
Create Dockerfile:
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "sentinel.main", "--serve"]

Create deploy.sh for Cloud Run deployment.

## Done When
- [ ] Full pipeline runs: detect -> diagnose -> gate -> act -> execute
- [ ] tests/test_gate.py all pass
- [ ] Dockerfile builds
- [ ] Cloud Run URL responds to GET /health

## Hand Off
Say: "W3 complete. Ready for W4."
