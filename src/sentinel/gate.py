"""Risk gate — the human sign-off before any destructive action.

THIS IS THE DIFFERENTIATOR. W1 stub only; the full Rich-rendered gate with
audit logging is owned by the safeguard-risk-engineer subagent and lands in W2.

Interface contract:
    RiskGate(audit_log_path: str)
    RiskGate.request_approval(action: ProposedAction) -> ApprovalResult
"""

import logging

from .models import ApprovalResult, ProposedAction

logger = logging.getLogger(__name__)


class RiskGate:
    """Presents a destructive action for human approval and logs the decision.

    Stub: auto-denies (fail-safe) and logs. The real interactive gate +
    audit trail is implemented in W2 by the safeguard-risk-engineer.
    """

    def __init__(self, audit_log_path: str = "sentinel-audit.log") -> None:
        self.audit_log_path = audit_log_path

    def request_approval(self, action: ProposedAction) -> ApprovalResult:
        """Request human approval for a proposed action.

        Args:
            action: the ProposedAction awaiting sign-off.

        Returns:
            An ApprovalResult. Stub defaults to NOT approved (fail-safe):
            the gate must never let an action through by accident.
        """
        logger.info("RiskGate.request_approval stub; W2 will implement gate UI.")
        return ApprovalResult(
            approved=False,
            approver="(stub) no human prompt yet",
            notes="W1 stub fail-safe deny",
        )
