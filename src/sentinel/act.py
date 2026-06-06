"""Act phase — propose and execute actions via MCP tools.

    ActionOrchestrator(mcp_client)
    ActionOrchestrator.propose_action(diagnosis) -> ProposedAction
    ActionOrchestrator.execute(action, approval) -> ExecutionResult

Rules:
- rollback / cancel are destructive=True (must pass the gate).
- alert / comment / hold are destructive=False.
- execute() refuses to run a destructive action without approval.approved.
"""

import logging
from datetime import datetime

from .models import (
    ApprovalResult,
    Diagnosis,
    ExecutionResult,
    ProposedAction,
)

logger = logging.getLogger(__name__)

DESTRUCTIVE_ACTIONS = {"rollback", "cancel"}


class ActionOrchestrator:
    """Turns a Diagnosis into a ProposedAction and executes approved actions."""

    def __init__(self, mcp_client=None) -> None:
        self.mcp_client = mcp_client

    def propose_action(self, diagnosis: Diagnosis) -> ProposedAction:
        """Propose an action based on the diagnosis."""
        action_type = diagnosis.recommended_action.lower().strip()
        destructive = action_type in DESTRUCTIVE_ACTIONS
        risk_score = self._severity_to_score(diagnosis)

        descriptions = {
            "rollback": "ROLLBACK pipeline #12345",
            "cancel": "CANCEL pipeline #12345",
            "hold": "HOLD deployment pending review",
            "alert": "ALERT team in merge request thread",
            "patch": "Suggest PATCH to mitigate risk",
        }
        description = descriptions.get(action_type, f"{action_type.upper()} action")

        action = ProposedAction(
            action_type=action_type,
            destructive=destructive,
            description=description,
            evidence=[diagnosis.root_cause, *diagnosis.alternatives[:2]],
            risk_score=risk_score,
        )
        logger.info(
            "Act: proposing %s (destructive=%s, risk=%.2f)",
            action_type,
            destructive,
            risk_score,
        )
        return action

    async def execute(
        self, action: ProposedAction, approval: ApprovalResult
    ) -> ExecutionResult:
        """Execute an action, honoring the gate approval result.

        A destructive action with no approval is discarded (held) with an
        audit entry. Non-destructive actions run without a gate.
        """
        audit = {
            "action": action.action_type,
            "destructive": action.destructive,
            "approved": approval.approved if approval else None,
            "approver": approval.approver if approval else None,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if action.destructive and not (approval and approval.approved):
            logger.info("Act: destructive action HELD (not approved).")
            return ExecutionResult(
                success=False,
                action_taken=f"HELD: {action.description} (no human approval)",
                audit_log={**audit, "result": "held"},
            )

        try:
            taken = await self._dispatch(action)
            return ExecutionResult(
                success=True,
                action_taken=taken,
                audit_log={**audit, "result": "executed"},
            )
        except Exception as exc:  # never crash the demo
            logger.error("Act: execution failed: %s", exc)
            return ExecutionResult(
                success=False,
                action_taken=f"FAILED: {action.description} ({exc})",
                audit_log={**audit, "result": "error", "error": str(exc)},
            )

    async def _dispatch(self, action: ProposedAction) -> str:
        """Route an approved action to the right MCP tool."""
        if self.mcp_client is None:
            return f"NO-OP (no MCP client): {action.description}"

        project_id = "demo-project"
        if action.action_type in ("rollback", "cancel"):
            await self.mcp_client.cancel_pipeline(project_id, "12345")
            return "Pipeline #12345 cancelled via GitLab MCP"
        if action.action_type == "alert":
            await self.mcp_client.create_comment(
                project_id, 1847, "Sentinel: elevated deployment risk detected."
            )
            return "Alert comment posted to MR !1847 via GitLab MCP"
        return f"Recorded: {action.description}"

    @staticmethod
    def _severity_to_score(diagnosis: Diagnosis) -> float:
        mapping = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 0.9}
        base = mapping.get(diagnosis.severity.value, 0.5)
        # Blend in model confidence so a confident high reads slightly higher.
        return round(min(1.0, base + 0.1 * diagnosis.confidence), 2)
