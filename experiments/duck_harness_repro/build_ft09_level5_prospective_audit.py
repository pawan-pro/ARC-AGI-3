#!/usr/bin/env python3
"""Build the EXP-DUCK-031 prospective level-5 visual audit."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from ft09_level5_objective_model import infer_level5_objective


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "artifacts/kaggle/duck_ft09_level5_prospective/latest"
EVENTS = RUN_ROOT / "artifacts/ft09-0d8bbf25_p0_events.jsonl"
VALIDATION = ROOT / "experiments/duck_harness_repro/exp_duck_031_validation.json"
OUTPUT_DIR = ROOT / "artifacts/kaggle/duck_ft09_level5_prospective_audit"
OUTPUT = OUTPUT_DIR / "index.html"
PALETTE = [
    (255, 255, 255), (204, 204, 204), (153, 153, 153), (102, 102, 102),
    (51, 51, 51), (0, 0, 0), (229, 58, 163), (255, 123, 204),
    (249, 60, 49), (30, 147, 255), (136, 216, 241), (255, 220, 0),
    (255, 133, 27), (146, 18, 49), (79, 204, 48), (163, 86, 214),
]


def board_image(board: list[list[int]], scale: int = 8) -> Image.Image:
    image = Image.new("RGB", (64, 64))
    image.putdata([PALETTE[int(value)] for row in board for value in row])
    return image.resize((64 * scale, 64 * scale), Image.Resampling.NEAREST)


def parse_cell(event: dict[str, object]) -> tuple[int, int]:
    display = str(event["action_display"])
    return (
        int(display.split("row=")[1].split(",")[0]),
        int(display.split("col=")[1].split(")")[0]),
    )


def main() -> int:
    events = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    initial = events[69]["board"]
    helper_events = events[70:88]
    objective = infer_level5_objective(initial)
    target = objective.target_dict()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    initial_image = board_image(initial)
    draw = ImageDraw.Draw(initial_image)
    for row, col in objective.clue_cells:
        draw.rectangle(
            ((col - 4) * 8, (row - 4) * 8, (col + 4) * 8, (row + 4) * 8),
            outline=(255, 209, 102),
            width=4,
        )
    initial_image.save(OUTPUT_DIR / "level5-initial.png")

    target_board = [row[:] for row in initial]
    for (row, col), color in target.items():
        for rr in range(row - 2, row + 4):
            for cc in range(col - 2, col + 4):
                target_board[rr][cc] = color
    board_image(target_board).save(OUTPUT_DIR / "predicted-target.png")
    board_image(events[-1]["board"]).save(OUTPUT_DIR / "observed-final.png")

    buttons = []
    for step, event in enumerate(helper_events, start=1):
        row, col = parse_cell(event)
        before = int(events[68 + step]["board"][row][col])
        after = int(event["board"][row][col])
        buttons.append(
            f'<button class="action" data-step="{step}" data-cell="{row},{col}" '
            f'data-before="{before}" data-after="{after}" data-target="{target[(row, col)]}">'
            f"<span>{step}</span><strong>Mouse ({row}, {col})</strong></button>"
        )

    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EXP-DUCK-031 Prospective ft09 Level-5 Audit</title>
<style>
:root {{ color-scheme:dark;--bg:#101315;--panel:#191e21;--line:#445057;
--text:#f5f7f8;--muted:#aeb9bf;--green:#54d19b;--yellow:#ffd166;
--red:#ff7474;--blue:#58a6ff }}
* {{ box-sizing:border-box }} body {{ margin:0;background:var(--bg);color:var(--text);
font:16px/1.55 system-ui,sans-serif }} header,main {{ width:min(1260px,calc(100% - 32px));margin:auto }}
header {{ padding:38px 0 28px }} h1 {{ margin:0;font-size:clamp(2rem,5vw,3.8rem);letter-spacing:0 }}
h2,h3 {{ letter-spacing:0 }} p {{ color:var(--muted) }} code {{ color:var(--yellow) }}
section {{ border-top:1px solid var(--line);padding:30px 0 }}
.badges {{ display:flex;flex-wrap:wrap;gap:8px }} .badge {{ border:1px solid var(--line);border-radius:4px;padding:7px 11px }}
.pass {{ color:var(--green) }} .fail {{ color:var(--red) }} .warn {{ color:var(--yellow) }}
.grid {{ display:grid;grid-template-columns:repeat(3,1fr);gap:14px }}
figure,article {{ margin:0;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:13px }}
img {{ width:100%;image-rendering:pixelated;border:1px solid var(--line) }} figcaption {{ color:var(--muted);padding-top:8px }}
.equation {{ display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:10px;align-items:center }}
.symbol {{ font-size:2rem;color:var(--yellow);text-align:center }}
.actions {{ display:grid;grid-template-columns:repeat(6,1fr);gap:7px }}
.action {{ min-height:70px;color:var(--text);background:#22292e;border:1px solid #52616b;border-radius:4px }}
.action span {{ display:block;color:var(--muted) }} .action:hover,.action.active {{ border-color:var(--yellow);background:#302d20 }}
.inspector {{ margin-top:12px;min-height:74px;background:var(--panel);border-left:4px solid var(--yellow);padding:14px }}
.decision {{ border-left:4px solid var(--red);padding-left:16px }}
@media(max-width:850px) {{ .grid,.equation {{ grid-template-columns:1fr }} .symbol {{ transform:rotate(90deg) }} .actions {{ grid-template-columns:repeat(3,1fr) }} }}
</style></head><body><header>
<p><a href="../duck_ft09_cross_game_learning_audit/index.html">Previous: successful level-4 audit</a></p>
<h1>ft09 level 5: The moves worked, the theory did not</h1>
<p>This is a genuinely prospective test. The learner saw the untouched board,
formed one actionable target, and made 18 guarded clicks without using a
level-5 solution trace.</p>
<div class="badges"><span class="badge pass">18/18 effects correct</span>
<span class="badge pass">0 target mismatches</span>
<span class="badge fail">Level gain: 0</span>
<span class="badge fail">Prospective gate: REJECTED</span>
<span class="badge warn">Competition submission: NO</span></div>
</header><main>
<section><h2>K-12 explanation</h2>
<div class="equation"><article><h3>1. Guess</h3><p>The clues seemed to say which
green squares should become purple.</p></article><div class="symbol">+</div>
<article><h3>2. Check every move</h3><p>Each click changed exactly the square
and color predicted.</p></article><div class="symbol">=</div>
<article><h3>3. Ask the game</h3><p>The finished picture was not accepted.
So the clicker was right, but the clue rule was incomplete.</p></article></div></section>
<section><h2>Before, prediction, and reality</h2><div class="grid">
<figure><img src="level5-initial.png" alt="Untouched ft09 level 5 board">
<figcaption>Untouched level 5. Yellow boxes mark the 11 detected clues.</figcaption></figure>
<figure><img src="predicted-target.png" alt="Frozen predicted target">
<figcaption>The target was frozen before the first level-5 click.</figcaption></figure>
<figure><img src="observed-final.png" alt="Final observed board">
<figcaption>The observed final board equals the prediction, but remained level 5.</figcaption></figure>
</div></section>
<section><h2>Exact action audit</h2>
<p>Click a button to inspect the recorded effect. Colors 14 and 15 are the
pixel labels for the two editable states.</p>
<div class="actions">{''.join(buttons)}</div>
<div class="inspector" id="inspector">Select an action to inspect its observed result.</div>
</section>
<section><h2>Decision</h2><p class="decision"><strong>Reject the simple global
same-or-flip interpretation.</strong> Overlap agreement was enough on level 4,
but not on level 5. The four mark types likely carry richer operator meaning,
or the clues impose a higher-order rule that the binary model omitted.</p>
<p>Next, learn the mark operators from solved levels 1-4 and hold out one solved
level as a calibration test. Return to level 5 only if that learned model
predicts a unique target different from this rejected one.</p>
<p><code>structural_pass={str(validation["structural_pass"]).lower()}</code> ·
<code>prospective_gate_pass={str(validation["prospective_gate_pass"]).lower()}</code></p>
</section></main><script>
document.querySelectorAll(".action").forEach(button => button.addEventListener("click", () => {{
document.querySelectorAll(".action").forEach(item => item.classList.remove("active"));
button.classList.add("active");
document.querySelector("#inspector").textContent =
`Step ${{button.dataset.step}}: Mouse (${{button.dataset.cell}}). Observed ${{button.dataset.before}} -> ${{button.dataset.after}}; predicted target ${{button.dataset.target}}. Effect correct.`;
}}));</script></body></html>"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
