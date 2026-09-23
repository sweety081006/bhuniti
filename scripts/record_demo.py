"""Record a walkthrough of the running BhuNiti prototype as an MP4.

    .\\.venv\\Scripts\\python.exe scripts\\record_demo.py

Needs both servers running (API :8000, frontend :3000) and ffmpeg on PATH.
Output: demo\\bhuniti_demo.mp4
"""

import glob
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "demo"
OUT_DIR.mkdir(exist_ok=True)
BASE = "http://localhost:3000"
W, H = 1280, 800

# Fake cursor so the viewer can see where clicks happen (Playwright video has no OS cursor).
CURSOR_JS = """
(() => {
  const c = document.createElement('div');
  c.id = '__cursor';
  Object.assign(c.style, {position:'fixed', zIndex: 2147483647, width:'18px', height:'18px',
    borderRadius:'50%', background:'rgba(232,122,30,.85)', border:'2px solid #fff',
    boxShadow:'0 0 0 3px rgba(232,122,30,.35)', pointerEvents:'none', left:'-50px', top:'-50px',
    transition:'transform .08s'});
  document.addEventListener('DOMContentLoaded', () => document.body.appendChild(c));
  if (document.body) document.body.appendChild(c);
  window.addEventListener('mousemove', e => { c.style.left = (e.clientX-9)+'px'; c.style.top = (e.clientY-9)+'px'; }, true);
  window.addEventListener('mousedown', () => { c.style.transform='scale(.7)'; }, true);
  window.addEventListener('mouseup',   () => { c.style.transform='scale(1)'; }, true);
})();
"""

t0 = None
cuts = []  # (start_s, end_s) segments to remove from the video


def now():
    return time.time() - t0


def pause(page, s):
    page.wait_for_timeout(int(s * 1000))


def glide_click(page, locator, settle=0.6):
    """Move the fake cursor smoothly to the element, then click it."""
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    page.mouse.move(x, y, steps=25)
    pause(page, 0.35)
    page.mouse.click(x, y)
    pause(page, settle)


def main():
    global t0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": W, "height": H},
            record_video_dir=str(OUT_DIR),
            record_video_size={"width": W, "height": H},
        )
        ctx.add_init_script(CURSOR_JS)
        page = ctx.new_page()
        t0 = time.time()

        # 1. Overview
        page.goto(BASE, wait_until="networkidle")
        page.mouse.move(640, 400, steps=10)
        pause(page, 4)

        # 2. Sign in (home page IS the login page) -> lands on AI Search
        glide_click(page, page.locator(".role-card").nth(1))   # show the Legal Authority option
        pause(page, 1.2)
        glide_click(page, page.locator(".role-card").nth(0))   # back to Researcher
        pause(page, 1)
        page.locator("input[type=password]").click()
        page.keyboard.type("demo1234", delay=70)
        pause(page, 0.6)
        glide_click(page, page.locator("form button[type=submit]"))
        page.wait_for_url("**/search", timeout=15_000)
        page.wait_for_load_state("networkidle")
        pause(page, 2.5)

        # 3. AI Search with a cited answer
        glide_click(page, page.locator(".card button.ghost").first)  # first example question
        pause(page, 3)                       # show the "Searching..." state briefly
        cut_start = now()
        page.wait_for_selector(".answer", timeout=400_000)
        cut_end = now() - 0.5
        if cut_end > cut_start + 1:
            cuts.append((cut_start, cut_end))
        pause(page, 7)
        page.mouse.wheel(0, 500)
        pause(page, 5)

        # 4. GIS Studio
        glide_click(page, page.locator("nav").get_by_role("link", name="GIS Studio", exact=True))
        page.wait_for_load_state("networkidle")
        pause(page, 5)
        page.select_option("select", "Muzaffarpur")
        pause(page, 5)
        glide_click(page, page.get_by_role("button", name="Show Bhuvan LULC"))
        pause(page, 6)

        # 5. Policy Sandbox
        glide_click(page, page.locator("nav").get_by_role("link", name="Policy Sandbox", exact=True))
        page.wait_for_load_state("networkidle")
        pause(page, 2.5)
        page.select_option("select", "Muzaffarpur")
        pause(page, 1)
        sliders = page.locator("input[type=range]")
        sliders.nth(0).focus()
        for _ in range(5):                   # horizon 5 -> 10 years
            page.keyboard.press("ArrowRight")
            pause(page, 0.15)
        sliders.nth(2).focus()               # adoption rate up
        for _ in range(4):
            page.keyboard.press("ArrowRight")
            pause(page, 0.15)
        pause(page, 1)
        glide_click(page, page.get_by_role("button", name="Run scenario"))
        page.wait_for_selector(".recharts-surface", timeout=30_000)
        pause(page, 6)
        page.mouse.wheel(0, 400)
        pause(page, 5)

        # 6. Dashboards
        glide_click(page, page.locator("nav").get_by_role("link", name="Dashboards", exact=True))
        page.wait_for_load_state("networkidle")
        pause(page, 5)
        page.mouse.wheel(0, 500)
        pause(page, 5)

        # 7. sign out -> back to the login page
        glide_click(page, page.get_by_role("button", name="Sign out"))
        page.wait_for_url(BASE + "/", timeout=15_000)
        pause(page, 3)

        video = page.video
        ctx.close()
        webm = Path(video.path())
        browser.close()

    print(f"raw video: {webm}  cuts: {cuts}")
    (OUT_DIR / "cuts.json").write_text(json.dumps({"webm": str(webm), "cuts": cuts}))
    mp4 = OUT_DIR / "bhuniti_demo.mp4"
    to_mp4(webm, mp4, cuts)
    print(f"DONE -> {mp4}")


def to_mp4(webm: Path, mp4: Path, cuts):
    """Convert to H.264 MP4, removing the LLM waiting segments."""
    if cuts:
        # keep-segments between the cuts
        keep, pos = [], 0.0
        for a, b in cuts:
            keep.append((pos, a))
            pos = b
        keep.append((pos, None))
        parts, labels = [], []
        for i, (a, b) in enumerate(keep):
            rng = f"start={a:.2f}" + (f":end={b:.2f}" if b else "")
            parts.append(f"[0:v]trim={rng},setpts=PTS-STARTPTS[v{i}]")
            labels.append(f"[v{i}]")
        fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(keep)}:v=1:a=0[out]"
        vf = ["-filter_complex", fc, "-map", "[out]"]
    else:
        vf = []
    cmd = [ffmpeg_path(), "-y", "-i", str(webm), *vf, "-c:v", "libx264", "-preset", "medium",
           "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)]
    subprocess.run(cmd, check=True, capture_output=True)


def ffmpeg_path() -> str:
    """ffmpeg from PATH, else the winget install location."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    hits = glob.glob(os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\**infmpeg.exe"), recursive=True)
    if not hits:
        raise FileNotFoundError("ffmpeg not found - install with: winget install Gyan.FFmpeg")
    return hits[0]


if __name__ == "__main__":
    main()
