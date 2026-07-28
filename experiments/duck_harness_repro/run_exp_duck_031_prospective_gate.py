#!/usr/bin/env python3
"""Freeze the source-hidden EXP-DUCK-031 ft09 level-5 objective and plan."""

from __future__ import annotations

import json
from pathlib import Path

from ft09_level5_objective_model import infer_level5_objective


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_level4_overlap/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)
OUTPUT = ROOT / "experiments/duck_harness_repro/exp_duck_031_prospective_gate.json"


def main() -> int:
    events = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    level5_event = next(
        event
        for event in events
        if int(event.get("level") or 0) == 5 and bool(event.get("level_completed"))
    )
    board = level5_event["board"]
    objective = infer_level5_objective(board)
    clicks = objective.clicks(board)
    target_colors = [color for _, color in objective.target]
    source = Path(__file__).with_name("ft09_level5_objective_model.py").read_text(
        encoding="utf-8"
    )
    checks = {
        "no_level5_actions_available": level5_event is events[-1],
        "no_stored_level5_coordinates": all(
            token not in source
            for token in ("(6, 24)", "(14, 16)", "(54, 40)")
        ),
        "binary_palette_discovered": len(objective.state_colors) == 2,
        "geometry_discovered": (
            len(objective.normal_cells) == 27
            and len(objective.clue_cells) == 11
            and objective.spacing == 8
        ),
        "one_actionable_target": len({objective.target}) == 1,
        "semantic_ambiguity_is_action_invariant": (
            len(objective.semantic_models) == 2
        ),
        "eighteen_guarded_clicks": len(clicks) == 18,
        "nine_cells_already_correct": len(target_colors) - len(clicks) == 9,
    }
    result = {
        "experiment": "EXP-DUCK-031",
        "method": "prospective source-hidden binary-mask objective inference",
        "data_boundary": {
            "input": "terminal level-4 frame containing untouched level-5 board",
            "known_level5_actions": 0,
            "known_level5_success": False,
            "game_source_used_by_learner": False,
        },
        "objective": objective.to_dict(),
        "planned_clicks": [list(cell) for cell in clicks],
        "planned_click_count": len(clicks),
        "guard": (
            "After each click, require the observed cell to equal its predicted "
            "target color; abort on mismatch, game over, or target ambiguity."
        ),
        "checks": checks,
        "structural_pass": all(checks.values()),
        "competition_submit": False,
        "next_action": (
            "Run only the isolated private Kaggle kernel. Do not build a full "
            "evaluation unless level 5 advances."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["structural_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
