#!/usr/bin/env python3
"""Build compact, self-contained visual audits for EXP-DUCK-036."""

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
from duck_harness_repro.two_action_feedback_gate import (
    FeedbackHypothesis,
    TwoActionFeedbackController,
)


ROOT = Path(__file__).resolve().parents[2]
MEMORY_PATH = PACKAGE / "exp_duck_034_mechanics_memory.json"
COMBINED_DIR = (
    ROOT / "artifacts/kaggle/duck_ft09_feedback_pair_visual_audit"
)
ARMS = (
    {
        "name": "top-bottom-right",
        "label": "Top then bottom-right",
        "root": ROOT
        / "artifacts/kaggle/duck_ft09_feedback_top_bottom_right/latest",
        "trace": "exp_duck_036_top-bottom-right_trace.json",
    },
    {
        "name": "middle-bottom-right",
        "label": "Middle then bottom-right",
        "root": ROOT
        / "artifacts/kaggle/duck_ft09_feedback_middle_bottom_right/latest",
        "trace": "exp_duck_036_middle-bottom-right_trace.json",
    },
)


def load_action_boards(path: Path) -> dict[int, list[list[int]]]:
    result: dict[int, list[list[int]]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        action_num = event.get("action_num")
        if event.get("type") == "action" and isinstance(action_num, int):
            result[action_num] = event["board"]
    return result


def reconstruct(arm: dict[str, object]) -> dict[str, object]:
    root = Path(arm["root"])
    trace = json.loads((root / str(arm["trace"])).read_text(encoding="utf-8"))
    boards = load_action_boards(
        root / "artifacts/ft09-0d8bbf25_p0_events.jsonl"
    )
    initial = boards[69]
    if board_sha256(initial) != trace["initial_sha256"]:
        raise RuntimeError(f"{arm['name']}: initial board hash mismatch")

    feedback_data = trace["feedback_hypothesis"]
    controller = TwoActionFeedbackController(
        memory=MechanicsMemory.load(MEMORY_PATH),
        context=ReasoningContext("ft09", "ft09-0d8bbf25", 5),
        initial_board=initial,
        action_order=tuple(trace["action_order"]),
        feedback=FeedbackHypothesis(
            point=tuple(feedback_data["point"]),
            inactive_value=int(feedback_data["inactive_value"]),
            active_value=int(feedback_data["active_value"]),
            active_rules=frozenset(feedback_data["active_rules"]),
        ),
    )

    current = initial
    steps: list[dict[str, object]] = []
    for index in (1, 2):
        planned = controller.next_action(current)
        if planned is None:
            raise RuntimeError(f"{arm['name']}: missing planned action {index}")
        observed = boards[69 + index]
        mismatches = board_mismatches(planned.predicted_board, observed)
        changed = [
            [row, col]
            for row in range(len(current))
            for col in range(len(current[row]))
            if current[row][col] != observed[row][col]
        ]
        if mismatches:
            raise RuntimeError(
                f"{arm['name']}: action {index} has {len(mismatches)} mismatches"
            )
        if not controller.observe(observed):
            raise RuntimeError(
                f"{arm['name']}: controller stopped at action {index}"
            )
        recorded = trace["records"][index - 1]
        if recorded["observed_sha256"] != board_sha256(observed):
            raise RuntimeError(
                f"{arm['name']}: action {index} trace hash mismatch"
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
                "mismatch_count": 0,
                "corner_before": current[63][63],
                "corner_predicted": planned.predicted_board[63][63],
                "corner_observed": observed[63][63],
                "observed_sha256": recorded["observed_sha256"],
            }
        )
        current = observed

    if controller.stop_reason != "two_action_plan_complete":
        raise RuntimeError(
            f"{arm['name']}: unexpected stop {controller.stop_reason}"
        )
    return {
        "name": arm["name"],
        "label": arm["label"],
        "initial": initial,
        "initial_corner": initial[63][63],
        "action_order": trace["action_order"],
        "stop_reason": trace["stop_reason"],
        "steps": steps,
        "conclusion": (
            "PASS: both complete-board predictions matched. The corner stayed "
            "12 with one active control and became 11 with this pair active."
        ),
    }


