# Subagent: Safeguard / Risk Engineer

## Role
You own the risk gate. This is THE differentiator. Make it bulletproof and beautiful in demo.

## Owned Files
- src/sentinel/gate.py
- tests/test_gate.py

## The Gate Philosophy
The gate exists because AI agents should not have unilateral power over destructive actions.
Before any destructive action: STOP. Show the human. WAIT. LOG. Only then act.

## Gate Implementation (src/sentinel/gate.py)

import json
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sentinel.models import ProposedAction, ApprovalResult

console = Console()
logger = logging.getLogger(__name__)

class RiskGate:
    def __init__(self, audit_log_path: str = "sentinel-audit.log"):
        self.audit_log_path = audit_log_path

    def request_approval(self, action: ProposedAction) -> ApprovalResult:
        self._display_gate(action)
        decision = self._wait_for_input()
        result = self._process_decision(decision, action)
        self._log_decision(result, action)
        return result

    def _display_gate(self, action: ProposedAction):
        table = Table(show_header=False, box=None, padding=(0,1))
        table.add_row("[bold red]Action[/]", action.description)
        table.add_row("[bold red]Risk Score[/]", f"{action.risk_score:.0%}")
        table.add_row("[bold red]Type[/]", action.action_type.upper())
        for i, ev in enumerate(action.evidence[:3]):
            table.add_row(f"[dim]Evidence {i+1}[/]", ev)
        console.print(Panel(
            table,
            title="[bold red]SENTINEL RISK GATE[/bold red]",
            subtitle="[dim]Human approval required[/dim]",
            border_style="red"
        ))

    def _wait_for_input(self) -> str:
        console.print("\nApprove? [green](y)[/] / [red](n)[/] / [blue](d)[/]etails: ", end="")
        return input().strip().lower()

    def _process_decision(self, decision: str, action: ProposedAction) -> ApprovalResult:
        return ApprovalResult(
            approved=decision in ('y', 'yes'),
            approver="human-cli",
            notes=f"Decision: {decision}",
            timestamp=datetime.utcnow()
        )

    def _log_decision(self, result: ApprovalResult, action: ProposedAction):
        entry = {
            "timestamp": result.timestamp.isoformat(),
            "action": action.action_type,
            "approved": result.approved,
            "approver": result.approver,
            "risk_score": action.risk_score,
        }
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        logger.info(f"Gate decision logged: {entry}")

## Tests Required
- test_gate_blocks_without_approval: user says 'n' -> approved=False
- test_gate_approves_on_yes: user says 'y' -> approved=True
- test_gate_logs_every_decision: audit log file updated after each call
- test_gate_blocks_execution: act.py must not execute if approved=False

## Communication
"[SAFEGUARD] gate.py complete. Gate blocks correctly. All tests pass. Audit log: working."
