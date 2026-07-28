#!/usr/bin/env python3
"""Validate the live EXP-DUCK-032 calibrated level-5 result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from ft09_operator_calibration import infer_calibrated_level5_objective


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = ROOT / "artifacts/kaggle/duck_ft09_level5_calibrated/latest"
DEFAULT_OUTPUT = (
    ROOT / "experiments/duck_harness_repro/exp_duck_032_validation.json"
)


def parse_cell(action_display: str) -> tuple[int, int]:
    match = re.search(r"row=(\d+), col=(\d+)", action_display)
    if not match:
        raise ValueError(action_display)
    return tuple(map(int, match.groups()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_root", nargs="?", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    benchmark = json.loads(
        (args.candidate_root / "benchmark.json").read_text(encoding="utf-8")
    )
    run = benchmark["game_runs"][0]
    events = [
        json.loads(line)
        for line in (
            args.candidate_root / "artifacts/ft09-0d8bbf25_p0_events.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    initial = events[69]["board"]
    helper_events = events[70:79]
    objective = infer_calibrated_level5_objective(
        initial, {0: "same", 2: "different"}
    )
    target = objective.target_dict()
    planned = list(objective.clicks(initial))
    observed = [parse_cell(str(event["action_display"])) for event in helper_events]
    effects = [
        int(event["board"][cell[0]][cell[1]]) == target[cell]
        for event, cell in zip(helper_events, observed)
    ]
    final = events[-1]["board"]
    mismatches = [
        list(cell)
        for cell, color in target.items()
        if int(final[cell[0]][cell[1]]) != color
    ]
    note = str(run["solver_note"])
    checks = {
        "one_ft09_game": len(benchmark["game_runs"]) == 1
        and str(run["game_id"]).startswith("ft09-"),
        "validated_prefix_reached_level5": int(events[69]["action_num"]) == 69
        and int(events[69]["level"]) == 5,
        "actions_per_level_exact": run["actions_per_level"]
        == [9, 7, 32, 21, 9, 0],
        "zero_tokens": int(run["final_generated_tokens"]) == 0
        and int(run["final_uncached_input_tokens"]) == 0,
        "calibrated_geometry_exact": len(objective.normal_cells) == 27
        and len(objective.clue_cells) == 8
        and len(objective.obstacle_cells) == 3
        and len(objective.uncovered_cells) == 1,
        "two_action_equivalent_unknown_models": len(
            objective.unknown_role_models
        ) == 2,
        "nine_helper_actions": len(helper_events) == 9,
        "live_actions_match_frozen_plan": observed == planned,
        "every_observed_effect_correct": all(effects),
        "final_board_matches_calibrated_target": not mismatches,
        "no_game_over": not any(bool(event["game_over"]) for event in helper_events),
        "level5_did_not_advance": int(run["levels_completed"]) == 4
        and int(events[-1]["level"]) == 5
        and not any(bool(event["level_completed"]) for event in helper_events),
        "solver_note_exact": all(
            token in note
            for token in (
                "normal=27",
                "clues=8",
                "obstacles=3",
                "unknown_models=2",
                "uncovered=1",
                "planned=9",
                "executed=9",
                "effects_ok=True",
                "solved=False",
                "stop=target_exhausted",
            )
        ),
    }
    structural_pass = all(checks.values())
    causal_gate_pass = structural_pass and int(run["levels_completed"]) >= 5
    result = {
        "experiment": "EXP-DUCK-032",
        "structural_pass": structural_pass,
        "causal_gate_pass": causal_gate_pass,
        "recommended_full_evaluation": causal_gate_pass,
        "decision": "REJECT_CALIBRATED_LEVEL5_TARGET",
        "reason": (
            "All nine actions and state predictions were correct and the final "
            "board matched the calibrated target, but level 5 did not advance."
        ),
        "metrics": {
            "levels_completed": run["levels_completed"],
            "actions_per_level": run["actions_per_level"],
            "total_actions": len(run["history"]),
            "generated_tokens": run["final_generated_tokens"],
            "planned_helper_actions": len(planned),
            "executed_helper_actions": len(helper_events),
            "correct_observed_effects": sum(effects),
            "final_target_mismatches": len(mismatches),
        },
        "checks": checks,
        "solver_note": note,
        "next_gate": (
            "EXP-DUCK-033 should probe the three new magenta cells from clean "
            "level-5 starts. Do not test another normal-cell complement."
        ),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if structural_pass and not causal_gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
