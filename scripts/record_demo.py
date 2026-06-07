"""Record the Sentinel demo as a video (Playwright) against the live stack.

Drives the live web UI (SENTINEL_DEMO=false) with on-page captions baked in at
each beat, recording a real run: hero -> Gemini 3 reasoning -> the gate ->
Deny (HOLD) -> Approve (real GitLab cancel) -> audit. Outputs a .webm; compose
to mp4 with scripts/compose_demo.sh.
"""

import glob
import os
import time
from playwright.sync_api import sync_playwright

URL = os.getenv("SENTINEL_URL", "http://localhost:8080")
OUT = os.getenv("SENTINEL_DEMO_OUT", "docs/demo/raw")
os.makedirs(OUT, exist_ok=True)

# Use the bundled Playwright Chromium if present (this container ships one at
# /opt/pw-browsers); otherwise fall back to the pip-installed default.
_cands = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
CHROME = _cands[-1] if _cands else None

CAPTION_JS = """
(text) => {
  let c = document.getElementById('demo-cap');
  if (!c) {
    c = document.createElement('div');
    c.id = 'demo-cap';
    c.style.cssText = 'position:fixed;left:0;right:0;bottom:0;padding:18px 24px;'
      + 'background:linear-gradient(0deg,rgba(0,0,0,.92),rgba(0,0,0,.0));'
      + 'color:#e6edf3;font:600 22px/1.4 ui-monospace,Menlo,monospace;'
      + 'text-align:center;z-index:9999;letter-spacing:.2px;';
    document.body.appendChild(c);
  }
  c.textContent = text;
}
"""


def cap(page, text):
    page.evaluate(CAPTION_JS, text)


def wait_for_gate(page, msgs, timeout_ms=90000):
    """Wait for the gate to render, cycling progress captions so the live
    Gemini 3 latency reads as intentional 'thinking' instead of dead air."""
    elapsed, step, i = 0, 1500, 0
    while elapsed < timeout_ms:
        if page.query_selector("#gate:not(.hidden)"):
            return
        cap(page, msgs[i % len(msgs)])
        i += 1
        page.wait_for_timeout(step)
        elapsed += step
    page.wait_for_selector("#gate:not(.hidden)", timeout=5000)


def main():
    with sync_playwright() as p:
        launch_kwargs = {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if CHROME:
            launch_kwargs["executable_path"] = CHROME
        browser = p.chromium.launch(**launch_kwargs)
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=OUT,
            record_video_size={"width": 1280, "height": 800},
        )
        page = ctx.new_page()

        page.goto(URL, wait_until="networkidle")
        cap(page, "AI agents that act are dangerous without a brake.")
        page.wait_for_timeout(3200)
        cap(page, "Sentinel is the brake — it guards a live GitLab deploy pipeline.")
        page.wait_for_timeout(3000)

        # Detect + Gemini 3 diagnosis + the gate
        page.click("#scan")
        wait_for_gate(page, [
            "Connecting to the GitLab MCP server…",
            "Reading the live pipeline state…",
            "Gemini 3 assessing the deployment blast radius…",
            "Weighing the risk…",
        ])
        page.wait_for_timeout(800)
        cap(page, "It wants to CANCEL the deploy. But it stops and asks a human.")
        page.wait_for_timeout(3800)

        # Deny -> HOLD
        cap(page, "I say no.")
        page.wait_for_timeout(900)
        page.click("button.deny")
        page.wait_for_selector("#result:not(.hidden)", timeout=30000)
        page.wait_for_timeout(700)
        cap(page, "HELD — the pipeline is left running. Production untouched.")
        page.wait_for_timeout(3400)

        # Re-run -> Approve -> real cancel
        page.goto(URL, wait_until="networkidle")
        cap(page, "Same risk. This time I approve.")
        page.click("#scan")
        wait_for_gate(page, [
            "Reading the next pipeline via GitLab MCP…",
            "Gemini 3 assessing the blast radius…",
        ])
        page.wait_for_timeout(1200)
        cap(page, "Approved by a human.")
        page.wait_for_timeout(900)
        page.click("button.approve")
        page.wait_for_selector("#result:not(.hidden)", timeout=30000)
        page.wait_for_timeout(700)
        cap(page, "Cancelled — for real — through GitLab's MCP server.")
        page.wait_for_timeout(3600)
        cap(page, "Approve or deny: one append-only, auditable record.")
        page.wait_for_timeout(3400)
        cap(page, "Gemini 3 · Google ADK · GitLab MCP · a human gate. Sentinel.")
        page.wait_for_timeout(3000)

        path = page.video.path()
        ctx.close()
        browser.close()
        print("VIDEO:", path)


if __name__ == "__main__":
    main()
