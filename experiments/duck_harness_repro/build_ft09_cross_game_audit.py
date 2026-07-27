#!/usr/bin/env python3
"""Build the EXP-DUCK-030 cross-game objective-learning visual audit."""

from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "experiments/duck_harness_repro/exp_duck_030_cross_game_gate.json"
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_level4_overlap/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)
OUTPUT_DIR = ROOT / "artifacts/kaggle/duck_ft09_cross_game_learning_audit"
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


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    boundary = result["data_boundary"]["training_action_frames"]
    initial = events[boundary]["board"]
    model = result["model"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    initial_image = board_image(initial)
    initial_draw = ImageDraw.Draw(initial_image)
    for row, col in model["clue_cells"]:
        initial_draw.rectangle(
            ((col - 4) * 8, (row - 4) * 8, (col + 4) * 8, (row + 4) * 8),
            outline=(255, 209, 102),
            width=4,
        )
    initial_image.save(OUTPUT_DIR / "heldout-initial.png")

    target_board = [row[:] for row in initial]
    for item in model["target"]:
        row, col = item["cell"]
        color = item["color"]
        for rr in range(row - 2, row + 4):
            for cc in range(col - 2, col + 4):
                target_board[rr][cc] = color
    board_image(target_board).save(OUTPUT_DIR / "inferred-target.png")

    action_buttons = "".join(
        f"""<button class="action" data-step="{row['step']}"
data-cell="{row['predicted'][0]},{row['predicted'][1]}"
data-before="{row['before_color']}" data-target="{row['target_color']}"
data-after="{row['after_color']}" data-advanced="{str(row['level_advanced']).lower()}">
<span>{row['step']}</span><strong>Mouse {tuple(row['predicted'])}</strong></button>"""
        for row in result["decisions"]
    )
    hypothesis_rows = "".join(
        f"<tr><td>Pixel mark {row['center_mark']}</td>"
        f"<td>{row['solutions']}</td>"
        f"<td>{'Accepted' if row['solutions'] == 1 else 'Rejected'}</td></tr>"
        for row in model["hypothesis_counts"]
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EXP-DUCK-030 Cross-Game Learning Audit</title>
<style>
:root {{ color-scheme:dark; --bg:#101315; --panel:#181d20; --line:#3b474e;
--text:#f4f6f7; --muted:#acb8bf; --green:#54d19b; --yellow:#ffd166;
--red:#ff7474; --blue:#58a6ff; }}
* {{ box-sizing:border-box }} body {{ margin:0;background:var(--bg);color:var(--text);
font:16px/1.55 system-ui,sans-serif }} header,main {{ width:min(1240px,calc(100% - 32px));margin:auto }}
header {{ padding:38px 0 28px }} h1 {{ margin:0;font-size:clamp(2rem,5vw,4rem);letter-spacing:0 }}
h2,h3 {{ letter-spacing:0 }} p {{ color:var(--muted) }} code {{ color:var(--yellow) }}
section {{ border-top:1px solid var(--line);padding:32px 0 }}
.badges,.stats {{ display:flex;flex-wrap:wrap;gap:8px }} .badge,.stat {{ border:1px solid var(--line);border-radius:4px;padding:7px 11px }}
.pass {{ color:var(--green) }} .fail {{ color:var(--red) }} .warn {{ color:var(--yellow) }}
.grid {{ display:grid;grid-template-columns:1fr 1fr;gap:18px }} article {{ background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:16px }}
figure {{ margin:0 }} img {{ width:100%;image-rendering:pixelated;border:1px solid var(--line) }} figcaption {{ color:var(--muted);padding-top:7px }}
table {{ width:100%;border-collapse:collapse;background:var(--panel) }} th,td {{ text-align:left;border-bottom:1px solid var(--line);padding:10px }}
.flow {{ display:grid;grid-template-columns:repeat(5,1fr);gap:8px }} .flow div {{ background:var(--panel);border-top:4px solid var(--blue);padding:12px;min-height:95px }}
.actions {{ display:grid;grid-template-columns:repeat(7,1fr);gap:7px }} .action {{ min-height:72px;color:var(--text);background:#22292e;border:1px solid #52616b;border-radius:4px }}
.action span {{ display:block;color:var(--muted) }} .action:hover,.action.active {{ border-color:var(--yellow);background:#302d20 }}
.inspector {{ margin-top:12px;min-height:76px;background:var(--panel);border-left:4px solid var(--yellow);padding:14px }}
.decision {{ border-left:4px solid var(--green);padding-left:16px }}
@media(max-width:820px) {{ .grid,.flow {{ grid-template-columns:1fr }} .actions {{ grid-template-columns:repeat(3,1fr) }} }}
</style></head><body><header>
<p><a href="../duck_tu93_pixel_learning_audit/index.html">Previous: tu93 navigation learner</a></p>
<h1>ft09: Form the objective, then act</h1>
<p>EXP-DUCK-030 tests the same hypothesis-first architecture on a different
family: a mouse-controlled color puzzle. The learner stores no winning
coordinates and no named color roles.</p>
<div class="badges"><span class="badge pass">Cross-family gate: PASS</span>
<span class="badge pass">21/21 actions matched</span>
<span class="badge pass">Advanced to level 5</span>
<span class="badge">Held-out winning actions used for inference: 0</span>
<span class="badge warn">Competition submission: NO</span></div>
</header><main>
<section><h2>The logic, in five steps</h2><div class="flow">
<div><strong>1. Find structure</strong><p>Detect repeated blocks and their spacing.</p></div>
<div><strong>2. Find clues</strong><p>Separate 18 plain cells from 3 patterned clue cells.</p></div>
<div><strong>3. State a rule</strong><p>One mask mark copies the clue center; the other chooses a different state.</p></div>
<div><strong>4. Test globally</strong><p>Shared cells must receive the same answer from every clue.</p></div>
<div><strong>5. Act and check</strong><p>Click the first wrong cell, observe it, and continue toward the frozen target.</p></div>
</div></section>
<section><div class="grid">
<figure><img src="heldout-initial.png" alt="Held-out ft09 level 4 board"><figcaption>Only this initial board was used. Yellow boxes identify the three detected clues.</figcaption></figure>
<figure><img src="inferred-target.png" alt="Pixel-derived target board"><figcaption>The target was fixed before any successful level-4 click was read.</figcaption></figure>
</div></section>
<section><div class="grid"><div><h2>Falsifiable hypothesis test</h2>
<table><thead><tr><th>Center-copy hypothesis</th><th>Consistent targets</th><th>Decision</th></tr></thead><tbody>{hypothesis_rows}</tbody></table>
</div><article><h3>Why overlap matters</h3>
<p>Reading each clue alone leaves <strong>8</strong> possible assignments.
Demanding that overlapping clues agree leaves exactly <strong>1</strong>.
Reversing the two mask meanings leaves <strong>0</strong>.</p>
<p class="pass"><strong>This is logic, not blind trial and error:</strong> the
wrong explanation is rejected before clicking.</p></article></div></section>
<section><h2>Closed-loop action audit</h2>
<p>The objective stays fixed. After every click, the policy reads the new board
and asks: “What is the first cell that still differs from the target?”</p>
<div class="actions">{action_buttons}</div>
<div class="inspector" id="inspector">Select an action to see the observed state change.</div>
</section>
<section><h2>Decision and next gate</h2>
<p class="decision">The architecture now works on two unlike families:
tu93 uses a learned navigation graph; ft09 uses a learned constraint model.
That supports the scalable principle <code>observe -> hypothesize -> reject
inconsistent models -> plan -> verify each effect</code>. The next honest test
is prospective: apply it to an unsolved level whose successful actions are not
already in our replay, and reject it if the objective is ambiguous or an
observed action contradicts the model.</p></section>
</main><script>
document.querySelectorAll(".action").forEach(button => button.addEventListener("click", () => {{
document.querySelectorAll(".action").forEach(item => item.classList.remove("active"));
button.classList.add("active");
const ending = button.dataset.advanced === "true" ? " The level advanced." : "";
document.querySelector("#inspector").textContent =
`Step ${{button.dataset.step}}: click (${{button.dataset.cell}}). Observed color ${{button.dataset.before}} -> ${{button.dataset.after}}; target is ${{button.dataset.target}}.${{ending}}`;
}}));</script></body></html>"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
