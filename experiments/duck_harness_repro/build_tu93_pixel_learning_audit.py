#!/usr/bin/env python3
"""Build the EXP-DUCK-029 source-hidden pixel-learning visual audit."""

from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "experiments/duck_harness_repro/exp_duck_029_pixel_gate.json"
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_tu93_level3_route/latest/artifacts"
    / "tu93-0768757b_p0_events.jsonl"
)
OUTPUT_DIR = ROOT / "artifacts/kaggle/duck_tu93_pixel_learning_audit"
OUTPUT = OUTPUT_DIR / "index.html"
PALETTE = [
    (255, 255, 255), (204, 204, 204), (153, 153, 153), (102, 102, 102),
    (51, 51, 51), (0, 0, 0), (229, 58, 163), (255, 123, 204),
    (249, 60, 49), (30, 147, 255), (136, 216, 241), (255, 220, 0),
    (255, 133, 27), (146, 18, 49), (79, 204, 48), (163, 86, 214),
]


def load_actions() -> list[dict]:
    return [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("type") == "action"
    ]


def board_image(board: list[list[int]], scale: int = 8) -> Image.Image:
    image = Image.new("RGB", (64, 64))
    image.putdata([PALETTE[int(value)] for row in board for value in row])
    return image.resize((64 * scale, 64 * scale), Image.Resampling.NEAREST)


def render_route(
    board: list[list[int]],
    steps: list[dict],
    output: Path,
    *,
    failure_step: int | None = None,
) -> None:
    scale = 8
    image = board_image(board, scale)
    draw = ImageDraw.Draw(image)
    points = [(43 * scale, 43 * scale)]
    points.extend(
        (int(step["destination"][1]) * scale, int(step["destination"][0]) * scale)
        for step in steps
    )
    draw.line(points, fill=(84, 209, 155), width=4)
    for index, (x, y) in enumerate(points[1:], start=1):
        color = (255, 116, 116) if index == failure_step else (255, 209, 102)
        radius = 6 if index in {10, 11, 16, 19} else 3
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    image.save(output)


