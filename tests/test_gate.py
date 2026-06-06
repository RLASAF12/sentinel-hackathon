"""Tests for the risk gate — the differentiator.

W1 stub tests. Full coverage of the interactive gate + audit log lands in W2
alongside the safeguard-risk-engineer implementation.
"""

from src.sentinel.gate import RiskGate
from src.sentinel.models import ApprovalResult, ProposedAction


def _destructive_action() -> ProposedAction:
    return ProposedAction(
        action_type="rollback",
        destructive=True,
        description="ROLLBACK pipeline #12345",
        evidence=["47 files changed", "k8s/prod.yaml modified"],
        risk_score=0.87,
    )


def test_gate_stub_returns_approval_result():
    """The gate always returns an ApprovalResult."""
    gate = RiskGate()
    result = gate.request_approval(_destructive_action())
    assert isinstance(result, ApprovalResult)


def test_gate_stub_fails_safe_by_denying():
    """Fail-safe: the W1 stub must NOT approve a destructive action by default."""
    gate = RiskGate()
    result = gate.request_approval(_destructive_action())
    assert result.approved is False