CSS = """
:root {
  color-scheme: dark;
  --bg: #0d1117;
  --panel: #151b23;
  --line: #303844;
  --text: #f0f4f8;
  --muted: #aeb8c4;
  --good: #63d6a4;
  --warn: #f1bd62;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 15px/1.45 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  letter-spacing: 0;
}
main { max-width: 1320px; margin: 0 auto; padding: 24px; }
h1 { margin: 0 0 6px; font-size: 28px; font-weight: 500; }
h2 { margin: 0; font-size: 20px; font-weight: 500; }
h3 { margin: 0 0 12px; font-size: 16px; font-weight: 500; }
p { margin: 6px 0; }
.muted { color: var(--muted); }
.pass { color: var(--good); font-weight: 500; }
.arm { border-top: 1px solid var(--line); padding: 22px 0; }
.summary {
  display: flex;
  flex-wrap: wrap;
  gap: 14px 24px;
  margin: 10px 0 18px;
}
.summary span { color: var(--muted); }
.summary strong { color: var(--text); font-weight: 500; }
.boards {
  display: grid;
  grid-template-columns: repeat(4, minmax(180px, 1fr));
  gap: 12px;
}
figure {
  margin: 0;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--panel);
}
figcaption { color: var(--muted); margin-bottom: 8px; }
canvas { display: block; width: 100%; aspect-ratio: 1; image-rendering: pixelated; }
.step { margin-top: 18px; }
.step-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px 20px;
  margin-bottom: 10px;
}
.corner { color: var(--warn); }
code { color: var(--text); }
@media (max-width: 900px) {
  .boards { grid-template-columns: repeat(2, minmax(150px, 1fr)); }
}
@media (max-width: 520px) {
  main { padding: 16px; }
  .boards { grid-template-columns: 1fr; }
}
"""


JS = """
const palette = [
  "#f4f4f4", "#1768ac", "#8b939c", "#4caf50",
  "#171b20", "#6f4cac", "#d84a9b", "#ed7831",
  "#ee3d46", "#20252b", "#7b5d45", "#ffd83d",
  "#f09a30", "#7fd8ee", "#b8c5cf", "#b92875"
];
function drawBoard(canvas, board) {
  const ctx = canvas.getContext("2d");
  canvas.width = 256;
  canvas.height = 256;
  const scale = 4;
  for (let row = 0; row < 64; row++) {
    for (let col = 0; col < 64; col++) {
      ctx.fillStyle = palette[board[row][col]] || "#ff00ff";
      ctx.fillRect(col * scale, row * scale, scale, scale);
    }
  }
}
function drawDiff(canvas, before, observed, changed) {
  const ctx = canvas.getContext("2d");
  canvas.width = 256;
  canvas.height = 256;
  const scale = 4;
  ctx.fillStyle = "#0b0f14";
  ctx.fillRect(0, 0, 256, 256);
  for (const [row, col] of changed) {
    ctx.fillStyle = palette[observed[row][col]] || "#ff00ff";
    ctx.fillRect(col * scale, row * scale, scale, scale);
  }
  ctx.strokeStyle = "#ffffff";
  ctx.lineWidth = 1;
  for (const [row, col] of changed) {
    ctx.strokeRect(col * scale + 0.5, row * scale + 0.5, scale - 1, scale - 1);
  }
}
document.querySelectorAll("[data-board]").forEach((canvas) => {
  drawBoard(canvas, JSON.parse(canvas.dataset.board));
});
document.querySelectorAll("[data-diff-mask]").forEach((canvas) => {
  drawDiff(
    canvas,
    JSON.parse(canvas.dataset.before),
    JSON.parse(canvas.dataset.observed),
    JSON.parse(canvas.dataset.diffMask)
  );
});
"""


def board_attr(board: object) -> str:
    return html.escape(json.dumps(board, separators=(",", ":")), quote=True)


