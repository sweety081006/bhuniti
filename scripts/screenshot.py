"""Full-page screenshot of any BhuNiti page (signed in as the demo researcher).

    .\\.venv\\Scripts\\python.exe scripts\\screenshot.py /dashboard
    .\\.venv\\Scripts\\python.exe scripts\\screenshot.py /map demo/map.png
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://localhost:3000"

route = sys.argv[1] if len(sys.argv) > 1 else "/dashboard"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "demo" / f"{route.strip('/') or 'home'}.png"
out.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
    page.goto(BASE, wait_until="networkidle")
    if route != "/":  # sign in so the role badge shows a real user
        page.locator("input[type=password]").fill("demo1234")
        page.locator("form button[type=submit]").click()
        page.wait_for_url("**/search", timeout=15_000)
        page.goto(BASE + route, wait_until="networkidle")
    page.wait_for_timeout(2500)  # let charts / map tiles finish drawing
    page.screenshot(path=str(out), full_page=True)
    browser.close()

print(f"saved {out}")
