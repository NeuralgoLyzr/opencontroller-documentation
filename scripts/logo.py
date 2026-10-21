#!/usr/bin/env python3
"""The navbar logo: the console's mark and the wordmark set in Manrope, as
PNGs at 2x, one per theme. SVG text cannot load a web font, so the wordmark
is rendered through Chrome like the diagrams. Run from the site's root."""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
from diagrams import CHROME

W, H = 212, 32
THEMES = {"light": ("#141311", "#fdfcf9"), "dark": ("#fdfcf9", "#141311")}
for theme, (ink, paper) in THEMES.items():
    html = f'''<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@700&display=swap" rel="stylesheet">
<style>html,body{{margin:0;background:transparent}}
.l{{display:flex;align-items:center;gap:10px;height:{H}px;width:{W}px;font:700 19px/1 Manrope,sans-serif;letter-spacing:-0.02em;color:{ink}}}</style>
<div class="l"><svg width="32" height="32" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="{ink}"/>
<g fill="none" stroke="{paper}" stroke-width="2" stroke-linecap="round"><circle cx="16" cy="16" r="9"/><circle cx="16" cy="16" r="4.5"/><path d="M16 16l6.5-6.5"/></g>
<circle cx="16" cy="16" r="1.6" fill="{paper}"/></svg><span>opencontroller</span></div>'''
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html); path = f.name
    out = os.path.join("logo", f"{theme}.png")
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--default-background-color=00000000", f"--window-size={W},{H}", "--virtual-time-budget=8000",
                    f"--screenshot={out}", f"file://{path}"], check=True, capture_output=True)
    os.unlink(path); print(out)