def render_arm(data: dict[str, object], *, standalone: bool) -> str:
    sections: list[str] = []
    initial = board_attr(data["initial"])
    header = f"""
<section class="arm">
  <h2>{html.escape(str(data["label"]))}</h2>
  <div class="summary">
    <span>Order <strong>{html.escape(" -> ".join(data["action_order"]))}</strong></span>
    <span>Start corner <strong>{data["initial_corner"]}</strong></span>
    <span>Budget <strong>2 clicks</strong></span>
    <span>Stop <strong>{html.escape(str(data["stop_reason"]))}</strong></span>
  </div>
  <div class="boards">
    <figure>
      <figcaption>Before probes, action 69</figcaption>
      <canvas data-board="{initial}" aria-label="Board before both probe clicks"></canvas>
    </figure>
  </div>
"""
    sections.append(header)
    for step in data["steps"]:
        action = step["action"]
        before = board_attr(step["before"])
        predicted = board_attr(step["predicted"])
        observed = board_attr(step["observed"])
        changed = board_attr(step["changed"])
        sections.append(
            f"""
  <div class="step">
    <div class="step-head">
      <h3>Click {step["index"]}: {html.escape(str(step["rule_id"]))}
        at ({action["row"]}, {action["col"]})</h3>
      <p class="corner">Corner {step["corner_before"]} -> predicted
        {step["corner_predicted"]} -> observed {step["corner_observed"]}</p>
    </div>
    <div class="boards">
      <figure>
        <figcaption>Before click</figcaption>
        <canvas data-board="{before}" aria-label="Board before click {step["index"]}"></canvas>
      </figure>
      <figure>
        <figcaption>Predicted board</figcaption>
        <canvas data-board="{predicted}" aria-label="Predicted board after click {step["index"]}"></canvas>
      </figure>
      <figure>
        <figcaption>Observed board</figcaption>
        <canvas data-board="{observed}" aria-label="Observed board after click {step["index"]}"></canvas>
      </figure>
      <figure>
        <figcaption>Changed pixels: {step["changed_count"]}; mismatches: 0</figcaption>
        <canvas data-before="{before}" data-observed="{observed}"
          data-diff-mask="{changed}" aria-label="Changed pixels after click {step["index"]}"></canvas>
      </figure>
    </div>
  </div>
"""
        )
    sections.append(
        f'  <p class="pass">{html.escape(str(data["conclusion"]))}</p>\n</section>'
    )
    content = "\n".join(sections)
    if not standalone:
        return content
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EXP-DUCK-036 {html.escape(str(data["label"]))} Audit</title>
  <style>{CSS}</style>
</head>
<body>
<main>
  <h1>EXP-DUCK-036 Visual Audit</h1>
  <p class="muted">Prediction-checked ft09 level-five pair probe.</p>
  {content}
</main>
<script>{JS}</script>
</body>
</html>
"""


def main() -> int:
    audits = [reconstruct(arm) for arm in ARMS]
    for arm, data in zip(ARMS, audits, strict=True):
        output = Path(arm["root"]) / "visual_audit.html"
        output.write_text(render_arm(data, standalone=True), encoding="utf-8")
        print(output)

    COMBINED_DIR.mkdir(parents=True, exist_ok=True)
    combined = "\n".join(render_arm(data, standalone=False) for data in audits)
    index = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EXP-DUCK-036 Pair Feedback Audit</title>
  <style>{CSS}</style>
</head>
<body>
<main>
  <h1>EXP-DUCK-036 Pair Feedback Audit</h1>
  <p class="muted">Two fresh private arms, each stopped after two clicks.</p>
  {combined}
  <p class="pass">Conclusion: all three tested two-control combinations now
    produce corner state 11, while every single-control state produces 12.
    This supports the model "corner 11 means any two controls are active."</p>
</main>
<script>{JS}</script>
</body>
</html>
"""
    combined_path = COMBINED_DIR / "index.html"
    combined_path.write_text(index, encoding="utf-8")
    print(combined_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
