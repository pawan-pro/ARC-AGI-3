#!/usr/bin/env python3
"""Validate the live prospective EXP-DUCK-031 result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ft09_level5_objective_model import infer_level5_objective


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = ROOT / "artifacts/kaggle/duck_ft09_level5_prospective/latest"
DEFAULT_OUTPUT = (
    ROOT / "experiments/duck_harness_repro/exp_duck_031_validation.json"
)


def read_events(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_root", nargs="?", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    benchmark = json.loads(
        (args.candidate_root / "benchmark.json").read_text(encoding="utf-8")
    )
    run = benchmark["game_runs"][0]
    events = read_events(
        args.candidate_root / "artifacts/ft09-0d8bbf25_p0_events.jsonl"
    )
    level5_initial = events[69]
    helper_events = events[70:88]
    objective = infer_level5_objective(level5_initial["board"])
    target = objective.target_dict()
    planned = list(objective.clicks(level5_initial["board"]))

    observed_cells = [
        (int(event["action_display"].split("row=")[1].split(",")[0]),
         int(event["action_display"].split("col=")[1].split(")")[0]))
        for event in helper_events
    ]
    effect_checks = [
        int(event["board"][row][col]) == target[(row, col)]
        for event, (row, col) in zip(helper_events, observed_cells)
    ]
    final_board = events[-1]["board"]
    final_mismatches = [
        list(cell)
        for cell, color in target.items()
        if int(final_board[cell[0]][cell[1]]) != color
    ]

    checks = {
        "one_ft09_game": len(benchmark["game_runs"]) == 1
        and str(run["game_id"]).startswith("ft09-"),
        "validated_prefix_reached_level5": int(level5_initial["level"]) == 5
        and int(level5_initial["action_num"]) == 69,
        "actions_per_level_exact": run["actions_per_level"]
        == [9, 7, 32, 21, 18, 0],
        "zero_tokens": int(run["final_generated_tokens"]) == 0
        and int(run["final_uncached_input_tokens"]) == 0,
        "objective_shape_exact": len(objective.normal_cells) == 27
        and len(objective.clue_cells) == 11
        and len(objective.semantic_models) == 2,
        "one_target_signature": len(objective.target) == 27,
        "eighteen_helper_actions": len(helper_events) == 18,
        "live_actions_match_frozen_plan": observed_cells == planned,
        "every_observed_effect_correct": all(effect_checks),
        "final_board_matches_frozen_target": not final_mismatches,
        "no_game_over": not any(bool(event["game_over"]) for event in helper_events),
        "level5_did_not_advance": int(run["levels_completed"]) == 4
        and int(events[-1]["level"]) == 5
        and not any(bool(event["level_completed"]) for event in helper_events),
    }
    structural_pass = all(checks.values())
    prospective_gate_pass = (
        structural_pass
        and int(run["levels_completed"]) >= 5
        and any(bool(event["level_completed"]) for event in helper_events)
    )
    result = {
        "experiment": "EXP-DUCK-031",
        "structural_pass": structural_pass,
        "prospective_gate_pass": prospective_gate_pass,
        "recommended_full_evaluation": prospective_gate_pass,
        "decision": "REJECT_OBJECTIVE_HYPOTHESIS",
        "reason": (
            "The executor reproduced every planned state change and the final board "
            "matched the frozen target, but the game remained on level 5."
        ),
        "metrics": {
            "levels_completed": run["levels_completed"],
            "actions_per_level": run["actions_per_level"],
            "total_actions": len(run["history"]),
            "generated_tokens": run["final_generated_tokens"],
            "uncached_input_tokens": run["final_uncached_input_tokens"],
            "normal_cells": len(objective.normal_cells),
            "clue_cells": len(objective.clue_cells),
            "semantic_models": len(objective.semantic_models),
            "target_signatures": 1,
            "planned_helper_actions": len(planned),
            "executed_helper_actions": len(helper_events),
            "correct_observed_effects": sum(effect_checks),
            "final_target_mismatches": len(final_mismatches),
        },
        "checks": checks,
        "solver_note": run["solver_note"],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if structural_pass and not prospective_gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
