"""Detect phase — scan a PR/commit/deploy context for risk signals.

RiskDetector.scan(context: dict) -> RiskReport

The detector is deterministic and dependency-free: it inspects deployment
metadata (files changed, coverage delta, config files touched, target env,
breaking-change hints) and emits weighted RiskSignals plus an aggregate score.
"""

import logging
from typing import List

from .models import RiskReport, RiskSignal

logger = logging.getLogger(__name__)

# Tunable thresholds. Kept module-level so they are easy to demo/tweak.
FILES_CHANGED_THRESHOLD = 20
COVERAGE_DROP_THRESHOLD = -5.0  # percentage points
CONFIG_FILE_HINTS = (".env", "k8s/", "values.yaml", "terraform", "dockerfile", ".tf")
BREAKING_CHANGE_HINTS = (
    "breaking change",
    "drop table",
    "remove endpoint",
    "delete column",
    "alter table",
)


class RiskDetector:
    """Scans a deployment context and emits a RiskReport."""

    def scan(self, context: dict) -> RiskReport:
        """Scan the given context and return a RiskReport.

        Args:
            context: deployment metadata. Recognized keys:
                files_changed (int), test_coverage_delta (float),
                config_files_modified (list[str]), target (str),
                diff_summary (str), mr_iid (int), pipeline_id (str).

        Returns:
            A RiskReport with detected signals and an aggregate 0.0-1.0 score.
        """
        signals: List[RiskSignal] = []

        files_changed = int(context.get("files_changed", 0) or 0)
        if files_changed > FILES_CHANGED_THRESHOLD:
            # Scale severity with how far past the threshold we are (cap at 1.0).
            sev = min(1.0, 0.5 + (files_changed - FILES_CHANGED_THRESHOLD) / 60.0)
            signals.append(
                RiskSignal(
                    type="FILES_CHANGED",
                    severity=round(sev, 2),
                    evidence=f"{files_changed} files changed (threshold {FILES_CHANGED_THRESHOLD})",
                )
            )

        coverage_delta = float(context.get("test_coverage_delta", 0.0) or 0.0)
        if coverage_delta <= COVERAGE_DROP_THRESHOLD:
            sev = min(1.0, abs(coverage_delta) / 20.0)
            signals.append(
                RiskSignal(
                    type="COVERAGE_DELTA",
                    severity=round(max(sev, 0.4), 2),
                    evidence=f"Test coverage changed {coverage_delta:.1f}%",
                )
            )

        for cfg in context.get("config_files_modified", []) or []:
            if any(hint in cfg.lower() for hint in CONFIG_FILE_HINTS):
                signals.append(
                    RiskSignal(
                        type="CONFIG_MODIFIED",
                        severity=0.8,
                        evidence=f"Sensitive config modified: {cfg}",
                    )
                )

        target = str(context.get("target", "")).lower()
        if target in ("production", "prod"):
            signals.append(
                RiskSignal(
                    type="PROD_DEPLOY",
                    severity=0.6,
                    evidence="Deployment targets production (not staging)",
                )
            )

        diff = str(context.get("diff_summary", "")).lower()
        for hint in BREAKING_CHANGE_HINTS:
            if hint in diff:
                signals.append(
                    RiskSignal(
                        type="BREAKING_CHANGE",
                        severity=0.9,
                        evidence=f"Breaking-change pattern in diff: '{hint}'",
                    )
                )
                break

        score = self._aggregate(signals)
        logger.info(
            "Detect: %d signal(s), risk score %.2f", len(signals), score
        )
        return RiskReport(signals=signals, score=score, context=context)

    @staticmethod
    def _aggregate(signals: List[RiskSignal]) -> float:
        """Combine signal severities into a 0.0-1.0 score.

        Uses a soft-OR (probabilistic union) so multiple moderate signals
        compound toward HIGH without ever exceeding 1.0.
        """
        if not signals:
            return 0.0
        product = 1.0
        for s in signals:
            product *= 1.0 - max(0.0, min(1.0, s.severity))
        return round(1.0 - product, 2)
