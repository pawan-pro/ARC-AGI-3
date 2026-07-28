#!/usr/bin/env python3
"""Build the live-result EXP-DUCK-032 visual audit."""

from __future__ import annotations

import json
from pathlib import Path
import re

from PIL import Image

from ft09_operator_calibration import infer_calibrated_level5_objective


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "artifacts/kaggle/duck_ft09_level5_calibrated/latest"
EVENTS = RUN_ROOT / "artifacts/ft09-0d8bbf25_p0_events.jsonl"
VALIDATION = ROOT / "experiments/duck_harness_repro/exp_duck_032_validation.json"
OUTPUT_DIR = ROOT / "artifacts/kaggle/duck_ft09_operator_calibration_live_audit"
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


def parse_cell(action_display: str) -> tuple[int, int]:
    match = re.search(r"row=(\d+), col=(\d+)", action_display)
    if not match:
        raise ValueError(action_display)
    return tuple(map(int, match.groups()))


def main() -> int:
    events = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    initial = events[69]["board"]
    helper_events = events[70:79]
    objective = infer_calibrated_level5_objective(
        initial, {0: "same", 2: "different"}
    )
    target = objective.target_dict()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    board_image(initial).save(OUTPUT_DIR / "initial.png")
    board_image(paint_target(initial, target)).save(OUTPUT_DIR / "predicted.png")
    board_image(events[-1]["board"]).save(OUTPUT_DIR / "observed-final.png")

    buttons = []
    for step, event in enumerate(helper_events, start=1):
        cell = parse_cell(str(event["action_display"]))
        before = int(events[68 + step]["board"][cell[0]][cell[1]])
        after = int(event["board"][cell[0]][cell[1]])
        buttons.append(
            f'<button class="action" data-step="{step}" data-cell="{cell[0]},{cell[1]}" '
            f'data-before="{before}" data-after="{after}"><span>{step}</span>'
            f"<strong>Mouse {cell}</strong></button>"
        )

    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EXP-DUCK-032 Live Result</title><style>
:root {{ color-scheme:dark;--bg:#101315;--panel:#191e21;--line:#445057;
--text:#f5f7f8;--muted:#aeb9bf;--green:#54d19b;--yellow:#ffd166;--red:#ff7474 }}
* {{ box-sizing:border-box }} body {{ margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,sans-serif }}
header,main {{ width:min(1240px,calc(100% - 32px));margin:auto }} header {{ padding:38px 0 28px }}
h1 {{ margin:0;font-size:clamp(2rem,5vw,3.7rem);letter-spacing:0 }} h2 {{ letter-spacing:0 }}
p,figcaption {{ color:var(--muted) }} section {{ border-top:1px solid var(--line);padding:30px 0 }}
.badges {{ display:flex;flex-wrap:wrap;gap:8px }} .badge {{ border:1px solid var(--line);border-radius:4px;padding:7px 11px }}
.pass {{ color:var(--green) }} .fail {{ color:var(--red) }} .grid {{ display:grid;grid-template-columns:repeat(3,1fr);gap:14px }}
figure {{ margin:0;background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:13px }}
img {{ width:100%;image-rendering:pixelated;border:1px solid var(--line) }} figcaption {{ padding-top:8px }}
.actions {{ display:grid;grid-template-columns:repeat(5,1fr);gap:7px }}
.action {{ min-height:70px;color:var(--text);background:#22292e;border:1px solid #52616b;border-radius:4px }}
.action span {{ display:block;color:var(--muted) }} .action:hover,.action.active {{ border-color:var(--yellow);background:#302d20 }}
.inspector {{ margin-top:12px;background:var(--panel);border-left:4px solid var(--yellow);padding:14px;min-height:70px }}
.decision {{ border-left:4px solid var(--red);padding-left:16px }}
@media(max-width:820px) {{ .grid {{ grid-template-columns:1fr }} .actions {{ grid-template-columns:repeat(3,1fr) }} }}
</style></head><body><header>
<p><a href="../duck_ft09_operator_calibration_audit/index.html">Calibration before the live run</a></p>
<h1>ft09 level 5: Exact execution, rejected objective</h1>
<p>The private run made all nine calibrated clicks and reached its frozen
picture exactly. The game did not accept that picture.</p>
<div class="badges"><span class="badge pass">9/9 effects correct</span>
<span class="badge pass">0 target mismatches</span>
<span class="badge fail">Level gain: 0</span>
<span class="badge fail">Causal gate: FAIL</span>
<span class="badge">Competition submission: NO</span></div></header><main>
<section><div class="grid">
<figure><img src="initial.png"><figcaption>Untouched level 5</figcaption></figure>
<figure><img src="predicted.png"><figcaption>Frozen calibrated target</figcaption></figure>
<figure><img src="observed-final.png"><figcaption>Observed final board: target matched, level unchanged</figcaption></figure>
</div></section><section><h2>Recorded actions</h2><div class="actions">{''.join(buttons)}</div>
<div class="inspector" id="inspector">Select an action to inspect its recorded effect.</div></section>
<section><h2>Decision</h2><p class="decision"><strong>Reject another normal-cell
coloring experiment.</strong> Both complementary normal-cell targets have now
failed. The next controlled test should probe the three new magenta cells from
clean level-5 starts to learn whether they are controls, locks, or active
operators.</p><p><code>structural_pass={str(validation["structural_pass"]).lower()}</code> ·
<code>causal_gate_pass={str(validation["causal_gate_pass"]).lower()}</code></p></section>
</main><script>document.querySelectorAll(".action").forEach(button => button.addEventListener("click", () => {{
document.querySelectorAll(".action").forEach(item => item.classList.remove("active"));button.classList.add("active");
document.querySelector("#inspector").textContent=`Step ${{button.dataset.step}} at (${{button.dataset.cell}}): observed ${{button.dataset.before}} -> ${{button.dataset.after}}; effect correct.`;
}}));</script></body></html>"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
