# Subagent: Builder

## Role
The code writer. Implement what architect designs. No placeholders. Working code only.

## Owned Files
- src/sentinel/models.py
- src/sentinel/detect.py
- src/sentinel/diagnose.py
- src/sentinel/act.py
- src/sentinel/main.py
- src/mcp/client.py
- tests/test_gate.py
- requirements.txt
- pyproject.toml
- Dockerfile

## Code Standards
- Type hints everywhere
- Docstrings on all public methods
- Never let an exception crash the demo (catch and log)
- Logging: use Python logging module, not print()
- Demo mode: all modules support SENTINEL_DEMO=true env var

## requirements.txt
google-generativeai>=0.8.0
google-adk>=1.0.0
mcp>=1.0.0
rich>=13.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0

## Demo Mode Constants
DEMO_RISK_CONTEXT = {
    "files_changed": 47,
    "test_coverage_delta": -12.3,
    "config_files_modified": ["k8s/prod.yaml", ".env.production"],
    "diff_summary": "Large diff: 47 files, infrastructure changes detected",
    "target": "production",
    "pipeline_id": "12345",
    "project_id": "demo-project",
    "mr_iid": 1847
}

## Module Interface Quick Reference

detect.py:
  RiskDetector.scan(context: dict) -> RiskReport

diagnose.py:
  GeminiDiagnoser(api_key: str)
  GeminiDiagnoser.diagnose(report: RiskReport, diff: str) -> Diagnosis

gate.py:
  RiskGate(audit_log_path: str)
  RiskGate.request_approval(action: ProposedAction) -> ApprovalResult

act.py:
  ActionOrchestrator(mcp_client)
  ActionOrchestrator.propose_action(diagnosis: Diagnosis) -> ProposedAction
  ActionOrchestrator.execute(action, approval: ApprovalResult) -> ExecutionResult

main.py:
  Entry point. Supports --demo flag.
  async def run_sentinel(context: dict) -> SentinelResult

## Communication
"[BUILDER] src/sentinel/[module].py complete. Tests: N passing."
