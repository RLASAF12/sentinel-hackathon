# Tech Stack — Confirmed (W1)

Runtime target: **Python 3.12**

## Dependencies

| Package | Version constraint | Role | Notes |
|---------|-------------------|------|-------|
| `google-generativeai` | `>=0.8.0` | Gemini 2.0 Flash diagnosis | Model id: `gemini-2.0-flash`. Needs `GEMINI_API_KEY`. |
| `google-adk` | `>=1.0.0` | Agent Development Kit | Multi-agent orchestration. |
| `mcp` | `>=1.0.0` | Model Context Protocol client | Official SDK; wraps GitLab MCP. |
| `rich` | `>=13.0.0` | Demo UI / gate panel | The gate "money shot" is rendered with Rich. |
| `python-dotenv` | `>=1.0.0` | Load `.env` | Local dev convenience. |
| `pydantic` | `>=2.0.0` | Validation (optional) | Dataclasses are primary; pydantic available if needed. |
| `pytest` | `>=8.0.0` | Tests | `tests/test_gate.py`. |
| `pytest-asyncio` | `>=0.23.0` | Async tests | `main.run_sentinel` is async. |

## Partner MCP

- **Primary:** GitLab MCP server (official) — rollback, alert, MR context.
- **Fallback:** GitHub MCP — only if GitLab MCP is unavailable.
- **Demo:** `SENTINEL_DEMO=true` routes to a mock MCP client so the pipeline
  runs without live credentials.

## Demo UI

- **Chosen:** `rich` (terminal). The demo is a terminal screen recording
  (see `docs/demo-script.md`), so Rich beats Streamlit for the gate reveal.
- Streamlit deferred — not needed for the 3-minute narrative.

## Cloud

- **Google Cloud Run** for deployment (W3). Dockerfile owned by builder.
- Gemini via API key for the hackathon; Vertex AI path noted as future work.

## Verification Notes

- Version constraints come from `agents/builder.md` requirements.txt.
- Heavy SDK imports (google-generativeai, mcp) are kept out of module
  top-level in stubs so the skeleton imports cleanly before deps are installed.
- Install + import verification of the full stack happens in W2/W3 once the
  real implementations land.