def step_buttons(steps: list[dict]) -> str:
    return "".join(
        f"""<button class="step" data-index="{step['index']}"
data-action="{html.escape(step['action'])}"
data-destination="{step['destination'][0]},{step['destination'][1]}"
data-collected="{str(step['collected_token']).lower()}"
data-unlocked="{html.escape(str(step['unlocked']))}">
<span>{step['index']}</span><strong>{html.escape(step['action'].title())}</strong>
</button>"""
        for step in steps
    )


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    actions = load_actions()
    training_count = result["data_boundary"]["training_action_frames"]
    level2_start = actions[17]["board"]
    heldout = actions[training_count - 1]["board"]
    planned_steps = result["planned"]["steps"]
    naive_steps = result["naive_ablation"]["steps"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    board_image(level2_start).save(OUTPUT_DIR / "training-level2.png")
    board_image(heldout).save(OUTPUT_DIR / "heldout-level3.png")
    render_route(heldout, planned_steps, OUTPUT_DIR / "planned-route.png")
    render_route(
        heldout,
        naive_steps,
        OUTPUT_DIR / "naive-failure.png",
        failure_step=4,
    )

    controls = result["learned_model"]["action_deltas"]
    lock_rows = "".join(
        f"""<tr><td>{row['token']}</td><td>{row['locked_neighbor']}</td></tr>"""
        for row in result["heldout_world"]["locks"]
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EXP-DUCK-029 Pixel Learning Audit</title>
<style>
:root {{
  color-scheme:dark; --bg:#101315; --panel:#181d20; --line:#3b474e;
  --text:#f4f6f7; --muted:#acb8bf; --blue:#58a6ff; --green:#54d19b;
  --yellow:#ffd166; --red:#ff7474; --pink:#e53aa3;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:16px/1.55 system-ui,sans-serif; }}
header,main {{ width:min(1240px,calc(100% - 32px)); margin:auto; }}
header {{ padding:40px 0 30px; }} h1 {{ margin:0 0 8px; font-size:clamp(2rem,5vw,4rem); letter-spacing:0; }}
h2,h3 {{ letter-spacing:0; }} p {{ color:var(--muted); }}
a {{ color:#83d7ff; }} code {{ color:var(--yellow); }}
.badges,.controls {{ display:flex; flex-wrap:wrap; gap:8px; }}
.badge,.control {{ border:1px solid var(--line); border-radius:4px; padding:7px 11px; }}
.pass {{ color:var(--green); }} .fail {{ color:var(--red); }} .warn {{ color:var(--yellow); }}
section {{ border-top:1px solid var(--line); padding:34px 0; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
.three {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }}
article {{ background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:16px; }}
figure {{ margin:0; }} img {{ width:100%; image-rendering:pixelated; border:1px solid var(--line); }}
figcaption {{ color:var(--muted); padding-top:7px; }}
.roles {{ display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin:18px 0; }}
.role {{ min-height:88px; border-top:5px solid; background:var(--panel); padding:12px; }}
.role strong,.role span {{ display:block; }} .role span {{ color:var(--muted); font-size:.9rem; }}
.blue {{ border-color:#1e93ff; }} .green {{ border-color:#4fcc30; }}
.red {{ border-color:#f93c31; }} .purple {{ border-color:#a356d6; }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); }}
th,td {{ text-align:left; border-bottom:1px solid var(--line); padding:9px; }}
.steps {{ display:grid; grid-template-columns:repeat(10,minmax(72px,1fr)); gap:7px; margin:18px 0; }}
.step {{ min-height:72px; color:var(--text); background:#22292e; border:1px solid #52616b; border-radius:4px; }}
.step span {{ display:block; color:var(--muted); }} .step:hover,.step.active {{ border-color:var(--yellow); background:#302d20; }}
.inspector {{ min-height:84px; background:var(--panel); border-left:4px solid var(--yellow); padding:14px; }}
.decision {{ border-left:4px solid var(--green); padding-left:16px; }}
@media(max-width:850px) {{
  .grid,.three,.roles {{ grid-template-columns:1fr; }}
  .steps {{ grid-template-columns:repeat(4,1fr); }}
}}
</style>
</head>
<body>
<header>
  <p><a href="../duck_tn36_model_learning_audit/index.html">Previous source-assisted planning audit</a></p>
  <h1>tu93: Learning the game from pictures</h1>
  <p>EXP-DUCK-029 trained on level 1-2 action frames, received only the initial
  level-3 picture, and planned without reading <code>tu93.py</code> or any
  level-3 action.</p>
  <div class="badges">
    <span class="badge pass">Pixel-only held-out gate: PASS</span>
    <span class="badge pass">Exact 19-action plan</span>
    <span class="badge">50 states explored</span>
    <span class="badge warn">Within-game transfer only</span>
    <span class="badge">Competition submission: NO</span>
  </div>
</header>
<main>
<section>
  <h2>What the learner discovered</h2>
  <div class="controls">
    <span class="control">Up {controls['UP']}</span>
    <span class="control">Down {controls['DOWN']}</span>
    <span class="control">Left {controls['LEFT']}</span>
    <span class="control">Right {controls['RIGHT']}</span>
    <span class="control">Grid step: 6 pixels</span>
  </div>
  <div class="roles">
    <div class="role blue"><strong>Blue piece</strong><span>Color 9: the moving player</span></div>
    <div class="role green"><strong>Green square</strong><span>Color 14: the final target</span></div>
    <div class="role red"><strong>Red switches</strong><span>Color 8: collect all three</span></div>
    <div class="role purple"><strong>Purple marker</strong><span>Color 15: points to a locked neighbor</span></div>
  </div>
  <div class="grid">
    <figure><img src="training-level2.png" alt="Level 2 training frame"><figcaption>Training evidence: level 2</figcaption></figure>
    <figure><img src="heldout-level3.png" alt="Held-out level 3 initial frame"><figcaption>Held-out input: only this initial level-3 picture</figcaption></figure>
  </div>
</section>
<section>
  <div class="grid">
    <div>
      <h2>The crucial lock rule</h2>
      <p>A purple pixel inside each red switch points to a neighboring node.
      That neighbor is dangerous until its switch is collected.</p>
      <table><thead><tr><th>Red switch</th><th>Locked neighbor</th></tr></thead>
      <tbody>{lock_rows}</tbody></table>
    </div>
    <figure><img src="planned-route.png" alt="Learned 19-action route"><figcaption>Green line: generated route. Large yellow points mark switches and the target.</figcaption></figure>
  </div>
  <h3>Inspect every planned action</h3>
  <div class="steps">{step_buttons(planned_steps)}</div>
  <div class="inspector" id="inspector">Select an action to see its predicted destination and whether it unlocks another cell.</div>
</section>
<section>
  <h2>Why the simpler model was rejected</h2>
  <div class="grid">
    <figure><img src="naive-failure.png" alt="Naive route failure"><figcaption>The red point is step 4: the naive route enters a locked cell and gets GAME_OVER.</figcaption></figure>
    <article>
      <p class="fail"><strong>Naive graph: REJECTED</strong></p>
      <p>It treated every visible corridor as immediately safe and proposed
      {len(naive_steps)} actions. The black-box game disagreed at the still-locked
      node.</p>
      <p class="pass"><strong>Lock-aware graph: ACCEPTED</strong></p>
      <p>It collected switches in dependency order and exactly matched all
      {len(planned_steps)} actions of the successful live replay.</p>
    </article>
  </div>
</section>
<section>
  <h2>Decision</h2>
  <p class="decision">We have proven pixel-only transfer between levels of the
  same game. We have not yet proven transfer to a different game family. The
  next gate should apply the architecture - control learning, role discovery,
  dependency parsing, planning, and prediction checks - to a second game
  without game-specific color constants.</p>
</section>
</main>
<script>
document.querySelectorAll(".step").forEach(button => {{
  button.addEventListener("click", () => {{
    document.querySelectorAll(".step").forEach(item => item.classList.remove("active"));
    button.classList.add("active");
    const collected = button.dataset.collected === "true";
    const detail = collected
      ? ` It collects a red switch and unlocks ${{button.dataset.unlocked}}.`
      : "";
    document.querySelector("#inspector").textContent =
      `Step ${{button.dataset.index}}: ${{button.dataset.action}} to (${{button.dataset.destination}}).${{detail}}`;
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
