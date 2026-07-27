#!/usr/bin/env python3
"""Build a local visual comparison of Duck calculator experiments."""

from __future__ import annotations

import base64
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
        "summary": "The LLM chose every action. It reached 1/7 levels, then spent 152 actions on level 2 without solving it.",
        "result": "1/7 levels",
        "calculator_start": None,
        "watch": "There is no calculator section in this replay.",
        "root": "duck_full_eval_ft09_overlap",
        "game": "tn36-ef4dde99",
    },
    {
        "id": "tn36-after",
        "title": "2. Calculator that reached 1.11: tn36",
        "subtitle": "EXP-DUCK-024, normal Duck then deterministic postlude",
        "summary": "The LLM played first. After it stopped on level 2, the calculator executed 19 pre-verified actions and reached 3/7 levels.",
        "result": "3/7 levels",
        "calculator_start": 232,
        "watch": "The calculator is the short green section at the end of the timeline.",
        "root": "duck_full_eval_tn36_postlude",
        "game": "tn36-ef4dde99",
    },
    {
        "id": "tu93-proof",
        "title": "3. Latest calculator proof: tu93",
        "subtitle": "EXP-DUCK-027, calculator only",
        "summary": "The LLM made no decisions. The calculator recognized each exact board and followed three fixed routes: 18, 10, and 19 actions.",
        "result": "3/9 levels",
        "calculator_start": 0,
        "watch": "The entire replay is calculator-controlled. It uses zero LLM tokens.",
        "root": "duck_tu93_level3_route",
        "game": "tu93-0768757b",
    },
    {
        "id": "tu93-current",
        "title": "4. Why the previous tu93 test proved nothing",
        "subtitle": "EXP-DUCK-026, calculator did not activate",
        "summary": "Normal Duck had already reached level 3, so the calculator correctly skipped. The higher local result could not be credited to the calculator.",
        "result": "2/9 before calculator; no added levels",
        "calculator_start": None,
        "watch": "This is an inconclusive control, not a calculator success.",
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


def load_game_run(run_root: Path, game_id: str) -> dict:
    benchmark = json.loads(
        (run_root / "benchmark.json").read_text(encoding="utf-8")
    )
    return next(
        run
        for run in benchmark["game_runs"]
        if run["game_id"] == game_id
    )


def action_label(action: dict) -> str:
    action_id = action.get("id", "UNKNOWN")
    data = action.get("data") or {}
    labels = {
        "ACTION1": "↑ Up",
        "ACTION2": "↓ Down",
        "ACTION3": "← Left",
        "ACTION4": "→ Right",
        "ACTION5": "Action 5",
        "ACTION7": "Undo",
        "RESET": "Reset",
    }
    if action_id == "ACTION6":
        return f"Mouse ({data.get('x', '?')}, {data.get('y', '?')})"
    return labels.get(action_id, action_id)


def packed_board(board: list[list[int]]) -> str:
    flat = [int(value) for row in board for value in row]
    payload = bytes(
        (flat[index] << 4) | flat[index + 1]
        for index in range(0, len(flat), 2)
    )
    return base64.b64encode(payload).decode("ascii")


def action_boards(event_path: Path) -> list[list[list[int]]]:
    return [
        event["board"]
        for line in event_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for event in [json.loads(line)]
        if event.get("type") == "action"
    ]


def build_action_controls(
    case_id: str,
    run: dict,
    calculator_start: int | None,
    boards: list[list[list[int]]],
) -> tuple[str, str, int, int]:
    history = run["history"]
    total_actions = len(history)
    if len(boards) != total_actions:
        raise ValueError(
            f"{case_id}: {len(boards)} action boards != {total_actions} actions"
        )
    calculator_actions = (
        total_actions - calculator_start
        if calculator_start is not None
        else 0
    )
    duck_actions = total_actions - calculator_actions
    levels = []
    cursor = 0
    for level, count in enumerate(run["actions_per_level"], start=1):
        if count <= 0:
            continue
        end = min(cursor + count, total_actions)
        status = "solved" if level <= run["levels_completed"] else "current"
        levels.append((level, cursor, end, status))
        cursor = end

    level_buttons = []
    action_panels = []
    for panel_index, (level, start, end, status) in enumerate(levels):
        level_buttons.append(
            f"""<button class="level-button{' active' if panel_index == 0 else ''}"
 data-panel="{case_id}-level-{level}" data-start="{start}" data-end="{end}">
Level {level} · {status} · {end - start} actions</button>"""
        )
        action_buttons = []
        for index in range(start, end):
            owner = (
                "calculator"
                if calculator_start is not None and index >= calculator_start
                else "duck"
            )
            label = action_label(history[index]["action"])
            action_buttons.append(
                f"""<button class="action-button {owner}" data-action-index="{index}"
 data-board="{packed_board(boards[index])}"
 title="View recorded action {index + 1}: {html.escape(label)} · {owner}">
<span>{index + 1}</span>{html.escape(label)}</button>"""
            )
        action_panels.append(
            f"""<div id="{case_id}-level-{level}" class="action-panel"
{' hidden' if panel_index else ''}>{''.join(action_buttons)}</div>"""
        )
    return (
        "".join(level_buttons),
        "".join(action_panels),
        duck_actions,
        calculator_actions,
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sections = []
    for case in CASES:
        run_root = ROOT / "artifacts/kaggle" / case["root"] / "latest"
        event_path = run_root / "artifacts" / f"{case['game']}_p0_events.jsonl"
        movie_path = run_root / "movies" / f"g{case['game']}_p0.mp4"
        run = load_game_run(run_root, case["game"])
        boards = action_boards(event_path)
        level_buttons, action_panels, duck_actions, calculator_actions = (
            build_action_controls(
                case["id"],
                run,
                case["calculator_start"],
                boards,
            )
        )
        still_name = f"{case['id']}.png"
        render_board(latest_board(event_path), OUTPUT_DIR / still_name)
        movie_rel = Path("..") / case["root"] / "latest/movies" / movie_path.name
        total_actions = duck_actions + calculator_actions
        duck_width = (
            100 * duck_actions / total_actions if total_actions else 0
        )
        calculator_width = 100 - duck_width
        sections.append(
            f"""<section class="case">
  <div class="copy">
    <p class="number">{html.escape(case["subtitle"])}</p>
    <h2>{html.escape(case["title"])}</h2>
    <p>{html.escape(case["summary"])}</p>
    <p class="result"><strong>Result:</strong> {html.escape(case["result"])}</p>
    <div class="phase-bar" aria-label="Action ownership timeline">
      <span class="duck" style="width:{duck_width:.2f}%"></span>
      <span class="calculator" style="width:{calculator_width:.2f}%"></span>
    </div>
    <div class="legend">
      <span><i class="duck-key"></i>Duck LLM: {duck_actions} actions</span>
      <span><i class="calculator-key"></i>Calculator: {calculator_actions} actions</span>
    </div>
    <p class="watch">{html.escape(case["watch"])}</p>
    <a href="{movie_rel.as_posix()}">Open replay in its own page</a>
  </div>
  <div class="media">
    <div class="replay" data-total-actions="{total_actions}">
      <video controls preload="metadata" poster="{still_name}" src="{movie_rel.as_posix()}"></video>
      <div class="view-only"><strong>View-only replay.</strong> These buttons do not send inputs to the game.</div>
      <div class="exact-board">
        <canvas width="64" height="64" aria-label="Exact recorded board after the selected action"></canvas>
        <div><strong>Exact action inspector</strong><span>Click an action below to show its recorded result here.</span></div>
      </div>
      <div class="now-playing" aria-live="polite">Select a level to play it, or select an action to inspect its exact recorded board.</div>
      <div class="level-controls">{level_buttons}</div>
      <div class="action-panels">{action_panels}</div>
    </div>
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
:root {{ color-scheme: dark; --bg:#101214; --panel:#181c20; --line:#343b42; --text:#f4f6f8; --muted:#aab4bd; --accent:#68c3a3; --warn:#f0bd63; --duck:#4d91e8; --calculator:#54c68a; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; line-height:1.5; }}
header {{ max-width:1180px; margin:0 auto; padding:42px 24px 24px; }}
h1 {{ font-size:36px; line-height:1.1; margin:0 0 12px; letter-spacing:0; }}
header p {{ color:var(--muted); max-width:760px; margin:0; }}
.explainer {{ border-top:1px solid var(--line); background:#15191c; }}
.explainer-inner {{ max-width:1180px; margin:0 auto; padding:24px; }}
.explainer h2 {{ font-size:22px; margin:0 0 16px; }}
.handoff {{ display:grid; grid-template-columns:1fr auto 1fr auto 1fr; align-items:stretch; gap:12px; }}
.step {{ border:1px solid var(--line); border-radius:6px; padding:16px; background:#101214; }}
.step strong {{ display:block; margin-bottom:6px; }}
.step p {{ color:var(--muted); margin:0; font-size:14px; }}
.arrow {{ align-self:center; color:var(--warn); font-size:24px; }}
.plain-note {{ color:var(--muted); margin:16px 0 0; }}
.plain-note code {{ color:var(--text); }}
main {{ border-top:1px solid var(--line); }}
.case {{ display:grid; grid-template-columns:minmax(240px,0.75fr) minmax(0,1.25fr); gap:32px; max-width:1180px; margin:0 auto; padding:32px 24px; border-bottom:1px solid var(--line); }}
.copy h2 {{ font-size:23px; margin:6px 0 10px; letter-spacing:0; }}
.copy p {{ color:var(--muted); }}
.copy .result {{ color:var(--text); }}
.number {{ color:var(--accent) !important; font-size:13px; font-weight:700; text-transform:uppercase; }}
.phase-bar {{ display:flex; width:100%; height:12px; overflow:hidden; border:1px solid var(--line); margin:16px 0 8px; }}
.phase-bar span {{ display:block; min-width:0; }}
.phase-bar .duck {{ background:var(--duck); }}
.phase-bar .calculator {{ background:var(--calculator); }}
.legend {{ display:flex; flex-wrap:wrap; gap:12px; color:var(--muted); font-size:12px; }}
.legend i {{ display:inline-block; width:10px; height:10px; margin-right:5px; }}
.duck-key {{ background:var(--duck); }}
.calculator-key {{ background:var(--calculator); }}
.watch {{ color:var(--warn) !important; font-size:13px; }}
a {{ color:#8dd9ff; }}
.media {{ display:grid; grid-template-columns:minmax(0,1.4fr) minmax(180px,0.6fr); gap:14px; align-items:start; }}
.replay, figure {{ width:100%; margin:0; background:#000; border:1px solid var(--line); border-radius:6px; }}
video {{ aspect-ratio:1/1; image-rendering:pixelated; }}
video {{ display:block; width:100%; border:0; }}
.now-playing {{ min-height:44px; padding:10px 12px; border-top:1px solid var(--line); color:var(--text); font-size:13px; }}
.view-only {{ padding:9px 12px; border-top:1px solid var(--line); color:var(--warn); font-size:12px; }}
.exact-board {{ display:grid; grid-template-columns:128px 1fr; gap:12px; align-items:center; padding:10px 12px; border-top:1px solid var(--line); background:#111; }}
.exact-board canvas {{ width:128px; height:128px; image-rendering:pixelated; border:1px solid var(--line); }}
.exact-board strong, .exact-board span {{ display:block; }}
.exact-board span {{ margin-top:5px; color:var(--muted); font-size:12px; }}
.level-controls {{ display:flex; gap:6px; padding:10px 12px; border-top:1px solid var(--line); overflow-x:auto; }}
.level-button, .action-button {{ border:1px solid var(--line); color:var(--text); background:#20252a; cursor:pointer; font:inherit; }}
.level-button {{ flex:0 0 auto; padding:7px 10px; font-size:12px; }}
.level-button.active {{ border-color:var(--warn); color:var(--warn); }}
.action-panels {{ border-top:1px solid var(--line); }}
.action-panel {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(112px,1fr)); gap:5px; max-height:170px; padding:10px 12px; overflow:auto; }}
.action-button {{ min-height:34px; padding:5px 7px; text-align:left; font-size:11px; }}
.action-button span {{ display:inline-block; min-width:24px; color:var(--muted); }}
.action-button.duck {{ border-left:4px solid var(--duck); }}
.action-button.calculator {{ border-left:4px solid var(--calculator); }}
.action-button.active {{ outline:2px solid var(--warn); outline-offset:1px; }}
figure {{ padding:10px; }}
figure img {{ display:block; width:100%; image-rendering:pixelated; }}
figcaption {{ color:var(--muted); font-size:12px; margin-top:8px; }}
.note {{ color:var(--warn); }}
@media (max-width:800px) {{ .case,.media,.handoff {{ grid-template-columns:1fr; }} .arrow {{ transform:rotate(90deg); justify-self:center; }} h1 {{ font-size:30px; }} }}
</style>
</head>
<body>
<header>
  <p><a href="../duck_tn36_model_learning_audit/index.html">Open the new objective and planning audit</a></p>
  <h1>Duck Calculator Visual Review</h1>
  <p>The calculator is code behind the player, not an object drawn on the board. The replay shows its actions, while the colored timeline below shows who chose them.</p>
</header>
<section class="explainer">
  <div class="explainer-inner">
    <h2>What “calculator” means here</h2>
    <div class="handoff">
      <div class="step"><strong>1. Look</strong><p>Read the current 64 × 64 board and its level number.</p></div>
      <div class="arrow">→</div>
      <div class="step"><strong>2. Match</strong><p>Check whether the board exactly matches a known puzzle state.</p></div>
      <div class="arrow">→</div>
      <div class="step"><strong>3. Act</strong><p>Return a tested route such as UP, UP, RIGHT, without asking the LLM.</p></div>
    </div>
    <p class="plain-note">So yes: physically, it is a small Python code block. Functionally, it is like giving Duck a memorized, checked answer key for one recognized level. It is <strong>not</strong> a general calculator visible inside the game.</p>
  </div>
</section>
<main>
{''.join(sections)}
</main>
<script>
document.querySelectorAll('.replay').forEach((replay) => {{
  const video = replay.querySelector('video');
  const total = Number(replay.dataset.totalActions);
  const status = replay.querySelector('.now-playing');
  const levelButtons = [...replay.querySelectorAll('.level-button')];
  const actionButtons = [...replay.querySelectorAll('.action-button')];
  const canvas = replay.querySelector('canvas');
  const context = canvas.getContext('2d');
  const palette = {json.dumps(["#ffffff", "#cccccc", "#999999", "#666666", "#333333", "#000000", "#e53aa3", "#ff7bcc", "#f93c31", "#1e93ff", "#88d8f1", "#ffdc00", "#ff851b", "#921231", "#4fcc30", "#a356d6"])};

  function renderBoard(encoded) {{
    const raw = atob(encoded);
    const image = context.createImageData(64, 64);
    for (let pixel = 0; pixel < 4096; pixel += 1) {{
      const packed = raw.charCodeAt(Math.floor(pixel / 2));
      const colorIndex = pixel % 2 === 0 ? packed >> 4 : packed & 15;
      const color = palette[colorIndex];
      image.data[pixel * 4] = parseInt(color.slice(1, 3), 16);
      image.data[pixel * 4 + 1] = parseInt(color.slice(3, 5), 16);
      image.data[pixel * 4 + 2] = parseInt(color.slice(5, 7), 16);
      image.data[pixel * 4 + 3] = 255;
    }}
    context.putImageData(image, 0, 0);
  }}

  function seekToAction(index, play) {{
    if (!video.duration || !total) return;
    video.currentTime = Math.min(video.duration, (index + 0.15) / total * video.duration);
    if (play) video.play();
    else video.pause();
    updateActive(index);
  }}

  function showPanel(panelId) {{
    replay.querySelectorAll('.action-panel').forEach((panel) => {{
      panel.hidden = panel.id !== panelId;
    }});
    levelButtons.forEach((button) => {{
      button.classList.toggle('active', button.dataset.panel === panelId);
    }});
  }}

  function updateActive(index) {{
    const action = actionButtons.find((button) => Number(button.dataset.actionIndex) === index);
    if (!action) return;
    actionButtons.forEach((button) => button.classList.toggle('active', button === action));
    const panel = action.closest('.action-panel');
    showPanel(panel.id);
    const owner = action.classList.contains('calculator') ? 'Calculator' : 'Duck LLM';
    status.textContent = `Recorded result: ${{owner}} · ${{action.textContent.trim()}}`;
    renderBoard(action.dataset.board);
    action.scrollIntoView({{block:'nearest', inline:'nearest'}});
  }}

  levelButtons.forEach((button) => {{
    button.addEventListener('click', () => {{
      showPanel(button.dataset.panel);
      seekToAction(Number(button.dataset.start), true);
    }});
  }});

  actionButtons.forEach((button) => {{
    button.addEventListener('click', () => {{
      video.pause();
      updateActive(Number(button.dataset.actionIndex));
    }});
  }});

  video.addEventListener('timeupdate', () => {{
    if (!video.duration || !total) return;
    const index = Math.min(total - 1, Math.floor(video.currentTime / video.duration * total));
    updateActive(index);
  }});

  if (actionButtons.length) updateActive(Number(actionButtons[0].dataset.actionIndex));
}});
</script>
</body>
</html>
"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
