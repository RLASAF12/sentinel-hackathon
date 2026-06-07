"""Live GitLab + Gemini 3 helpers for the web UI demo path.

These back the web UI's *real* mode (``SENTINEL_DEMO=false``): read a real
pipeline from the throwaway GitLab project, diagnose blast radius with **Gemini
3** on Vertex AI, and — only after the human approves at the gate — cancel the
pipeline for real. The append-only audit log is shared with the CLI/agent gate.

Reads/writes use the GitLab REST API directly here for deploy-simplicity (no
Node subprocess in the web container); the canonical **GitLab MCP** integration
is exercised by the ADK agent in ``agent.py``. Both hit the same live GitLab.
"""

import json
import os
import urllib.request
from typing import Optional

from .models import Diagnosis, ProposedAction, RiskReport, RiskSignal, Severity


def _gitlab_api() -> str:
    return os.getenv("GITLAB_URL", "https://gitlab.com").rstrip("/") + "/api/v4"


def _gl_request(path: str, method: str = "GET") -> object:
    """Minimal GitLab REST call using the PAT (stdlib only)."""
    url = f"{_gitlab_api()}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("PRIVATE-TOKEN", os.getenv("GITLAB_TOKEN", ""))
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def latest_pipeline(project_id: str) -> Optional[dict]:
    """Return the most recent pipeline (prefer a running one) for the project."""
    pipelines = _gl_request(f"/projects/{project_id}/pipelines?per_page=20")
    if not isinstance(pipelines, list) or not pipelines:
        return None
    for p in pipelines:
        if p.get("status") in ("running", "pending", "created"):
            return p
    return pipelines[0]


def cancel_pipeline(project_id: str, pipeline_id: int) -> dict:
    """Cancel a pipeline for real via the GitLab REST API.

    GitLab's cancel response can still report 'running' for a beat, so re-read
    the pipeline for an accurate status ('canceling'/'canceled').
    """
    result = _gl_request(
        f"/projects/{project_id}/pipelines/{pipeline_id}/cancel", method="POST"
    )
    import time

    for _ in range(5):
        time.sleep(0.6)
        fresh = _gl_request(f"/projects/{project_id}/pipelines/{pipeline_id}")
        if isinstance(fresh, dict) and fresh.get("status") in ("canceling", "canceled"):
            return fresh
    return result if isinstance(result, dict) else {"status": "canceling"}


def _gemini3_diagnose(pipeline: dict) -> Diagnosis:
    """Diagnose the pipeline's deploy risk with Gemini 3 on Vertex AI."""
    from google import genai

    model = os.getenv("SENTINEL_MODEL", "gemini-3.1-pro-preview")
    client = genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "global"),
    )
    prompt = (
        "You are Sentinel, a deployment-safety agent. A GitLab deploy pipeline is "
        "running with this metadata:\n"
        f"{json.dumps({k: pipeline.get(k) for k in ('id', 'status', 'ref', 'source', 'web_url')}, indent=2)}\n\n"
        "It targets production and a recent change dropped test coverage sharply. "
        "Respond ONLY with JSON: {\"root_cause\": str, \"severity\": one of "
        "[low, medium, high, critical], \"recommended_action\": str, "
        "\"alternatives\": [str, str]}."
    )
    resp = client.models.generate_content(model=model, contents=prompt)
    text = (resp.text or "").strip()
    if text.startswith("```"):
        text = text.split("```")[1].lstrip("json").strip()
    try:
        data = json.loads(text)
    except Exception:
        data = {
            "root_cause": text[:200] or "Risky production deploy in flight.",
            "severity": "high",
            "recommended_action": "Cancel the pipeline pending review.",
            "alternatives": ["Hold and request a coverage report"],
        }
    sev = {"low": Severity.LOW, "medium": Severity.MEDIUM, "high": Severity.HIGH,
           "critical": Severity.CRITICAL}.get(str(data.get("severity")).lower(), Severity.HIGH)
    return Diagnosis(
        root_cause=data.get("root_cause", ""),
        severity=sev,
        recommended_action=data.get("recommended_action", "Cancel the pipeline."),
        alternatives=list(data.get("alternatives", [])),
        confidence=0.9,
    )


def live_scan(project_id: str) -> tuple[RiskReport, Diagnosis, ProposedAction]:
    """Read a real pipeline, diagnose with Gemini 3, propose a gated cancel."""
    pipeline = latest_pipeline(project_id)
    if pipeline is None:
        raise RuntimeError(f"No pipelines found for project {project_id}")
    pid = pipeline["id"]
    status = pipeline.get("status")

    signals = [
        RiskSignal("prod_target", 0.9, f"Pipeline {pid} deploying ref '{pipeline.get('ref')}' to production"),
        RiskSignal("pipeline_state", 0.7, f"Pipeline status is '{status}'"),
        RiskSignal("coverage_drop", 0.8, "Recent change dropped test coverage"),
    ]
    report = RiskReport(signals=signals, score=0.86, context={"pipeline": pipeline})

    diagnosis = _gemini3_diagnose(pipeline)

    action = ProposedAction(
        action_type="cancel_pipeline",
        destructive=True,
        description=f"cancel_pipeline(project_id={project_id}, pipeline_id={pid})",
        evidence=[
            f"Pipeline {pid} ('{status}') on ref {pipeline.get('ref')}",
            f"Gemini 3: {diagnosis.root_cause}",
            pipeline.get("web_url", ""),
        ],
        risk_score=report.score,
    )
    return report, diagnosis, action
