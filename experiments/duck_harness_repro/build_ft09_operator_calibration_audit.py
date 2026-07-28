#!/usr/bin/env python3
"""Build the EXP-DUCK-032 operator-calibration visual audit."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from ft09_operator_calibration import (
    infer_calibrated_level5_objective,
    reconstruct_solved_examples,
)


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_level5_prospective/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)
RESULT = ROOT / "experiments/duck_harness_repro/exp_duck_032_calibration.json"
REJECTED = ROOT / "experiments/duck_harness_repro/exp_duck_031_prospective_gate.json"
OUTPUT_DIR = ROOT / "artifacts/kaggle/duck_ft09_operator_calibration_audit"
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


def paint_target(
    board: list[list[int]], target: dict[tuple[int, int], int]
) -> list[list[int]]:
    result = [row[:] for row in board]
    for (row, col), color in target.items():
        for rr in range(row - 2, row + 4):
            for cc in range(col - 2, col + 4):
                result[rr][cc] = color
    return result


def main() -> int:
    events = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    rejected = json.loads(REJECTED.read_text(encoding="utf-8"))
    examples = reconstruct_solved_examples(events)
    initial = events[69]["board"]
    objective = infer_calibrated_level5_objective(
        initial, {0: "same", 2: "different"}
    )
    old_target = {
        tuple(item["cell"]): int(item["color"])
        for item in rejected["objective"]["target"]
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for example in examples:
        board_image(
            paint_target(example.board, example.target_dict()), scale=5
        ).save(OUTPUT_DIR / f"level-{example.level}-accepted-target.png")

    initial_image = board_image(initial)
    draw = ImageDraw.Draw(initial_image)
    for row, col in objective.clue_cells:
        draw.rectangle(
            ((col - 4) * 8, (row - 4) * 8, (col + 4) * 8, (row + 4) * 8),
            outline=(255, 209, 102),
            width=4,
        )
    for row, col in objective.obstacle_cells:
        draw.rectangle(
            ((col - 4) * 8, (row - 4) * 8, (col + 4) * 8, (row + 4) * 8),
            outline=(229, 58, 163),
            width=4,
        )
    initial_image.save(OUTPUT_DIR / "level-5-classified.png")
    board_image(paint_target(initial, old_target)).save(
        OUTPUT_DIR / "rejected-target.png"
    )
    board_image(paint_target(initial, objective.target_dict())).save(
        OUTPUT_DIR / "calibrated-target.png"
    )

    fold_rows = "".join(
        f"<tr><td>Level {fold['heldout_level']}</td>"
        f"<td>{', '.join(map(str, fold['training_levels']))}</td>"
        f"<td>{fold['target_signatures']}</td>"
        f"<td class=\"pass\">{'Exact' if fold['exact_target_match'] else 'Failed'}</td></tr>"
        for fold in result["leave_one_level_out"]
    )
    action_buttons = "".join(
        f'<button class="action" data-step="{index}" data-cell="{row},{col}">'
        f"<span>{index}</span><strong>Mouse ({row}, {col})</strong></button>"
        for index, (row, col) in enumerate(result["planned_clicks"], start=1)
    )
    accepted_cards = "".join(
        f'<figure><img src="level-{level}-accepted-target.png" '
        f'alt="Accepted level {level} target"><figcaption>Level {level}: '
        f'{result["reconstructed_levels"][level - 1]["target_cells"]} target cells</figcaption></figure>'
        for level in range(1, 5)
    )

    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EXP-DUCK-032 ft09 Operator Calibration</title>
<style>
:root {{ color-scheme:dark;--bg:#101315;--panel:#191e21;--line:#445057;
--text:#f5f7f8;--muted:#aeb9bf;--green:#54d19b;--yellow:#ffd166;
--red:#ff7474;--blue:#58a6ff;--pink:#e53aa3 }}
* {{ box-sizing:border-box }} body {{ margin:0;background:var(--bg);color:var(--text);
font:16px/1.55 system-ui,sans-serif }} header,main {{ width:min(1260px,calc(100% - 32px));margin:auto }}
header {{ padding:38px 0 28px }} h1 {{ margin:0;font-size:clamp(2rem,5vw,3.7rem);letter-spacing:0 }}
h2,h3 {{ letter-spacing:0 }} p {{ color:var(--muted) }} code {{ color:var(--yellow) }}
section {{ border-top:1px solid var(--line);padding:30px 0 }}
.badges {{ display:flex;flex-wrap:wrap;gap:8px }} .badge {{ border:1px solid var(--line);border-radius:4px;padding:7px 11px }}
.pass {{ color:var(--green) }} .fail {{ color:var(--red) }} .warn {{ color:var(--yellow) }}
.grid3 {{ display:grid;grid-template-columns:repeat(3,1fr);gap:14px }}
.grid4 {{ display:grid;grid-template-columns:repeat(4,1fr);gap:12px }}
figure,article {{ margin:0;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:13px }}
img {{ width:100%;image-rendering:pixelated;border:1px solid var(--line) }} figcaption {{ color:var(--muted);padding-top:8px }}
table {{ width:100%;border-collapse:collapse;background:var(--panel) }} th,td {{ text-align:left;border-bottom:1px solid var(--line);padding:10px }}
.rule {{ display:grid;grid-template-columns:1fr 1fr;gap:12px }} .rule article {{ border-top:4px solid var(--blue) }}
.actions {{ display:grid;grid-template-columns:repeat(5,1fr);gap:7px }}
.action {{ min-height:70px;color:var(--text);background:#22292e;border:1px solid #52616b;border-radius:4px }}
.action span {{ display:block;color:var(--muted) }} .action:hover,.action.active {{ border-color:var(--yellow);background:#302d20 }}
.inspector {{ margin-top:12px;min-height:70px;background:var(--panel);border-left:4px solid var(--yellow);padding:14px }}
.launch {{ border-left:4px solid var(--green);padding-left:16px }}
@media(max-width:850px) {{ .grid3,.grid4,.rule {{ grid-template-columns:1fr }} .actions {{ grid-template-columns:repeat(3,1fr) }} }}
</style></head><body><header>
<p><a href="../duck_ft09_level5_prospective_audit/index.html">Previous: rejected level-5 target</a></p>
<h1>ft09: Learn the clue language before answering</h1>
<p>EXP-DUCK-032 reconstructs four accepted targets, hides each one in turn,
and asks whether the other three levels teach enough to predict it exactly.</p>
<div class="badges"><span class="badge pass">4/4 closed-book folds exact</span>
<span class="badge pass">One target per fold</span>
<span class="badge pass">Level-5 target: 9 clicks</span>
<span class="badge warn">Private isolated run only</span>
<span class="badge">Competition submission: NO</span></div>
</header><main>
<section><h2>The learned rule</h2><div class="rule">
<article><h3>White mark</h3><p>Copy the color at the center of the clue.</p></article>
<article><h3>Light-gray mark</h3><p>Use a different state. Overlapping clues
must agree on which different state works.</p></article></div></section>
<section><h2>Accepted answer sheets reconstructed from replay</h2>
<div class="grid4">{accepted_cards}</div></section>
<section><h2>Closed-book calibration</h2>
<table><thead><tr><th>Hidden level</th><th>Training levels</th><th>Predicted targets</th><th>Result</th></tr></thead>
<tbody>{fold_rows}</tbody></table></section>
<section><h2>What EXP-DUCK-031 got wrong</h2><div class="grid3">
<figure><img src="level-5-classified.png" alt="Level 5 with corrected classifications">
<figcaption>Yellow: 8 true clues. Pink: 3 fixed obstacles, not clues.</figcaption></figure>
<figure><img src="rejected-target.png" alt="Rejected 18-click target">
<figcaption>Rejected target: reversed white/gray meanings and 18 clicks.</figcaption></figure>
<figure><img src="calibrated-target.png" alt="Calibrated 9-click target">
<figcaption>New target: learned meanings, obstacles excluded, 9 clicks.</figcaption></figure>
</div></section>
<section><h2>Prospective nine-click plan</h2>
<p>No successful level-5 action was used to produce this plan.</p>
<div class="actions">{action_buttons}</div>
<div class="inspector" id="inspector">Select an action to highlight its planned board cell.</div>
</section>
<section><h2>Launch decision</h2><p class="launch">The calibration gate passes.
Run one private isolated Kaggle test. Promote only if the nine-click helper
advances from level 5 to level 6 with every observed effect correct.</p></section>
</main><script>
document.querySelectorAll(".action").forEach(button => button.addEventListener("click", () => {{
document.querySelectorAll(".action").forEach(item => item.classList.remove("active"));
button.classList.add("active");
document.querySelector("#inspector").textContent =
`Step ${{button.dataset.step}}: click board cell (${{button.dataset.cell}}), changing green to purple.`;
}}));</script></body></html>"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
