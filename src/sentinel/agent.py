"""Sentinel as a Google ADK / Agent Builder agent (Fixes 2 & 3).

This is the qualification-stack rebuild: the agent's brain is a Google ADK
``LlmAgent`` running **Gemini 3**, its tools are the **real GitLab MCP server**,
and every destructive tool call is intercepted by the human risk-gate via a
``before_tool_callback`` — preserving Sentinel's differentiator *inside* the
agent loop, with the same append-only audit trail.

────────────────────────────────────────────────────────────────────────────
STATUS: DRAFT written against the verified ADK API (June 2026). It is NOT run
in the build container (no google-adk, no Gemini 3 key, no GitLab token). The
cloud-access session must:
  1. `pip install "google-adk>=1.14.0"` and confirm the imports below.
  2. Confirm the live Gemini 3 model id (see GEMINI_3_MODEL note).
  3. Provide GITLAB_TOKEN + the GitLab MCP server command, then run + verify.
See WINNING-BUILD-PROMPT.md (Fixes 2–4) for acceptance criteria.

API verified against (June 2026):
  - McpToolset(connection_params=StdioConnectionParams(server_params=...),
        tool_filter=[...], require_confirmation=...)
    google/adk-python src/google/adk/tools/mcp_tool/mcp_toolset.py
  - before_tool_callback: Callable[[BaseTool, dict, ToolContext], Optional[dict]]
    return a dict -> skip the tool (our HOLD); return None -> proceed (approved)
    google/adk-python src/google/adk/agents/llm_agent.py
────────────────────────────────────────────────────────────────────────────
"""

import logging
import os
from typing import Any, Optional

from .detect import RiskDetector
from .gate import RiskGate
from .models import ProposedAction

logger = logging.getLogger(__name__)

# Gemini 3 model id. The brief requires Gemini 3. As of 2026, gemini-3-pro-preview
# was superseded by gemini-3.1-pro-preview on Vertex AI — the cloud session MUST
# confirm the currently-served id. Override with SENTINEL_MODEL.
GEMINI_3_MODEL = os.getenv("SENTINEL_MODEL", "gemini-3-pro-preview")

# A tool call is destructive (and therefore gated) when its name contains any of
# these keywords. Keyword matching is deliberate: exact GitLab MCP tool names
# must be confirmed against the live server, but "cancel/revert/rollback/delete"
# reliably identify the dangerous ones.
DESTRUCTIVE_KEYWORDS = ("cancel", "delete", "revert", "rollback", "remove", "drop")

AGENT_INSTRUCTION = """\
You are Sentinel, a deployment-safety agent guarding a GitLab project.

Your mandate:
1. Read the merge request and pipeline state using the GitLab MCP tools.
2. Assess deployment blast radius using the risk_scan tool.
3. Reason about whether any action is warranted.
4. You MAY freely use read-only tools (diffs, pipeline status, comments).
5. You MUST NEVER execute a destructive action (cancel/revert/rollback a
   pipeline or deployment) on your own. Propose it; a human approves it.

When you believe a destructive action is needed, call the relevant tool with a
clear, specific argument set and a one-line justification. The system will pause
and ask a human to approve before anything runs. If the human declines, respect
the HOLD and explain the safer alternative.
"""


def is_destructive(tool_name: str) -> bool:
    """True if a tool name denotes a destructive (gate-requiring) action."""
    name = (tool_name or "").lower()
    return any(kw in name for kw in DESTRUCTIVE_KEYWORDS)


def make_gate_callback(gate: Optional[RiskGate] = None):
    """Build an ADK ``before_tool_callback`` that routes destructive tool calls
    through the human risk-gate.

    Returns a callable ``(tool, args, tool_context) -> Optional[dict]``:
      - non-destructive tool  -> returns None (ADK runs the tool normally)
      - destructive + approved -> returns None (ADK runs the tool)
      - destructive + denied   -> returns a dict (ADK skips the tool: HOLD)

    The dict short-circuits execution per the ADK contract, so a denied action
    never reaches GitLab. Every decision is written to the audit log by the gate.
    """
    gate = gate or RiskGate()

    def before_tool_callback(tool: Any, args: dict, tool_context: Any) -> Optional[dict]:
        tool_name = getattr(tool, "name", str(tool))
        if not is_destructive(tool_name):
            return None  # read-only / safe tool: proceed

        action = ProposedAction(
            action_type=tool_name,
            destructive=True,
            description=f"{tool_name}({_summarize_args(args)})",
            evidence=[f"Agent requested destructive tool '{tool_name}'", f"args={args}"],
            risk_score=float(args.get("risk_score", 0.9)) if isinstance(args, dict) else 0.9,
        )

        approval = gate.request_approval(action)
        if approval.approved:
            logger.info("Gate APPROVED destructive tool %s; proceeding.", tool_name)
            return None  # let ADK execute the real tool

        logger.info("Gate DENIED destructive tool %s; holding.", tool_name)
        return {
            "status": "held",
            "tool": tool_name,
            "reason": "Human approval denied at the Sentinel risk gate.",
            "approver": approval.approver,
        }

    return before_tool_callback


def _summarize_args(args: Any) -> str:
    if not isinstance(args, dict):
        return str(args)
    return ", ".join(f"{k}={v}" for k, v in list(args.items())[:4])


def risk_scan(context: dict) -> dict:
    """ADK FunctionTool: scan a deployment context for risk signals.

    Wraps RiskDetector so the agent can call it as a tool and reason over the
    structured result.
    """
    report = RiskDetector().scan(context or {})
    return {
        "score": report.score,
        "signals": [
            {"type": s.type, "severity": s.severity, "evidence": s.evidence}
            for s in report.signals
        ],
    }


def build_gitlab_mcp_toolset():
    """Construct the real GitLab MCP toolset (lazy ADK import).

    Requires google-adk installed and GITLAB_TOKEN set. The exact GitLab MCP
    server command/tool names must be confirmed in the cloud session.
    """
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@gitlab/mcp-server"],
                env={
                    "GITLAB_TOKEN": os.getenv("GITLAB_TOKEN", ""),
                    "GITLAB_URL": os.getenv("GITLAB_URL", "https://gitlab.com"),
                },
            )
        ),
        # Expose read tools + the destructive ones we gate. Confirm names live.
        tool_filter=[
            "get_merge_request_diff",
            "get_merge_request",
            "get_pipeline",
            "list_pipeline_jobs",
            "create_merge_request_note",
            "cancel_pipeline",
        ],
    )


def build_agent(gate: Optional[RiskGate] = None):
    """Build the Sentinel ADK LlmAgent (lazy ADK import).

    Tools: risk_scan (FunctionTool) + GitLab MCP toolset. Destructive tool calls
    are intercepted by the gate via before_tool_callback.
    """
    from google.adk.agents import LlmAgent
    from google.adk.tools import FunctionTool

    return LlmAgent(
        name="sentinel",
        model=GEMINI_3_MODEL,
        instruction=AGENT_INSTRUCTION,
        tools=[FunctionTool(risk_scan), build_gitlab_mcp_toolset()],
        before_tool_callback=make_gate_callback(gate),
    )


async def run_agent(prompt: str, *, user_id: str = "operator", session_id: str = "s1") -> str:
    """Run the agent once and return its final text (lazy ADK import).

    Minimal Runner + in-memory session loop. The cloud session verifies the
    event/response API shape against the installed google-adk version.
    """
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    agent = build_agent()
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="sentinel", user_id=user_id, session_id=session_id
    )
    runner = Runner(agent=agent, app_name="sentinel", session_service=session_service)

    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    final_text = ""
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or ""
    return final_text
