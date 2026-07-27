#!/usr/bin/env python3
"""Build the EXP-DUCK-028 visual audit from verified local artifacts."""

from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "experiments/duck_harness_repro/exp_duck_028_model_gate.json"
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_tn36_level3_wall_route/latest/artifacts"
    / "tn36-ef4dde99_p0_events.jsonl"
)
OUTPUT_DIR = ROOT / "artifacts/kaggle/duck_tn36_model_learning_audit"
OUTPUT = OUTPUT_DIR / "index.html"
PALETTE = [
    (255, 255, 255), (204, 204, 204), (153, 153, 153), (102, 102, 102),
    (51, 51, 51), (0, 0, 0), (229, 58, 163), (255, 123, 204),
    (249, 60, 49), (30, 147, 255), (136, 216, 241), (255, 220, 0),
    (255, 133, 27), (146, 18, 49), (79, 204, 48), (163, 86, 214),
]
ARROWS = {1: "Left", 2: "Right", 3: "Down", 33: "Up"}


def action_boards() -> list[list[list[int]]]:
    return [
        event["board"]
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for event in [json.loads(line)]
        if event.get("type") == "action" and event.get("board")
    ]


def render_board(board: list[list[int]], output: Path) -> None:
    image = Image.new("RGB", (64, 64))
    image.putdata([PALETTE[int(value)] for row in board for value in row])
    image.resize((512, 512), Image.Resampling.NEAREST).save(output)


def program_buttons(level: str, program: list[int]) -> str:
    return "".join(
        f"""<button class="program-step" data-level="{level}" data-step="{index}">
<span>{index + 1}</span><strong>{html.escape(ARROWS[command])}</strong>
<small>command {command}</small></button>"""
        for index, command in enumerate(program)
    )


