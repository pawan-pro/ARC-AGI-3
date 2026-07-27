#!/usr/bin/env python3
"""Build a local visual comparison of Duck calculator experiments."""

from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "artifacts/kaggle/duck_calculator_visual_review"
OUTPUT = OUTPUT_DIR / "index.html"
PALETTE = [
    (255, 255, 255), (204, 204, 204), (153, 153, 153), (102, 102, 102),
    (51, 51, 51), (0, 0, 0), (229, 58, 163), (255, 123, 204),
    (249, 60, 49), (30, 147, 255), (136, 216, 241), (255, 220, 0),
    (255, 133, 27), (146, 18, 49), (79, 204, 48), (163, 86, 214),
]

CASES = [
    {
        "id": "tn36-before",
        "title": "1. Before calculator: tn36",
        "subtitle": "EXP-DUCK-009, normal Duck only",
        "summary": "Duck reached 1/7 levels. This is the comparison case before the successful postlude.",
        "root": "duck_full_eval_ft09_overlap",
        "game": "tn36-ef4dde99",
    },
    {
        "id": "tn36-after",
        "title": "2. Calculator that reached 1.11: tn36",
        "subtitle": "EXP-DUCK-024, normal Duck then deterministic postlude",
        "summary": "Duck reasoned normally first. The zero-token repair then reached 3/7 levels. This notebook scored 1.11 publicly.",
        "root": "duck_full_eval_tn36_postlude",
        "game": "tn36-ef4dde99",
    },
    {
        "id": "tu93-proof",
        "title": "3. Proposed calculator proof: tu93",
        "subtitle": "EXP-DUCK-025, isolated deterministic route",
        "summary": "The calculator solved levels 1-2 in exactly 28 actions with zero LLM tokens.",
        "root": "duck_tu93_route_helper",
        "game": "tu93-0768757b",
    },
    {
        "id": "tu93-current",
        "title": "4. Current tu93 state",
        "subtitle": "EXP-DUCK-026, normal Duck already reached level 3",
        "summary": "The postlude correctly skipped because Duck had already completed two levels. The still shows the resulting level-3 state.",
        "root": "duck_full_eval_tu93_postlude",
        "game": "tu93-0768757b",
    },
]


def latest_board(event_path: Path) -> list[list[int]]:
    events = [
        json.loads(line)
        for line in event_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return next(event["board"] for event in reversed(events) if event.get("board"))


def render_board(board: list[list[int]], output: Path) -> None:
    height, width = len(board), len(board[0])
    image = Image.new("RGB", (width, height))
    image.putdata([PALETTE[int(value)] for row in board for value in row])
    image.resize((width * 8, height * 8), Image.Resampling.NEAREST).save(output)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sections = []
    for case in CASES:
        run_root = ROOT / "artifacts/kaggle" / case["root"] / "latest"
        event_path = run_root / "artifacts" / f"{case['game']}_p0_events.jsonl"
        movie_path = run_root / "movies" / f"g{case['game']}_p0.mp4"
        still_name = f"{case['id']}.png"
        render_board(latest_board(event_path), OUTPUT_DIR / still_name)
        movie_rel = Path("..") / case["root"] / "latest/movies" / movie_path.name
        sections.append(
            f"""<section class="case">
  <div class="copy">
    <p class="number">{html.escape(case["subtitle"])}</p>
    <h2>{html.escape(case["title"])}</h2>
    <p>{html.escape(case["summary"])}</p>
    <a href="{movie_rel.as_posix()}">Open replay in its own page</a>
  </div>
  <div class="media">
    <video controls loop preload="metadata" poster="{still_name}" src="{movie_rel.as_posix()}"></video>
    <figure><img src="{still_name}" alt="Final recorded board for {html.escape(case['title'])}"><figcaption>Final recorded board</figcaption></figure>
  </div>
</section>"""
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Duck Calculator Visual Review</title>
<style>
:root {{ color-scheme: dark; --bg:#101214; --panel:#181c20; --line:#343b42; --text:#f4f6f8; --muted:#aab4bd; --accent:#68c3a3; --warn:#f0bd63; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; line-height:1.5; }}
header {{ max-width:1180px; margin:0 auto; padding:42px 24px 24px; }}
h1 {{ font-size:36px; line-height:1.1; margin:0 0 12px; letter-spacing:0; }}
header p {{ color:var(--muted); max-width:760px; margin:0; }}
main {{ border-top:1px solid var(--line); }}
.case {{ display:grid; grid-template-columns:minmax(240px,0.75fr) minmax(0,1.25fr); gap:32px; max-width:1180px; margin:0 auto; padding:32px 24px; border-bottom:1px solid var(--line); }}
.copy h2 {{ font-size:23px; margin:6px 0 10px; letter-spacing:0; }}
.copy p {{ color:var(--muted); }}
.number {{ color:var(--accent) !important; font-size:13px; font-weight:700; text-transform:uppercase; }}
a {{ color:#8dd9ff; }}
.media {{ display:grid; grid-template-columns:minmax(0,1.4fr) minmax(180px,0.6fr); gap:14px; align-items:start; }}
video, figure {{ width:100%; margin:0; background:#000; border:1px solid var(--line); border-radius:6px; }}
video {{ aspect-ratio:1/1; image-rendering:pixelated; }}
figure {{ padding:10px; }}
figure img {{ display:block; width:100%; image-rendering:pixelated; }}
figcaption {{ color:var(--muted); font-size:12px; margin-top:8px; }}
.note {{ color:var(--warn); }}
@media (max-width:800px) {{ .case,.media {{ grid-template-columns:1fr; }} h1 {{ font-size:30px; }} }}
</style>
</head>
<body>
<header>
  <h1>Duck Calculator Visual Review</h1>
  <p>Play each replay and use the timeline to compare normal reasoning with deterministic postludes. The current proposal now targets <span class="note">tu93 level 3</span>, because levels 1-2 may already be solved by normal Duck.</p>
</header>
<main>
{''.join(sections)}
</main>
</body>
</html>
"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
