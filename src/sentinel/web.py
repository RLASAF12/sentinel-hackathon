"""Sentinel web UI (Fix 5) — the approval moment as a single page.

A dependency-free (stdlib http.server) web app whose centerpiece is the human
risk gate. It runs the current pipeline (detect -> diagnose -> propose), then
pauses on a destructive proposal and waits for the operator to Approve / Deny in
the browser. The decision is written to the same append-only audit log.

    python -m src.sentinel.web        # then open http://localhost:8080

This is adaptable to the ADK backend (src/sentinel/agent.py): swap the pipeline
call in `_scan()` for an agent run whose before_tool_callback surfaces the gate.
"""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .act import ActionOrchestrator
from .detect import RiskDetector
from .diagnose import GeminiDiagnoser
from .gate import RiskGate
from .main import DEMO_RISK_CONTEXT

try:
    from ..mcp.client import get_mcp_client
except ImportError:  # pragma: no cover
    from mcp.client import get_mcp_client  # type: ignore

logger = logging.getLogger(__name__)

# In-memory store of the pending proposal between /api/scan and /api/decision.
# Single-operator demo scope; a real deployment would key this per session.
_PENDING: dict = {}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Sentinel — the agent that knows when not to ship</title>
<style>
  :root { --bg:#0d1117; --card:#161b22; --line:#30363d; --red:#f85149;
          --green:#3fb950; --amber:#d29922; --text:#e6edf3; --dim:#8b949e; }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;
         background:var(--bg); color:var(--text); }
  header { padding:22px 28px; border-bottom:1px solid var(--line); }
  h1 { margin:0; font-size:20px; } .sub { color:var(--dim); font-size:13px; }
  main { max-width:760px; margin:0 auto; padding:28px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:10px;
          padding:18px 20px; margin:16px 0; }
  .gate { border-color:var(--red); box-shadow:0 0 0 1px var(--red) inset; }
  .row { display:flex; gap:10px; padding:3px 0; }
  .k { color:var(--dim); min-width:120px; } .v { color:var(--text); }
  .pill { display:inline-block; padding:2px 8px; border-radius:20px; font-size:12px; }
  .pill.red { background:rgba(248,81,73,.15); color:var(--red); }
  .pill.green { background:rgba(63,185,80,.15); color:var(--green); }
  button { font:inherit; padding:10px 18px; border-radius:8px; border:1px solid var(--line);
           background:#21262d; color:var(--text); cursor:pointer; }
  button.approve { border-color:var(--green); color:var(--green); }
  button.deny { border-color:var(--red); color:var(--red); }
  button:disabled { opacity:.4; cursor:default; }
  .signals .row .k { color:var(--amber); }
  .muted { color:var(--dim); } pre { white-space:pre-wrap; margin:0; }
  .hidden { display:none; }
  .banner { font-size:13px; padding:8px 12px; border-radius:8px; margin-top:8px; }
  .banner.held { background:rgba(210,153,34,.15); color:var(--amber); }
  .banner.exec { background:rgba(63,185,80,.15); color:var(--green); }
</style>
</head>
<body>
<header>
  <h1>🛡️ Sentinel <span class="muted">— the agent that knows when not to ship</span></h1>
  <div class="sub">Detect → Diagnose (Gemini) → Act (GitLab MCP) → <b>human GATE</b> → Execute</div>
</header>
<main>
  <button id="scan" onclick="scan()">▶ Review the pending deployment</button>

  <div id="detect" class="card hidden">
    <b>[DETECT]</b> <span id="score" class="muted"></span>
    <div class="signals" id="signals"></div>
  </div>

  <div id="diagnose" class="card hidden">
    <b>[DIAGNOSE] Gemini</b>
    <div class="row"><span class="k">Root cause</span><span class="v" id="root"></span></div>
    <div class="row"><span class="k">Severity</span><span class="v" id="sev"></span></div>
  </div>

  <div id="gate" class="card gate hidden">
    <b style="color:var(--red)">SENTINEL RISK GATE — human approval required</b>
    <div class="row"><span class="k">Action</span><span class="v" id="action"></span></div>
    <div class="row"><span class="k">Risk score</span><span class="v" id="risk"></span></div>
    <div class="row"><span class="k">Type</span><span class="v"><span class="pill red" id="dtype"></span></span></div>
    <div id="evidence"></div>
    <div style="margin-top:14px; display:flex; gap:10px;">
      <button class="approve" onclick="decide(true)">✓ Approve</button>
      <button class="deny" onclick="decide(false)">✕ Deny (hold)</button>
    </div>
    <div class="muted" style="margin-top:8px;font-size:12px;">AI cannot proceed alone. Every decision is logged.</div>
  </div>

  <div id="result" class="card hidden">
    <b>[EXECUTE]</b>
    <div id="resbanner" class="banner"></div>
    <div class="muted" style="margin-top:10px;font-size:12px;">Audit entry:</div>
    <pre id="audit" class="muted"></pre>
  </div>
</main>
<script>
async function scan() {
  document.getElementById('scan').disabled = true;
  const r = await fetch('/api/scan', {method:'POST'}); const d = await r.json();
  show('detect'); document.getElementById('score').textContent =
    'risk score ' + d.score.toFixed(2);
  document.getElementById('signals').innerHTML = d.signals.map(s =>
    `<div class="row"><span class="k">${s.type}</span><span class="v">${s.evidence} <span class="muted">(sev ${s.severity.toFixed(2)})</span></span></div>`).join('');
  show('diagnose');
  document.getElementById('root').textContent = d.root_cause;
  document.getElementById('sev').textContent = d.severity.toUpperCase();
  if (d.destructive) {
    show('gate');
    document.getElementById('action').textContent = d.description;
    document.getElementById('risk').textContent = (d.risk_score*100).toFixed(0)+'%';
    document.getElementById('dtype').textContent = d.action_type.toUpperCase()+' · DESTRUCTIVE';
    document.getElementById('evidence').innerHTML = d.evidence.map((e,i) =>
      `<div class="row"><span class="k">Evidence ${i+1}</span><span class="v">${e}</span></div>`).join('');
  } else {
    finish({approved:true, success:true, action_taken:d.description, audit:{}});
  }
}
async function decide(approve) {
  document.querySelectorAll('#gate button').forEach(b => b.disabled = true);
  const r = await fetch('/api/decision', {method:'POST',
    headers:{'Content-Type':'application/json'}, body:JSON.stringify({approve})});
  finish(await r.json());
}
function finish(d) {
  show('result');
  const b = document.getElementById('resbanner');
  b.className = 'banner ' + (d.success ? 'exec' : 'held');
  b.textContent = d.action_taken;
  document.getElementById('audit').textContent = JSON.stringify(d.audit, null, 2);
}
function show(id){ document.getElementById(id).classList.remove('hidden'); }
</script>
</body>
</html>"""


def _scan() -> dict:
    """Run detect -> diagnose -> propose and stash the proposal for /api/decision."""
    context = DEMO_RISK_CONTEXT if _demo() else {}
    report = RiskDetector().scan(context)
    diagnoser = GeminiDiagnoser(api_key=os.getenv("GEMINI_API_KEY", ""))
    diagnosis = diagnoser.diagnose(report, diff=context.get("diff_summary", ""))
    action = ActionOrchestrator().propose_action(diagnosis)

    _PENDING["action"] = action
    return {
        "score": report.score,
        "signals": [
            {"type": s.type, "severity": s.severity, "evidence": s.evidence}
            for s in report.signals
        ],
        "root_cause": diagnosis.root_cause,
        "severity": diagnosis.severity.value,
        "action_type": action.action_type,
        "description": action.description,
        "destructive": action.destructive,
        "risk_score": action.risk_score,
        "evidence": action.evidence,
    }


async def _decide(approve: bool) -> dict:
    """Apply the operator's decision to the pending action; log + execute."""
    action = _PENDING.get("action")
    if action is None:
        return {"success": False, "action_taken": "No pending action.", "audit": {}}
    gate = RiskGate()
    approval = gate.record_decision(action, approved=approve, approver="human-web")
    execution = await ActionOrchestrator(mcp_client=get_mcp_client()).execute(action, approval)
    return {
        "approved": approval.approved,
        "success": execution.success,
        "action_taken": execution.action_taken,
        "audit": execution.audit_log,
    }


def _demo() -> bool:
    return os.getenv("SENTINEL_DEMO", "true").lower() in ("1", "true", "yes")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: dict) -> None:
        self._send(code, json.dumps(obj).encode(), "application/json")

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.encode(), "text/html; charset=utf-8")
        elif self.path == "/health":
            self._json(200, {"status": "ok", "service": "sentinel-web"})
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):  # noqa: N802
        import asyncio

        if self.path == "/api/scan":
            self._json(200, _scan())
        elif self.path == "/api/decision":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            result = asyncio.run(_decide(bool(payload.get("approve", False))))
            self._json(200, result)
        else:
            self._send(404, b"not found", "text/plain")

    def log_message(self, *args):  # quiet
        return


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    os.environ.setdefault("SENTINEL_DEMO", "true")
    port = int(os.getenv("PORT", "8080"))
    print(f"Sentinel web UI on http://localhost:{port}  (demo={_demo()})")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
