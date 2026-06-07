"""Sentinel entry point — wires the full pipeline.

    detect -> diagnose -> act(propose) -> GATE -> execute

Modes:
    --demo    run with mock clients over a high-risk scenario (no API keys)
    --serve   run a minimal HTTP server exposing /health (Cloud Run)

    async def run_sentinel(context: dict) -> SentinelResult
"""

import argparse
import asyncio
import logging
import os

from rich.console import Console

from .act import ActionOrchestrator
from .detect import RiskDetector
from .diagnose import GeminiDiagnoser
from .gate import RiskGate
from .models import SentinelResult

try:  # works whether imported as src.sentinel.* or sentinel.*
    from ..mcp.client import get_mcp_client
except ImportError:  # pragma: no cover - fallback for top-level layout
    from mcp.client import get_mcp_client  # type: ignore

logger = logging.getLogger(__name__)
console = Console()

# Risk score below which Sentinel clears the deploy without diagnosis.
RISK_THRESHOLD = 0.3

# Demo scenario used by the offline (SENTINEL_DEMO) path.
DEMO_RISK_CONTEXT = {
    "files_changed": 47,
    "test_coverage_delta": -12.3,
    "config_files_modified": ["k8s/prod.yaml", ".env.production"],
    "diff_summary": "Large diff: 47 files, infrastructure changes detected",
    "target": "production",
    "pipeline_id": "12345",
    "project_id": "demo-project",
    "mr_iid": 1847,
}


def _demo_mode() -> bool:
    return os.getenv("SENTINEL_DEMO", "").lower() in ("1", "true", "yes")


async def run_sentinel(context: dict) -> SentinelResult:
    """Run one full Sentinel pass over a deployment context.

    Returns a SentinelResult capturing every phase. The gate is consulted
    only for destructive proposals; nothing destructive runs without approval.
    """
    detector = RiskDetector()
    diagnoser = GeminiDiagnoser(api_key=os.getenv("GEMINI_API_KEY", ""))
    gate = RiskGate()
    mcp_client = get_mcp_client()
    orchestrator = ActionOrchestrator(mcp_client=mcp_client)

    # DETECT
    console.print("\n[bold cyan][DETECT][/] Scanning merge request...", highlight=False)
    report = detector.scan(context)
    for s in report.signals:
        console.print(
            f"  Signal: {s.type:<16} sev {s.severity:.2f}  [dim]{s.evidence}[/]"
        )
    console.print(f"  Risk score: [bold]{report.score:.2f}[/]")

    # Pull the diff via MCP (demo returns a canned diff).
    diff = await mcp_client.get_diff(
        context.get("project_id", "demo-project"), context.get("mr_iid", 0)
    )

    # DIAGNOSE
    console.print("\n[bold cyan][DIAGNOSE][/] Reasoning with Gemini...")
    diagnosis = diagnoser.diagnose(report, diff)
    console.print(f"  Root cause: {diagnosis.root_cause}")
    console.print(f"  Severity:   {diagnosis.severity.value.upper()}")
    console.print(f"  Recommended: {diagnosis.recommended_action}")

    # ACT (propose)
    console.print("\n[bold cyan][ACT][/] Proposing action...")
    action = orchestrator.propose_action(diagnosis)
    console.print(
        f"  Proposed: {action.description}  "
        f"[{'red' if action.destructive else 'green'}]"
        f"{'DESTRUCTIVE' if action.destructive else 'non-destructive'}[/]"
    )

    # GATE (only for destructive actions) + EXECUTE
    approval = None
    if action.destructive:
        console.print()
        approval = gate.request_approval(action)

    execution = await orchestrator.execute(action, approval)
    console.print(
        f"\n[bold cyan][EXECUTE][/] "
        f"[{'green' if execution.success else 'yellow'}]{execution.action_taken}[/]"
    )

    from .models import ApprovalResult

    return SentinelResult(
        report=report,
        diagnosis=diagnosis,
        action=action,
        approval=approval
        or ApprovalResult(approved=False, approver="n/a", notes="no gate needed"),
        execution=execution,
    )


def serve() -> None:
    """Minimal HTTP server exposing /health for Cloud Run."""
    from http.server import BaseHTTPRequestHandler, HTTPServer

    port = int(os.getenv("PORT", "8080"))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (stdlib API)
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok","service":"sentinel"}')
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *args):  # silence default logging
            return

    logger.info("Sentinel serving on :%d (GET /health)", port)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sentinel — the agent that knows when not to ship."
    )
    parser.add_argument("--demo", action="store_true", help="Run with mock clients.")
    parser.add_argument("--serve", action="store_true", help="Run the /health server.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    if args.serve:
        serve()
        return

    if args.demo:
        os.environ["SENTINEL_DEMO"] = "true"

    console.print("[bold]SENTINEL[/] - Risk Guardian for CI/CD")
    console.print("[dim]Google Cloud Rapid Agent Hackathon[/]")
    console.print(f"[dim]Demo mode: {_demo_mode()}[/]")

    context = DEMO_RISK_CONTEXT if _demo_mode() else {}
    asyncio.run(run_sentinel(context))


if __name__ == "__main__":
    main()
