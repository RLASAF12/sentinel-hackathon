"""Sentinel entry point — wires the pipeline and supports --demo.

W1 stub. The full async pipeline (detect -> diagnose -> act -> gate ->
execute) lands in W2/W3.

Interface contract:
    async def run_sentinel(context: dict) -> SentinelResult
"""

import argparse
import asyncio
import logging
import os

from .act import ActionOrchestrator
from .detect import RiskDetector
from .diagnose import GeminiDiagnoser
from .gate import RiskGate
from .models import SentinelResult

logger = logging.getLogger(__name__)


def _demo_mode() -> bool:
    """True when SENTINEL_DEMO env var enables mock clients everywhere."""
    return os.getenv("SENTINEL_DEMO", "").lower() in ("1", "true", "yes")


async def run_sentinel(context: dict) -> SentinelResult:
    """Run one full Sentinel pass over a deployment context.

    W1 stub: walks the pipeline with stub components and returns a
    SentinelResult. Real wiring (Gemini, MCP, interactive gate) lands in W2/W3.

    Args:
        context: deployment metadata to evaluate.

    Returns:
        A SentinelResult capturing every phase of the run.
    """
    detector = RiskDetector()
    diagnoser = GeminiDiagnoser(api_key=os.getenv("GEMINI_API_KEY", ""))
    gate = RiskGate()
    orchestrator = ActionOrchestrator(mcp_client=None)

    report = detector.scan(context)
    diagnosis = diagnoser.diagnose(report, diff=context.get("diff_summary", ""))
    action = orchestrator.propose_action(diagnosis)
    approval = gate.request_approval(action)
    execution = orchestrator.execute(action, approval)

    return SentinelResult(
        report=report,
        diagnosis=diagnosis,
        action=action,
        approval=approval,
        execution=execution,
    )


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sentinel — the agent that knows when not to ship."
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run with mock clients (no API keys)."
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.demo:
        os.environ["SENTINEL_DEMO"] = "true"

    logger.info("SENTINEL - Risk Guardian for CI/CD (W1 skeleton)")
    logger.info("Demo mode: %s", _demo_mode())
    logger.info("Pipeline stubs wired. Implementation lands in W2.")

    asyncio.run(run_sentinel(context={}))


if __name__ == "__main__":
    main()
