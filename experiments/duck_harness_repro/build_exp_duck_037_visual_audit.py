#!/usr/bin/env python3
"""Build a self-contained visual audit for EXP-DUCK-037."""

from __future__ import annotations

import html
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE.parent))

from duck_harness_repro.bounded_reasoning_loop import (
    MechanicsMemory,
    ReasoningContext,
    board_mismatches,
    board_sha256,
)
from duck_harness_repro.three_action_objective_gate import (
    ThreeActionObjectiveController,
    ThresholdFeedbackHypothesis,
)


ROOT = Path(__file__).resolve().parents[2]
RUN_ROOT = ROOT / "artifacts/kaggle/duck_ft09_all_three_objective/latest"
MEMORY_PATH = PACKAGE / "exp_duck_034_mechanics_memory.json"
TRACE_PATH = RUN_ROOT / "exp_duck_037_objective_trace.json"
EVENTS_PATH = RUN_ROOT / "artifacts/ft09-0d8bbf25_p0_events.jsonl"
OUTPUT_PATH = RUN_ROOT / "visual_audit.html"


def load_action_boards(path: Path) -> dict[int, list[list[int]]]:
    boards: dict[int, list[list[int]]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        action_num = event.get("action_num")
        if event.get("type") == "action" and isinstance(action_num, int):
            boards[action_num] = event["board"]
    return boards


def reconstruct() -> dict[str, object]:
    trace = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
    boards = load_action_boards(EVENTS_PATH)
    initial = boards[69]
    if board_sha256(initial) != trace["initial_sha256"]:
        raise RuntimeError("Initial action-69 board does not match the trace")

    feedback = trace["feedback_hypothesis"]
    controller = ThreeActionObjectiveController(
        memory=MechanicsMemory.load(MEMORY_PATH),
        context=ReasoningContext("ft09", "ft09-0d8bbf25", 5),
        initial_board=initial,
        action_order=tuple(trace["action_order"]),
        feedback=ThresholdFeedbackHypothesis(
            point=tuple(feedback["point"]),
            inactive_value=int(feedback["inactive_value"]),
            active_value=int(feedback["active_value"]),
            activation_threshold=int(feedback["activation_threshold"]),
        ),
    )

    current = initial
    steps: list[dict[str, object]] = []
    for record in trace["records"]:
        index = int(record["step"])
        planned = controller.next_action(current)
        if planned is None or planned.index != index:
            raise RuntimeError(f"Could not reconstruct planned action {index}")
        observed = boards[69 + index]
        level_completed = bool(record.get("level_completed"))
        mismatches = board_mismatches(planned.predicted_board, observed)
        if not level_completed and record.get("prediction_check") == "match" and mismatches:
            raise RuntimeError(f"Action {index} unexpectedly has {len(mismatches)} mismatches")
        if board_sha256(observed) != record["observed_sha256"]:
            raise RuntimeError(f"Action {index} event board does not match trace")

        changed = [
            [row, col]
            for row in range(64)
            for col in range(64)
            if current[row][col] != observed[row][col]
        ]
        controller.observe(
            observed,
            level_completed=level_completed,
            game_over=bool(record.get("game_over")),
            run_complete=bool(record.get("run_complete")),
        )
        steps.append(
            {
                "index": index,
                "rule_id": planned.rule_id,
                "action": {"row": planned.row, "col": planned.col},
                "before": current,
                "predicted": [list(row) for row in planned.predicted_board],
                "observed": observed,
                "changed": changed,
                "changed_count": len(changed),
                "mismatch_count": len(mismatches),
                "mismatches": [list(item) for item in mismatches],
                "corner_before": current[63][63],
                "corner_predicted": planned.predicted_board[63][63],
                "corner_observed": observed[63][63],
                "prediction_check": record["prediction_check"],
                "level_completed": level_completed,
            }
        )
        current = observed

    if controller.stop_reason != trace["stop_reason"]:
        raise RuntimeError("Reconstructed stop reason differs from trace")
    if controller.objective_supported != trace["objective_supported"]:
        raise RuntimeError("Reconstructed objective decision differs from trace")

    if trace["stop_reason"] == "objective_completed":
        conclusion = (
            "SUPPORTED: clicks one and two matched exactly, and activating the "
            "third control advanced the game to level 6."
        )
    elif trace["stop_reason"] == "objective_falsified_no_transition":
        conclusion = (
            "FALSIFIED: all three exact action effects occurred, but the game "
            "remained on level 5. No further action was taken."
        )
    else:
        conclusion = (
            f"STOPPED SAFELY: {trace['stop_reason']}. No action beyond the "
            "recorded evidence was taken."
        )
    return {
        "initial": initial,
        "initial_corner": initial[63][63],
        "action_order": trace["action_order"],
        "stop_reason": trace["stop_reason"],
        "objective_supported": trace["objective_supported"],
        "steps": steps,
        "conclusion": conclusion,
    }


CSS = """
:root { color-scheme: dark; --bg:#0d1117; --panel:#151b23; --line:#303844;
  --text:#f0f4f8; --muted:#aeb8c4; --good:#63d6a4; --warn:#f1bd62; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:15px/1.45 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  letter-spacing:0; }
main { max-width:1320px; margin:0 auto; padding:24px; }
h1 { margin:0 0 6px; font-size:28px; font-weight:500; }
h2 { margin:0; font-size:19px; font-weight:500; }
p { margin:6px 0; } .muted { color:var(--muted); }
.summary { display:flex; flex-wrap:wrap; gap:12px 24px; margin:16px 0 20px; }
.summary span { color:var(--muted); } .summary strong { color:var(--text); }
.step { border-top:1px solid var(--line); padding:20px 0; }
.step-head { display:flex; flex-wrap:wrap; justify-content:space-between;
  align-items:baseline; gap:8px 20px; margin-bottom:10px; }
.corner { color:var(--warn); }
.boards { display:grid; grid-template-columns:repeat(4,minmax(180px,1fr)); gap:12px; }
figure { margin:0; padding:10px; border:1px solid var(--line); border-radius:6px;
  background:var(--panel); }
figcaption { color:var(--muted); margin-bottom:8px; }
canvas { display:block; width:100%; aspect-ratio:1; image-rendering:pixelated; }
.result { color:var(--good); font-size:18px; font-weight:500; margin-top:20px; }
@media(max-width:900px){.boards{grid-template-columns:repeat(2,minmax(150px,1fr));}}
@media(max-width:520px){main{padding:16px}.boards{grid-template-columns:1fr}}
"""


JS = """
const palette=["#f4f4f4","#1768ac","#8b939c","#4caf50","#171b20",
"#6f4cac","#d84a9b","#ed7831","#ee3d46","#20252b","#7b5d45",
"#ffd83d","#f09a30","#7fd8ee","#b8c5cf","#b92875"];
function drawBoard(canvas,board){const ctx=canvas.getContext("2d");canvas.width=256;
canvas.height=256;for(let r=0;r<64;r++){for(let c=0;c<64;c++){
ctx.fillStyle=palette[board[r][c]]||"#ff00ff";ctx.fillRect(c*4,r*4,4,4);}}}
function drawDiff(canvas,observed,changed){const ctx=canvas.getContext("2d");
canvas.width=256;canvas.height=256;ctx.fillStyle="#0b0f14";ctx.fillRect(0,0,256,256);
for(const [r,c] of changed){ctx.fillStyle=palette[observed[r][c]]||"#ff00ff";
ctx.fillRect(c*4,r*4,4,4);ctx.strokeStyle="#fff";ctx.strokeRect(c*4+.5,r*4+.5,3,3);}}
document.querySelectorAll("[data-board]").forEach(c=>drawBoard(c,JSON.parse(c.dataset.board)));
document.querySelectorAll("[data-diff]").forEach(c=>drawDiff(c,
JSON.parse(c.dataset.observed),JSON.parse(c.dataset.diff)));
"""


def attr(value: object) -> str:
    return html.escape(json.dumps(value, separators=(",", ":")), quote=True)


def render(data: dict[str, object]) -> str:
    steps: list[str] = []
    for step in data["steps"]:
        if step["level_completed"]:
            transition_note = (
                "Intended level transition; pixel equality is not expected."
            )
        elif step["mismatches"]:
            details = ", ".join(
                f"({row},{col}) expected {expected}, observed {observed}"
                for row, col, expected, observed in step["mismatches"]
            )
            transition_note = f"Exact-board mismatch: {details}."
        else:
            transition_note = f"Exact-board check: {step['prediction_check']}."
        steps.append(f"""
<section class="step">
  <div class="step-head">
    <h2>Click {step['index']}: {html.escape(str(step['rule_id']))} at
      ({step['action']['row']}, {step['action']['col']})</h2>
    <p class="corner">Corner {step['corner_before']} -> predicted
      {step['corner_predicted']} -> observed {step['corner_observed']}</p>
  </div>
  <p class="muted">{html.escape(transition_note)}</p>
  <div class="boards">
    <figure><figcaption>Before click</figcaption><canvas data-board="{attr(step['before'])}"></canvas></figure>
    <figure><figcaption>Predicted board</figcaption><canvas data-board="{attr(step['predicted'])}"></canvas></figure>
    <figure><figcaption>Observed board</figcaption><canvas data-board="{attr(step['observed'])}"></canvas></figure>
    <figure><figcaption>Observed change mask: {step['changed_count']} pixels</figcaption>
      <canvas data-observed="{attr(step['observed'])}" data-diff="{attr(step['changed'])}"></canvas></figure>
  </div>
</section>""")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EXP-DUCK-037 Objective Confirmation</title><style>{CSS}</style></head>
<body><main><h1>EXP-DUCK-037: All-Three Objective Confirmation</h1>
<p class="muted">Fresh isolated ft09 level-five arm. Exactly three added clicks; no runtime LLM.</p>
<div class="summary"><span>Order <strong>{html.escape(' -> '.join(data['action_order']))}</strong></span>
<span>Start corner <strong>{data['initial_corner']}</strong></span><span>Budget <strong>3 clicks</strong></span>
<span>Stop <strong>{html.escape(str(data['stop_reason']))}</strong></span></div>
<figure><figcaption>Initial level-five board after validated 69-action prefix</figcaption>
<canvas data-board="{attr(data['initial'])}"></canvas></figure>
{''.join(steps)}<p class="result">{html.escape(str(data['conclusion']))}</p>
</main><script>{JS}</script></body></html>"""


def main() -> int:
    data = reconstruct()
    OUTPUT_PATH.write_text(render(data), encoding="utf-8")
    print(OUTPUT_PATH)
    print(json.dumps({
        "stop_reason": data["stop_reason"],
        "objective_supported": data["objective_supported"],
        "steps": len(data["steps"]),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
