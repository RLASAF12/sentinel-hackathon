"""Tests for the ADK before_tool_callback gate (Fix 2 acceptance).

These exercise the human-in-the-loop guard without requiring google-adk: the
callback only reads ``tool.name``, so a tiny stub stands in for an ADK BaseTool.
"""

from dataclasses import dataclass

from src.sentinel.agent import is_destructive, make_gate_callback
from src.sentinel.gate import RiskGate


@dataclass
class _StubTool:
    name: str


def test_is_destructive_matches_keywords():
    assert is_destructive("cancel_pipeline")
    assert is_destructive("revert_merge_request")
    assert is_destructive("rollback_deploy")
    assert not is_destructive("get_merge_request_diff")
    assert not is_destructive("create_merge_request_note")


def test_callback_holds_destructive_without_approval(monkeypatch, tmp_path):
    """Denied destructive tool -> returns a dict, so ADK SKIPS the real call."""
    monkeypatch.setattr("src.sentinel.gate.sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: "n")
    cb = make_gate_callback(RiskGate(audit_log_path=str(tmp_path / "a.log")))
    result = cb(_StubTool("cancel_pipeline"), {"pipeline_id": "12345"}, None)
    assert isinstance(result, dict)
    assert result["status"] == "held"


def test_callback_proceeds_destructive_with_approval(monkeypatch, tmp_path):
    """Approved destructive tool -> returns None, so ADK RUNS the real call."""
    monkeypatch.setattr("src.sentinel.gate.sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: "y")
    cb = make_gate_callback(RiskGate(audit_log_path=str(tmp_path / "a.log")))
    result = cb(_StubTool("cancel_pipeline"), {"pipeline_id": "12345"}, None)
    assert result is None


def test_callback_skips_gate_for_readonly_tool(tmp_path):
    """Non-destructive tool -> None, and no human prompt is required."""
    cb = make_gate_callback(RiskGate(audit_log_path=str(tmp_path / "a.log")))
    result = cb(_StubTool("get_merge_request_diff"), {"mr_iid": 1}, None)
    assert result is None


def test_callback_logs_denied_decision(monkeypatch, tmp_path):
    """A denied destructive call is written to the audit trail."""
    monkeypatch.setattr("src.sentinel.gate.sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: "n")
    log = tmp_path / "a.log"
    cb = make_gate_callback(RiskGate(audit_log_path=str(log)))
    cb(_StubTool("cancel_pipeline"), {"pipeline_id": "12345"}, None)
    assert log.exists() and log.read_text().strip()
