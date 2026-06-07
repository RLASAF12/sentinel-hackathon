"""Capture the Sentinel demo phase-by-phase as PNG screenshots.

Drives the live web UI (SENTINEL_DEMO=false) with headless Chromium:
landing -> Gemini 3 reasoning -> the risk GATE -> Deny (HOLD) -> Approve
(real GitLab cancel) -> audit. Outputs scripts/shots/sentinel-NN-*.png.

Run with the web server already up on :8080 and a running pipeline available.
"""

import os
import sys
import time

from playwright.sync_api import sync_playwright

URL = os.getenv("SENTINEL_URL", "http://localhost:8080")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
OUT = os.path.join(os.path.dirname(__file__), "shots")
os.makedirs(OUT, exist_ok=True)


def shot(page, name):
    path = os.path.join(OUT, name)
    page.screenshot(path=path, full_page=True)
    print("saved", path)


def wait_visible(page, sel, timeout=60000):
    page.wait_for_selector(sel + ":not(.hidden)", timeout=timeout)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 960},
                                device_scale_factor=2)

        # Phase 1 — landing
        page.goto(URL, wait_until="networkidle")
        shot(page, "sentinel-01-landing.png")

        # Phase 2/3 — scan -> Gemini 3 reasoning + the GATE
        page.click("#scan")
        wait_visible(page, "#gate")
        time.sleep(0.5)
        shot(page, "sentinel-02-reasoning-and-gate.png")
        page.locator("#gate").screenshot(path=os.path.join(OUT, "sentinel-03-gate-hero.png"))
        print("saved gate hero")

        # Phase 4 — DENY -> HELD
        page.click("button.deny")
        wait_visible(page, "#result")
        time.sleep(0.5)
        shot(page, "sentinel-04-denied-held.png")

        # Phase 5 — APPROVE on a fresh scan -> real GitLab cancel
        page.goto(URL, wait_until="networkidle")
        page.click("#scan")
        wait_visible(page, "#gate")
        page.click("button.approve")
        wait_visible(page, "#result")
        time.sleep(1.0)
        shot(page, "sentinel-05-approved-executed.png")

        browser.close()


if __name__ == "__main__":
    sys.exit(main())
