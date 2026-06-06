"""Tests for the risk gate — the differentiator — and the hold behavior.

Covers the W3 required cases:
- gate blocks without approval
- gate approves on yes
- gate logs every decision
- pipeline / act holds a destructive action without gate approval
"""

import json

import pytest

from src.sentinel.act import ActionOrchestrator
from src.sentinel.gate import RiskGate
from src.sentinel.models import ApprovalResult, ProposedAction


def _destructive_action() -> ProposedAction:
    return ProposedAction(
        action_type="rollback",
        destructive=True,
        description="ROLLBACK pipeline #12345",
        evidence=["47 files changed", "k8s/prod.yaml modified", "coverage -12.3%"],
        risk_score=0.87,
    )


def test_gate_blocks_without_approval(monkeypatch, tmp_path):
    """User says 'n' -> approved=False."""
    monkeypatch.setattr("src.sentinel.gate.sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: "n")
    gate = RiskGate(audit_log_path=str(tmp_path / "audit.log"))
    result = gate.request_approval(_destructive_action())
    assert result.approved is False


def test_gate_approves_on_yes(monkeypatch, tmp_path):
    """User says 'y' -> approved=True."""
    monkeypatch.setattr("src.sentinel.gate.sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: "y")
    gate = RiskGate(audit_log_path=str(tmp_path / "audit.log"))
    result = gate.request_approval(_destructive_action())
    assert result.approved is True


def test_gate_logs_every_decision(monkeypatch, tmp_path):
    """Audit log gets one JSON line per decision."""
    monkeypatch.setattr("src.sentinel.gate.sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda: "y")
    log_path = tmp_path / "audit.log"
    gate = RiskGate(audit_log_path=str(log_path))
    gate.request_approval(_destructive_action())
    gate.request_approval(_destructive_action())

    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 2
    entry = json.loads(lines[0])
    assert entry["action"] == "rollback"
    assert entry["approved"] is True
    assert "timestamp" in entry


def test_gate_details_then_decision(monkeypatch, tmp_path):
    """Selecting 'd' shows details, then a real decision is honored."""
    monkeypatch.setattr("src.sentinel.gate.sys.stdin.isatty", lambda: True)
    answers = iter(["d", "y"])
    monkeypatch.setattr("builtins.input", lambda: next(answers))
    gate = RiskGate(audit_log_path=str(tmp_path / "audit.log"))
    result = gate.request_approval(_destructive_action())
    assert result.approved is True


@pytest.mark.asyncio
async def test_pipeline_holds_without_gate_approval():
    """Destructive action with approval=False must NOT execute."""
    orchestrator = ActionOrchestrator(mcp_client=None)
    denied = ApprovalResult(approved=False, approver="human-cli", notes="n")
    result = await orchestrator.execute(_destructive_action(), denied)
    assert result.success is False
    assert "HELD" in result.action_taken


@pytest.mark.asyncio
async def test_pipeline_executes_with_approval():
    """Destructive action with approval=True executes via the (mock) client."""
    from src.mcp.client import MockGitLabMCPClient

    orchestrator = ActionOrchestrator(mcp_client=MockGitLabMCPClient())
    approved = ApprovalResult(approved=True, approver="human-cli", notes="y")
    result = await orchestrator.execute(_destructive_action(), approved)
    assert result.success is True
    assert "cancelled" in result.action_taken.lower()