def failed_rows(observations: list[dict]) -> str:
    failures = [row for row in observations if not row["solved"]][:8]
    return "".join(
        "<tr><td>"
        + " ".join(ARROWS[value] for value in row["program"])
        + "</td><td>Did not advance</td></tr>"
        for row in failures
    )


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    boards = action_boards()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Action 7 exposes level 2, action 16 exposes level 3, action 25 exposes level 4.
    snapshots = {
        "level2-before": boards[6],
        "level2-after": boards[15],
        "level3-before": boards[15],
        "level3-after": boards[24],
    }
    for name, board in snapshots.items():
        render_board(board, OUTPUT_DIR / f"{name}.png")

    level2 = result["searches"]["2"]
    level3 = result["searches"]["3"]
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EXP-DUCK-028 Model Learning Audit</title>
<style>
:root {{
  color-scheme: dark; --bg:#101315; --panel:#171b1e; --line:#39434a;
  --text:#f4f6f7; --muted:#aeb8bf; --blue:#58a6ff; --green:#54d19b;
  --yellow:#ffd166; --red:#ff7474; --magenta:#e53aa3;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:16px/1.55 system-ui,sans-serif; }}
header, main {{ width:min(1220px,calc(100% - 32px)); margin:auto; }}
header {{ padding:42px 0 28px; }}
h1 {{ margin:0 0 8px; font-size:clamp(2rem,5vw,4rem); letter-spacing:0; }}
h2,h3 {{ letter-spacing:0; }}
p {{ color:var(--muted); }}
.status {{ display:flex; gap:8px; flex-wrap:wrap; }}
.badge {{ border:1px solid var(--line); border-radius:4px; padding:6px 10px; font-weight:700; }}
.pass {{ color:var(--green); }} .warn {{ color:var(--yellow); }} .reject {{ color:var(--red); }}
.flow {{ display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin:24px 0 42px; }}
.flow div {{ border-top:4px solid var(--blue); padding:12px; background:var(--panel); min-height:108px; }}
.flow strong {{ display:block; }} .flow span {{ color:var(--muted); font-size:.9rem; }}
section {{ border-top:1px solid var(--line); padding:34px 0; }}
.level-grid {{ display:grid; grid-template-columns:minmax(260px,.8fr) minmax(420px,1.4fr); gap:28px; }}
.boards {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
figure {{ margin:0; }} img {{ width:100%; image-rendering:pixelated; border:1px solid var(--line); }}
figcaption {{ color:var(--muted); padding-top:6px; }}
.program {{ display:grid; grid-template-columns:repeat(6,minmax(74px,1fr)); gap:8px; margin:18px 0; }}
.program-step {{ background:#20262b; color:var(--text); border:1px solid #52606a; border-radius:4px; padding:10px 5px; min-height:86px; }}
.program-step:hover,.program-step.active {{ border-color:var(--yellow); background:#2c2a20; }}
.program-step span,.program-step small {{ display:block; color:var(--muted); }}
.inspector {{ border-left:4px solid var(--yellow); background:var(--panel); padding:14px; min-height:76px; }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); }}
th,td {{ text-align:left; border-bottom:1px solid var(--line); padding:9px; }}
.evidence {{ border-left:4px solid var(--green); padding-left:14px; }}
.decision {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }}
.decision article {{ background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:16px; }}
code {{ color:var(--yellow); }}
a {{ color:#83d7ff; }}
@media(max-width:800px) {{
  .flow,.decision {{ grid-template-columns:1fr; }}
  .level-grid {{ grid-template-columns:1fr; }}
  .program {{ grid-template-columns:repeat(3,1fr); }}
}}
</style>
</head>
<body>
<header>
  <p><a href="../duck_tu93_pixel_learning_audit/index.html">Next: open the source-hidden pixel-learning audit</a></p>
  <p><a href="../duck_calculator_visual_review/index.html">Back to calculator replays</a></p>
  <h1>tn36: From guessing to planning</h1>
  <p>This page audits EXP-DUCK-028. It shows what was remembered, what goal was stated,
  what programs were tested, and what the official engine actually accepted.</p>
  <div class="status">
    <span class="badge pass">Research gate: PASS</span>
    <span class="badge warn">Source-assisted</span>
    <span class="badge reject">Pixel-only generalization: NOT PROVEN</span>
    <span class="badge">Competition submission: NO</span>
  </div>
  <div class="flow">
    <div><strong>1. Remember</strong><span>Carry forward command meanings from earlier levels.</span></div>
    <div><strong>2. State goal</strong><span>Move the editable robot onto its target.</span></div>
    <div><strong>3. Predict</strong><span>Try directions that reduce visible distance first.</span></div>
    <div><strong>4. Simulate</strong><span>Test complete programs in the official local engine.</span></div>
    <div><strong>5. Verify</strong><span>Accept only if the engine advances a level.</span></div>
  </div>
</header>
<main>
<section>
  <div class="level-grid">
    <div>
      <p class="pass"><strong>Level 2 · learned behavior reused</strong></p>
      <h2>Objective before action</h2>
      <p>{html.escape(level2["objective"]["statement"])}</p>
      <p class="evidence">The target is above the robot. Memory says command
      <code>33</code> means Up, so Up is tested first.</p>
      <p><strong>{level2["tested_candidates"]} candidate</strong> tested.
      The engine advanced to level 3.</p>
    </div>
    <div class="boards">
      <figure><img src="level2-before.png" alt="tn36 level 2 before planning"><figcaption>Before: level 2</figcaption></figure>
      <figure><img src="level2-after.png" alt="tn36 level 2 after planning"><figcaption>After: engine advanced to level 3</figcaption></figure>
    </div>
  </div>
  <div class="program">{program_buttons("2", level2["winning_program"])}</div>
  <div class="inspector" id="inspector-2">Select a step. Each button writes one remembered movement command into the visible program editor.</div>
</section>
<section>
  <div class="level-grid">
    <div>
      <p class="pass"><strong>Level 3 · held-out search</strong></p>
      <h2>Old controls, new obstacle rule</h2>
      <p>{html.escape(level3["objective"]["statement"])}</p>
      <p class="evidence">Right and Up are tried first because the target is right
      and above. The walls change after every third command, so order matters.</p>
      <p><strong>{level3["tested_candidates"]} candidates</strong> tested before
      one advanced the engine to level 4.</p>
    </div>
    <div class="boards">
      <figure><img src="level3-before.png" alt="tn36 level 3 before planning"><figcaption>Before: level 3 with switching walls</figcaption></figure>
      <figure><img src="level3-after.png" alt="tn36 level 3 after planning"><figcaption>After: engine advanced to level 4</figcaption></figure>
    </div>
  </div>
  <div class="program">{program_buttons("3", level3["winning_program"])}</div>
  <div class="inspector" id="inspector-3">Select a step to inspect its predicted movement and its position in the three-command wall cycle.</div>
  <h3>Some rejected hypotheses</h3>
  <table><thead><tr><th>Predicted program</th><th>Actual result</th></tr></thead>
  <tbody>{failed_rows(level3["observations"])}</tbody></table>
</section>
<section>
  <h2>What this proves, and what it does not</h2>
  <div class="decision">
    <article><h3 class="pass">Keep</h3><p>Cross-level control memory, explicit objectives,
    direction-ranked search, and level-advance verification.</p></article>
    <article><h3 class="reject">Reject</h3><p>Copying the visible demonstration.
    <code>Down Down Down Down</code> did not solve level 3.</p></article>
    <article><h3 class="warn">Next gate</h3><p>Infer the simulator from pixels and
    observed action effects, then pass a new held-out game without reading its source.</p></article>
  </div>
</section>
</main>
<script>
const meanings = {{1:"move left",2:"move right",3:"move down",33:"move up"}};
const programs = {{
  "2": {json.dumps(level2["winning_program"])},
  "3": {json.dumps(level3["winning_program"])}
}};
document.querySelectorAll(".program-step").forEach(button => {{
  button.addEventListener("click", () => {{
    const level = button.dataset.level;
    const index = Number(button.dataset.step);
    document.querySelectorAll(`.program-step[data-level="${{level}}"]`).forEach(item => item.classList.remove("active"));
    button.classList.add("active");
    const command = programs[level][index];
    const cycle = (index % 3) + 1;
    const wallText = level === "3" && cycle === 3
      ? " After this third command, the wall state switches."
      : level === "3" ? ` This is command ${{cycle}} of the current wall cycle.` : "";
    document.querySelector(`#inspector-${{level}}`).textContent =
      `Step ${{index + 1}} predicts: ${{meanings[command]}} one cell.${{wallText}}`;
  }});
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
