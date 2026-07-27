#!/usr/bin/env python3
"""Run the EXP-DUCK-030 source-hidden ft09 objective-learning gate."""

from __future__ import annotations

import json
from pathlib import Path
import re

from ft09_pixel_objective_model import choose_next_click, infer_objective


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_level4_overlap/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)
OUTPUT = ROOT / "experiments/duck_harness_repro/exp_duck_030_cross_game_gate.json"


def parse_cell(action_display: str) -> tuple[int, int]:
    match = re.search(r"row=(\d+), col=(\d+)", action_display)
    if not match:
        raise ValueError(action_display)
    return tuple(map(int, match.groups()))


def main() -> int:
    events = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("type") == "action"
    ]
    boundary = next(
        index
        for index, event in enumerate(events)
        if int(event.get("level") or 0) == 4 and bool(event.get("level_completed"))
    )
    training = events[:boundary]
    heldout_initial = events[boundary]["board"]

    # The complete target is frozen before any successful level-4 action is read.
    model = infer_objective(training, heldout_initial)
    current_board = heldout_initial
    decisions = []
    validation_events = events[boundary + 1 :]
    for step, event in enumerate(validation_events, start=1):
        predicted = choose_next_click(current_board, model)
        actual = parse_cell(str(event["action_display"]))
        decisions.append(
            {
                "step": step,
                "predicted": list(predicted) if predicted else None,
                "actual": list(actual),
                "matched": predicted == actual,
                "before_color": (
                    int(current_board[predicted[0]][predicted[1]])
                    if predicted
                    else None
                ),
                "target_color": (
                    model.target_dict()[predicted] if predicted else None
                ),
                "after_color": int(event["board"][actual[0]][actual[1]]),
                "level_advanced": bool(event.get("level_completed")),
            }
        )
        current_board = event["board"]

    learner_source = Path(__file__).with_name(
        "ft09_pixel_objective_model.py"
    ).read_text(encoding="utf-8")
    target_reached = bool(
        decisions
        and decisions[-1]["matched"]
        and decisions[-1]["level_advanced"]
    )
    wrong_hypothesis_count = next(
        count
        for mark, count in model.hypothesis_counts
        if mark != model.center_mark
    )
    checks = {
        "heldout_actions_hidden_during_objective_inference": boundary == len(training),
        "no_stored_board_coordinates": all(
            token not in learner_source
            for token in ("(16, 14)", "(24, 22)", "(40, 30)", "(48, 38)")
        ),
        "no_stored_color_roles": all(
            token not in learner_source
            for token in ("BLUE =", "RED =", "ORANGE =", "WHITE =", "GRAY =")
        ),
        "geometry_discovered": (
            len(model.normal_cells) == 18
            and len(model.clue_cells) == 3
            and model.spacing == 8
        ),
        "objective_unique": dict(model.hypothesis_counts)[model.center_mark] == 1,
        "wrong_mask_hypothesis_rejected": wrong_hypothesis_count == 0,
        "closed_loop_actions_match": all(row["matched"] for row in decisions),
        "exactly_21_actions": len(decisions) == 21,
        "target_reached": target_reached,
        "live_replay_advanced_to_level_5": bool(
            validation_events and validation_events[-1].get("level_completed")
        ),
    }
    result = {
        "experiment": "EXP-DUCK-030",
        "method": "source-hidden pixel objective inference plus closed-loop control",
        "data_boundary": {
            "training_levels": [1, 2, 3],
            "training_action_frames": len(training),
            "heldout_level": 4,
            "heldout_success_actions_available_to_objective_model": 0,
            "heldout_control_feedback": (
                "one observed board after each action selected by the frozen objective"
            ),
        },
        "model": model.to_dict(),
        "decisions": decisions,
        "validation": {
            "actions": len(decisions),
            "all_actions_matched": all(row["matched"] for row in decisions),
            "target_reached": target_reached,
            "advanced_to_level": int(validation_events[-1]["level"]),
        },
        "ablations": {
            "wrong_mask_role_solutions": wrong_hypothesis_count,
            "without_overlap_candidates": 2 ** len(model.clue_cells),
            "interpretation": (
                "Local clues alone leave eight assignments. Requiring shared cells "
                "to agree reduces the correct interpretation to one and the reversed "
                "interpretation to zero."
            ),
        },
        "checks": checks,
        "structural_pass": all(checks.values()),
        "competition_submit": False,
        "decision": (
            "Accept a second, non-navigation family as source-hidden model-based "
            "transfer. Next test the same hypothesis-first protocol prospectively "
            "on an unsolved level before integrating it into a full notebook."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["structural_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
