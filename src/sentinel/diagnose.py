"""Diagnose phase — root-cause analysis via Gemini 2.0 Flash.

W1 stub. Real Gemini call lands in W2 (builder).
Heavy SDK (google-generativeai) is imported lazily inside methods so the
skeleton imports cleanly before dependencies are installed.

Interface contract:
    GeminiDiagnoser(api_key: str)
    GeminiDiagnoser.diagnose(report: RiskReport, diff: str) -> Diagnosis
"""

import logging

from .models import Diagnosis, RiskReport, Severity

logger = logging.getLogger(__name__)


class GeminiDiagnoser:
    """Wraps Gemini 2.0 Flash to turn a RiskReport into a Diagnosis.

    Stub: returns a placeholder Diagnosis. Implemented in W2.
    """

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def diagnose(self, report: RiskReport, diff: str) -> Diagnosis:
        """Produce a root-cause Diagnosis for the given risk report.

        Args:
            report: the RiskReport from the detect phase.
            diff: the code/config diff text for context.

        Returns:
            A Diagnosis with root cause, severity, and recommended action.
        """
        logger.info("GeminiDiagnoser.diagnose stub called; W2 will implement.")
        return Diagnosis(
            root_cause="(stub) diagnosis pending W2 implementation",
            severity=Severity.LOW,
            recommended_action="hold",
            alternatives=[],
            confidence=0.0,
        )
