#!/usr/bin/env python3
"""Post-plan black-box validation for EXP-DUCK-029.

The official source is loaded only here, after both pixel-derived plans exist.
It is never imported by the learner or planning gate.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import arcengine

from tu93_pixel_world_model import learn_visual_model, plan_world


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_tu93_level3_route/latest/artifacts"
    / "tu93-0768757b_p0_events.jsonl"
)
DEFAULT_OUTPUT = (
    ROOT
    / "experiments/duck_harness_repro/exp_duck_029_black_box_validation.json"
)
ACTION_IDS = {
    "UP": arcengine.GameAction.ACTION1,
    "DOWN": arcengine.GameAction.ACTION2,
    "LEFT": arcengine.GameAction.ACTION3,
    "RIGHT": arcengine.GameAction.ACTION4,
}


def load_game(source: Path) -> type:
    spec = importlib.util.spec_from_file_location("exp_duck_029_validator", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Tu93


def execute(game_class: type, actions: tuple[str, ...]) -> dict:
    game = game_class()
    game.set_level(2)
    rows = []
    for index, action in enumerate(actions, start=1):
        frame = game.perform_action(arcengine.ActionInput(id=ACTION_IDS[action]))
        rows.append(
            {
                "step": index,
                "action": action,
                "state": frame.state.value,
                "level": int(game.level_index + 1),
            }
        )
        if frame.state.value in {"GAME_OVER", "WIN"} or game.level_index > 2:
            break
    return {
        "steps_executed": len(rows),
        "terminal_state": rows[-1]["state"],
        "final_level": rows[-1]["level"],
        "trace": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    events = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("type") == "action"
    ]
    training = events[:28]
    model = learn_visual_model(training)
    correct = plan_world(training[-1]["board"], model, use_marker_locks=True)
    naive = plan_world(training[-1]["board"], model, use_marker_locks=False)
    if correct.actions is None or naive.actions is None:
        raise SystemExit("FAIL: planner did not produce both validation candidates")

    game_class = load_game(args.source)
    correct_result = execute(game_class, correct.actions)
    naive_result = execute(game_class, naive.actions)
    checks = {
        "correct_plan_advanced": correct_result["final_level"] == 4,
        "correct_plan_exactly_19_actions": correct_result["steps_executed"] == 19,
        "naive_plan_game_over": naive_result["terminal_state"] == "GAME_OVER",
        "naive_failure_at_step_4": naive_result["steps_executed"] == 4,
    }
    result = {
        "experiment": "EXP-DUCK-029",
        "validator_boundary": (
            "official engine loaded after pixel learner produced both plans"
        ),
        "correct": correct_result,
        "naive": naive_result,
        "checks": checks,
        "structural_pass": all(checks.values()),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["structural_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
