"""Detect phase — scan a PR/commit/deploy context for risk signals.

W1 stub. Real scanning logic lands in W2 (builder).
Interface contract: RiskDetector.scan(context: dict) -> RiskReport
"""

import logging

from .models import RiskReport

logger = logging.getLogger(__name__)


class RiskDetector:
    """Scans a deployment context and emits a RiskReport.

    Stub: returns an empty, zero-score report. Implemented in W2.
    """

    def scan(self, context: dict) -> RiskReport:
        """Scan the given context and return a RiskReport.

        Args:
            context: deployment metadata (files changed, coverage delta, etc.).

        Returns:
            A RiskReport with detected signals and an aggregate score.
        """
        logger.info("RiskDetector.scan stub called; W2 will implement.")
        return RiskReport(signals=[], score=0.0, context=context)
