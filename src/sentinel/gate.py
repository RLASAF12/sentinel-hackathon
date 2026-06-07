"""Risk gate — the human sign-off before any destructive action.

THIS IS THE DIFFERENTIATOR. Before any action with destructive=True, Sentinel
STOPS, shows the human a structured sign-off panel, WAITS for a decision, LOGS
it to an append-only audit trail, and only then allows execution.

    RiskGate(audit_log_path).request_approval(action) -> ApprovalResult

Fail-safe: anything other than an explicit "yes" is treated as NOT approved.
"""

import json
import logging
import os
import sys
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .models import ApprovalResult, ProposedAction

console = Console()
logger = logging.getLogger(__name__)


class RiskGate:
    """Presents a destructive action for human approval and logs the decision."""

    def __init__(self, audit_log_path: str = "sentinel-audit.log") -> None:
        self.audit_log_path = audit_log_path

    def request_approval(self, action: ProposedAction) -> ApprovalResult:
        """Request human approval for a proposed action.

        Loops on the "details" option so an operator can inspect evidence
        before deciding. Returns an ApprovalResult and writes an audit entry.
        """
        self._display_gate(action)
        while True:
            decision = self._wait_for_input()
            if decision in ("d", "details"):
                self._display_details(action)
                continue
            break

        result = self._process_decision(decision)
        self._log_decision(result, action)
        return result

    # --- display -------------------------------------------------------------

    def _display_gate(self, action: ProposedAction) -> None:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[bold red]Action[/]", action.description)
        table.add_row("[bold red]Risk Score[/]", f"{action.risk_score:.0%}")
        table.add_row("[bold red]Type[/]", action.action_type.upper())
        for i, ev in enumerate(action.evidence[:3]):
            table.add_row(f"[dim]Evidence {i + 1}[/]", ev)
        console.print(
            Panel(
                table,
                title="[bold red]SENTINEL RISK GATE[/bold red]",
                subtitle="[dim]Human approval required — AI cannot proceed alone[/dim]",
                border_style="red",
            )
        )

    def _display_details(self, action: ProposedAction) -> None:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[bold]Action type[/]", action.action_type)
        table.add_row("[bold]Destructive[/]", str(action.destructive))
        table.add_row("[bold]Risk score[/]", f"{action.risk_score:.2f}")
        for i, ev in enumerate(action.evidence):
            table.add_row(f"[dim]Evidence {i + 1}[/]", ev)
        console.print(Panel(table, title="[bold]Action Details[/bold]", border_style="blue"))

    # --- input ---------------------------------------------------------------

    def _wait_for_input(self) -> str:
        """Read the operator's decision.

        Interactive TTY: prompt and read. Non-interactive (piped/CI/recording):
        honor SENTINEL_AUTO_APPROVE=true (-> 'y') else fail-safe to 'n'.
        """
        if not sys.stdin.isatty():
            auto = os.getenv("SENTINEL_AUTO_APPROVE", "false").lower() in (
                "1",
                "true",
                "yes",
            )
            decision = "y" if auto else "n"
            console.print(
                f"\nApprove? [green](y)[/] / [red](n)[/] / [blue](d)[/]etails: "
                f"[dim]{decision} (non-interactive)[/dim]"
            )
            return decision

        console.print(
            "\nApprove? [green](y)[/] / [red](n)[/] / [blue](d)[/]etails: ", end=""
        )
        try:
            return input().strip().lower()
        except EOFError:
            return "n"  # fail-safe

    # --- decision + audit ----------------------------------------------------

    def _process_decision(self, decision: str) -> ApprovalResult:
        approved = decision in ("y", "yes")
        return ApprovalResult(
            approved=approved,
            approver="human-cli",
            notes=f"Decision: {decision!r}",
            timestamp=datetime.utcnow(),
        )

    def record_decision(
        self,
        action: ProposedAction,
        approved: bool,
        approver: str = "human-web",
        notes: str = "",
    ) -> ApprovalResult:
        """Record a programmatic approval decision (web UI / agent callback).

        Builds an ApprovalResult and writes the same audit entry the CLI gate
        does, so every approval path shares one append-only trail.
        """
        result = ApprovalResult(
            approved=approved,
            approver=approver,
            notes=notes or f"Decision: {'approve' if approved else 'deny'}",
            timestamp=datetime.utcnow(),
        )
        self._log_decision(result, action)
        return result

    def _log_decision(self, result: ApprovalResult, action: ProposedAction) -> None:
        entry = {
            "timestamp": result.timestamp.isoformat(),
            "action": action.action_type,
            "description": action.description,
            "destructive": action.destructive,
            "risk_score": action.risk_score,
            "approved": result.approved,
            "approver": result.approver,
            "notes": result.notes,
        }
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError as exc:  # auditing must not crash the pipeline
            logger.error("Failed to write audit log: %s", exc)
        logger.info("Gate decision logged: %s", entry)
