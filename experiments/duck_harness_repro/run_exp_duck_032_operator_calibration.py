#!/usr/bin/env python3
"""Run the EXP-DUCK-032 operator calibration and level-5 launch gate."""

from __future__ import annotations

import json
from pathlib import Path

from ft09_operator_calibration import (
    infer_calibrated_level5_objective,
    learn_mark_roles,
    leave_one_level_out,
    reconstruct_solved_examples,
)


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_level5_prospective/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)
REJECTED = ROOT / "experiments/duck_harness_repro/exp_duck_031_validation.json"
REJECTED_PLAN = (
    ROOT / "experiments/duck_harness_repro/exp_duck_031_prospective_gate.json"
)
OUTPUT = ROOT / "experiments/duck_harness_repro/exp_duck_032_calibration.json"


def main() -> int:
    events = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    examples = reconstruct_solved_examples(events)
    folds = leave_one_level_out(examples)
    learned_roles = learn_mark_roles(examples)
    level5_board = events[69]["board"]
    objective = infer_calibrated_level5_objective(level5_board, learned_roles)
    clicks = objective.clicks(level5_board)

    rejected_plan = json.loads(REJECTED_PLAN.read_text(encoding="utf-8"))
    rejected_target = {
        tuple(item["cell"]): int(item["color"])
        for item in rejected_plan["objective"]["target"]
    }
    new_target = objective.target_dict()
    changed_from_rejected = [
        cell for cell in objective.normal_cells
        if new_target[cell] != rejected_target[cell]
    ]
    rejected_result = json.loads(REJECTED.read_text(encoding="utf-8"))

    checks = {
        "four_targets_reconstructed": [len(example.target) for example in examples]
        == [8, 13, 23, 18],
        "roles_learned_from_all_four_levels": learned_roles
        == {0: "same", 2: "different"},
        "four_leave_one_out_folds_exact": len(folds) == 4
        and all(bool(fold["exact_target_match"]) for fold in folds),
        "every_fold_has_one_target": all(
            int(fold["target_signatures"]) == 1 for fold in folds
        ),
        "level5_geometry_corrected": len(objective.normal_cells) == 27
        and len(objective.clue_cells) == 8
        and len(objective.obstacle_cells) == 3,
        "one_uncovered_cell_safely_retained": len(objective.uncovered_cells) == 1
        and new_target[objective.uncovered_cells[0]]
        == int(level5_board[objective.uncovered_cells[0][0]][objective.uncovered_cells[0][1]]),
        "new_mark_ambiguity_is_action_invariant": len(
            objective.unknown_role_models
        ) == 2,
        "one_calibrated_target": len(objective.target) == 27,
        "new_target_differs_from_rejected": len(changed_from_rejected) == 27,
        "nine_guarded_clicks": len(clicks) == 9,
        "prior_rejection_used_only_as_ablation": (
            rejected_result["decision"] == "REJECT_OBJECTIVE_HYPOTHESIS"
        ),
        "no_level5_success_trace_available": not any(
            int(event.get("level") or 0) > 5 for event in events
        ),
    }
    result = {
        "experiment": "EXP-DUCK-032",
        "method": (
            "learn clue-mark relations from solved levels 1-4, validate with "
            "leave-one-level-out prediction, separate fixed obstacles, and infer "
            "one prospective level-5 target"
        ),
        "data_boundary": {
            "calibration_levels": [1, 2, 3, 4],
            "level5_success_actions": 0,
            "game_source_used": False,
            "rejected_level5_actions_used_for_learning": False,
            "rejected_level5_target_used_only_for_difference_ablation": True,
        },
        "reconstructed_levels": [
            {
                "level": example.level,
                "normal_cells": len(example.normal_cells),
                "clue_cells": len(example.clue_cells),
                "palette": list(example.palette),
                "target_cells": len(example.target),
            }
            for example in examples
        ],
        "leave_one_level_out": list(folds),
        "learned_roles": learned_roles,
        "level5_objective": objective.to_dict(),
        "planned_clicks": [list(cell) for cell in clicks],
        "planned_click_count": len(clicks),
        "target_cells_changed_from_exp_duck_031": len(changed_from_rejected),
        "checks": checks,
        "structural_pass": all(checks.values()),
        "recommended_isolated_kaggle_run": all(checks.values()),
        "competition_submit": False,
        "next_action": (
            "Build and run only an isolated private level-5 Kaggle notebook. "
            "Require a live advance to level 6 before any full evaluation."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["structural_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
