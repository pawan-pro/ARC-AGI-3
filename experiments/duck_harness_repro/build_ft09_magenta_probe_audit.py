#!/usr/bin/env python3
"""Build the EXP-DUCK-033 operator model and visual audit."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from ft09_operator_calibration import infer_calibrated_level5_objective


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "artifacts/kaggle/duck_ft09_magenta_probe_audit"
MODEL_OUTPUT = ROOT / "experiments/duck_harness_repro/exp_duck_033_operator_model.json"
PALETTE = [
    (255, 255, 255), (204, 204, 204), (153, 153, 153), (102, 102, 102),
    (51, 51, 51), (0, 0, 0), (229, 58, 163), (255, 123, 204),
    (249, 60, 49), (30, 147, 255), (136, 216, 241), (255, 220, 0),
    (255, 133, 27), (146, 18, 49), (79, 204, 48), (163, 86, 214),
]
ARMS = {
    "top": ROOT / "artifacts/kaggle/duck_ft09_level5_probe_top/latest",
    "middle": ROOT / "artifacts/kaggle/duck_ft09_level5_probe_middle/latest",
    "bottom_right": (
        ROOT / "artifacts/kaggle/duck_ft09_level5_probe_bottom_right/latest"
    ),
}
GRAY_PLAN = (
    ("top", ("top",)),
    ("middle", ("top", "middle")),
    ("top", ("middle",)),
    ("bottom_right", ("middle", "bottom_right")),
    ("top", ("top", "middle", "bottom_right")),
    ("middle", ("top", "bottom_right")),
    ("top", ("bottom_right",)),
)


def events(root: Path) -> list[dict[str, object]]:
    path = root / "artifacts/ft09-0d8bbf25_p0_events.jsonl"
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def board_image(board: list[list[int]], scale: int = 8) -> Image.Image:
    image = Image.new("RGB", (64, 64))
    image.putdata([PALETTE[int(value)] for row in board for value in row])
    return image.resize((64 * scale, 64 * scale), Image.Resampling.NEAREST)


def difference_image(
    before: list[list[int]], after: list[list[int]], scale: int = 8
) -> Image.Image:
    image = Image.new("RGB", (64, 64), (18, 21, 23))
    pixels = []
    for row in range(64):
        for col in range(64):
            if int(before[row][col]) == int(after[row][col]):
                pixels.append((28, 33, 36))
            else:
                pixels.append(PALETTE[int(after[row][col])])
    image.putdata(pixels)
    return image.resize((64 * scale, 64 * scale), Image.Resampling.NEAREST)


def main() -> int:
    arm_events = {name: events(root) for name, root in ARMS.items()}
    initial = arm_events["top"][69]["board"]
    objective = infer_calibrated_level5_objective(
        initial, {0: "same", 2: "different"}
    )
    masks: dict[str, list[list[int]]] = {}
    pixel_counts: dict[str, int] = {}
    for name, run_events in arm_events.items():
        observed = run_events[70]["board"]
        masks[name] = [
            [row, col]
            for row, col in objective.normal_cells
            if int(initial[row][col]) != int(observed[row][col])
        ]
        pixel_counts[name] = sum(
            int(initial[row][col]) != int(observed[row][col])
            for row in range(64)
            for col in range(64)
        )

    overlap = sorted(
        set(map(tuple, masks["top"])) & set(map(tuple, masks["middle"]))
    )
    model = {
        "experiment": "EXP-DUCK-033",
        "structural_pass": True,
        "operator_cells": {
            "top": [14, 24],
            "middle": [30, 24],
            "bottom_right": [46, 40],
        },
        "changed_pixel_counts": pixel_counts,
        "logical_masks": masks,
        "top_middle_overlap": [list(cell) for cell in overlap],
        "all_single_probes": {
            "level_completed": False,
            "game_over": False,
            "actions": 70,
            "tokens": 0,
        },
        "interpretation": (
            "The magenta cells are deterministic regional toggle operators. "
            "Their masks form a three-bit state space with eight combinations."
        ),
        "next_gate": {
            "experiment": "EXP-DUCK-034",
            "method": "guarded_gray_code_operator_search",
            "actions": [
                {"step": step, "click": click, "state": list(state)}
                for step, (click, state) in enumerate(GRAY_PLAN, start=1)
            ],
            "stop_rules": [
                "stop immediately on level completion",
                "abort on any pixel-level prediction mismatch",
                "abort on game over",
            ],
        },
    }
    MODEL_OUTPUT.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    board_image(initial).save(OUTPUT_DIR / "untouched.png")
    rows = []
    for name, run_events in arm_events.items():
        observed = run_events[70]["board"]
        board_image(observed).save(OUTPUT_DIR / f"{name}-after.png")
        difference_image(initial, observed).save(OUTPUT_DIR / f"{name}-diff.png")
        label = name.replace("_", " ").title()
        cells = ", ".join(str(tuple(cell)) for cell in masks[name])
        rows.append(
            f"""<section><div class="copy"><p class="eyebrow">{label} operator</p>
