"""Act phase — propose and execute actions via MCP tools.

W1 stub. Real MCP-backed actions land in W2/W3.
Interface contract:
    ActionOrchestrator(mcp_client)
    ActionOrchestrator.propose_action(diagnosis: Diagnosis) -> ProposedAction
    ActionOrchestrator.execute(action, approval: ApprovalResult) -> ExecutionResult
"""

import logging

from .models import (
    ApprovalResult,
    Diagnosis,
    ExecutionResult,
    ProposedAction,
)

logger = logging.getLogger(__name__)


class ActionOrchestrator:
    """Turns a Diagnosis into a ProposedAction and executes approved actions.

    Stub: proposals/executions are placeholders. Implemented in W2/W3.
    """

    def __init__(self, mcp_client=None) -> None:
        self.mcp_client = mcp_client

    def propose_action(self, diagnosis: Diagnosis) -> ProposedAction:
        """Propose an action based on the diagnosis.

        Args:
            diagnosis: the Diagnosis from the diagnose phase.

        Returns:
            A ProposedAction. Destructive actions must pass the gate.
        """
        logger.info("ActionOrchestrator.propose_action stub; W2 will implement.")
        return ProposedAction(
            action_type="hold",
            destructive=False,
            description="(stub) action pending W2 implementation",
            evidence=[],
            risk_score=0.0,
        )

    def execute(
        self, action: ProposedAction, approval: ApprovalResult
    ) -> ExecutionResult:
        """Execute an action, honoring the gate approval result.

        Args:
            action: the ProposedAction to execute.
            approval: the human ApprovalResult from the gate.

        Returns:
            An ExecutionResult with an audit log.
        """
        logger.info("ActionOrchestrator.execute stub; W3 will implement.")
        return ExecutionResult(
            success=False,
            action_taken="(stub) no-op pending implementation",
            audit_log={},
        )
