"""Diagnose phase — root-cause analysis via Gemini.

GeminiDiagnoser(api_key).diagnose(report, diff) -> Diagnosis

This is the lightweight CLI/offline diagnoser (google-generativeai), imported
lazily. The primary, hosted path reasons with Gemini 3 on Vertex AI (see
agent.py / live.py). If the SDK or an API key is missing, or SENTINEL_DEMO=true,
this falls back to a deterministic heuristic so the pipeline always runs.
"""

import json
import logging
import os
from typing import List

from .models import Diagnosis, RiskReport, Severity

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("SENTINEL_DIAGNOSE_MODEL", "gemini-2.0-flash")

PROMPT_TEMPLATE = """You are Sentinel, a deployment-risk diagnostician.

Risk signals detected (type, severity 0-1, evidence):
{signals}

Aggregate risk score: {score:.2f}

Code/config diff (truncated):
{diff}

Identify the single most likely root cause of deployment risk and recommend
ONE action. Respond with ONLY a JSON object, no prose, in this exact shape:
{{"root_cause": "<one sentence>",
  "severity": "low|medium|high|critical",
  "recommended_action": "rollback|hold|alert|patch",
  "alternatives": ["<alt 1>", "<alt 2>"],
  "confidence": <float 0-1>}}
"""


class GeminiDiagnoser:
    """Turns a RiskReport into a Diagnosis using Gemini."""

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.demo_mode = os.getenv("SENTINEL_DEMO", "false").lower() in (
            "1",
            "true",
            "yes",
        )

    def diagnose(self, report: RiskReport, diff: str) -> Diagnosis:
        """Produce a root-cause Diagnosis for the given risk report.

        Falls back to a deterministic heuristic when Gemini is unavailable so
        the pipeline never crashes during a demo.
        """
        if self.demo_mode or not self.api_key:
            reason = "demo mode" if self.demo_mode else "no GEMINI_API_KEY"
            logger.info("Diagnose: using heuristic fallback (%s).", reason)
            return self._heuristic(report)

        try:
            return self._gemini(report, diff)
        except Exception as exc:  # never let the demo crash on an API error
            logger.warning("Diagnose: Gemini call failed (%s); using heuristic.", exc)
            return self._heuristic(report)

    # --- Gemini path ---------------------------------------------------------

    def _gemini(self, report: RiskReport, diff: str) -> Diagnosis:
        import google.generativeai as genai  # lazy import

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = PROMPT_TEMPLATE.format(
            signals=self._format_signals(report),
            score=report.score,
            diff=(diff or "")[:4000],
        )
        response = model.generate_content(prompt)
        return self._parse(response.text, report)

    @staticmethod
    def _parse(text: str, report: RiskReport) -> Diagnosis:
        """Parse Gemini's JSON response, tolerating code fences."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned[cleaned.find("{") :]
        data = json.loads(cleaned[cleaned.find("{") : cleaned.rfind("}") + 1])
        return Diagnosis(
            root_cause=data["root_cause"],
            severity=Severity(data.get("severity", "medium")),
            recommended_action=data.get("recommended_action", "hold"),
            alternatives=list(data.get("alternatives", [])),
            confidence=float(data.get("confidence", 0.7)),
        )

    # --- Heuristic fallback --------------------------------------------------

    def _heuristic(self, report: RiskReport) -> Diagnosis:
        """Deterministic diagnosis derived from the risk signals."""
        severity = self._severity_from_score(report.score)
        types = {s.type for s in report.signals}

        if {"CONFIG_MODIFIED", "FILES_CHANGED"} <= types:
            root = (
                "Large deployment scope combined with infrastructure/config "
                "changes increases blast radius on production."
            )
            action = "rollback" if report.score >= 0.7 else "hold"
        elif "BREAKING_CHANGE" in types:
            root = "Diff contains a breaking change likely to disrupt consumers."
            action = "hold"
        elif "COVERAGE_DELTA" in types:
            root = "Test coverage regressed, lowering confidence in this change."
            action = "hold"
        elif report.signals:
            root = "Elevated deployment risk from the detected signals."
            action = "alert"
        else:
            root = "No significant risk signals detected."
            action = "alert"

        return Diagnosis(
            root_cause=root,
            severity=severity,
            recommended_action=action,
            alternatives=[
                "Delay 2h and notify the on-call team",
                "Restore test coverage before deploying",
            ],
            confidence=0.78 if report.signals else 0.5,
        )

    @staticmethod
    def _severity_from_score(score: float) -> Severity:
        if score >= 0.85:
            return Severity.CRITICAL
        if score >= 0.6:
            return Severity.HIGH
        if score >= 0.3:
            return Severity.MEDIUM
        return Severity.LOW

    @staticmethod
    def _format_signals(report: RiskReport) -> str:
        lines: List[str] = [
            f"- {s.type} (sev {s.severity:.2f}): {s.evidence}" for s in report.signals
        ]
        return "\n".join(lines) if lines else "- (none)"