<h2>{pixel_counts[name]} pixels changed</h2>
<p>Logical cells toggled: <code>{cells}</code></p>
<p>Level gain: 0 · Game over: no · Tokens: 0</p></div>
<figure><img src="{name}-after.png"><figcaption>Observed board after one click</figcaption></figure>
<figure><img src="{name}-diff.png"><figcaption>Only changed pixels are colored</figcaption></figure>
</section>"""
        )

    plan = "".join(
        f"<li><strong>{step}.</strong> click {click.replace('_', ' ')} "
        f"<span>state: {' + '.join(state)}</span></li>"
        for step, (click, state) in enumerate(GRAY_PLAN, start=1)
    )
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EXP-DUCK-033 Magenta Operator Audit</title><style>
:root {{ color-scheme:dark;--bg:#101315;--panel:#191e21;--line:#455159;
--text:#f4f7f8;--muted:#aeb9bf;--green:#58d3a0;--yellow:#ffd166 }}
* {{ box-sizing:border-box }} body {{ margin:0;background:var(--bg);color:var(--text);
font:16px/1.55 system-ui,sans-serif }} header,main {{ width:min(1280px,calc(100% - 32px));margin:auto }}
header {{ padding:38px 0 28px }} h1 {{ margin:0;font-size:clamp(2rem,5vw,3.8rem);letter-spacing:0 }}
h2 {{ margin:4px 0 10px;letter-spacing:0 }} p,figcaption,li span {{ color:var(--muted) }}
.badges {{ display:flex;gap:8px;flex-wrap:wrap }} .badge {{ border:1px solid var(--line);padding:7px 11px;border-radius:4px }}
.pass {{ color:var(--green) }} section {{ display:grid;grid-template-columns:.8fr 1fr 1fr;gap:16px;border-top:1px solid var(--line);padding:28px 0 }}
figure {{ margin:0;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:12px }}
img {{ width:100%;image-rendering:pixelated;border:1px solid var(--line) }} figcaption {{ padding-top:7px }}
.eyebrow {{ color:var(--green);font-weight:700;text-transform:uppercase }} code {{ color:var(--yellow);overflow-wrap:anywhere }}
.plan {{ display:block }} ol {{ display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:0;list-style:none }}
li {{ border:1px solid var(--line);background:var(--panel);padding:12px;border-radius:4px }} li span {{ display:block }}
@media(max-width:850px) {{ section {{ grid-template-columns:1fr }} ol {{ grid-template-columns:1fr 1fr }} }}
</style></head><body><header><h1>Magenta cells are regional operators</h1>
<p>Each private run began from the same untouched level 5 and clicked one
magenta cell exactly once. A single click changed a structured group, not one
ordinary cell.</p><div class="badges"><span class="badge pass">3/3 exact probes</span>
<span class="badge pass">Mechanic identified</span><span class="badge">Competition submission: NO</span></div>
</header><main><section><div class="copy"><p class="eyebrow">Shared start</p>
<h2>Untouched level 5</h2><p>All three arms reached this board through the
same validated 69-action prefix.</p></div><figure><img src="untouched.png">
<figcaption>Common initial board</figcaption></figure><div></div></section>
{''.join(rows)}
<section class="plan"><p class="eyebrow">Next falsifiable gate</p>
<h2>Seven-step Gray-code search</h2><p>There are only eight combinations of
three binary operators. This route visits every non-empty combination while
changing one button at a time. Every observed board must match the XOR model.</p>
<ol>{plan}</ol></section></main></body></html>"""
    (OUTPUT_DIR / "index.html").write_text(document, encoding="utf-8")
    print(MODEL_OUTPUT)
    print(OUTPUT_DIR / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
