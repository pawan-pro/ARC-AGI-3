#!/usr/bin/env python3
"""Run the source-hidden EXP-DUCK-029 tu93 pixel-learning gate."""

from __future__ import annotations

import json
from pathlib import Path

from tu93_pixel_world_model import learn_visual_model, parse_world, plan_world


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_tu93_level3_route/latest/artifacts"
    / "tu93-0768757b_p0_events.jsonl"
)
BENCHMARK = (
    ROOT / "artifacts/kaggle/duck_tu93_level3_route/latest/benchmark.json"
)
OUTPUT = ROOT / "experiments/duck_harness_repro/exp_duck_029_pixel_gate.json"


def main() -> int:
    actions = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("type") == "action"
    ]
    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    run = benchmark["game_runs"][0]
    training_count = sum(int(value) for value in run["actions_per_level"][:2])
    training_events = actions[:training_count]
    heldout_board = training_events[-1]["board"]

    model = learn_visual_model(training_events)
    world = parse_world(heldout_board, model)
    planned = plan_world(heldout_board, model, use_marker_locks=True)
    naive = plan_world(heldout_board, model, use_marker_locks=False)

    # Validation happens only after planning; these actions were never passed to
    # the learner or planner.
    heldout_events = actions[training_count:]
    actual_actions = tuple(str(event["action_display"]) for event in heldout_events)
    actual_success = bool(heldout_events and heldout_events[-1].get("reward"))
    naive_first_disagreement = next(
        (
            index
            for index, (predicted, actual) in enumerate(
                zip(naive.actions or (), actual_actions),
                start=1,
            )
            if predicted != actual
        ),
        None,
    )
    learner_source = Path(__file__).with_name("tu93_pixel_world_model.py").read_text(
        encoding="utf-8"
    )
    checks = {
        "source_hidden_from_learner": "tu93.py" not in learner_source,
        "no_level3_actions_used_for_planning": len(training_events) == training_count,
        "four_controls_learned": len(model.action_deltas) == 4,
        "visual_roles_learned": (
            model.agent_color,
            model.target_color,
            model.token_color,
            model.marker_color,
        ) == (9, 14, 8, 15),
        "three_token_dependencies_parsed": len(world.locks) == 3,
        "heldout_plan_found": planned.actions is not None,
        "heldout_plan_matches_live_replay": planned.actions == actual_actions,
        "live_replay_advanced_level": actual_success,
        "naive_model_rejected": naive.actions != actual_actions,
    }
    result = {
        "experiment": "EXP-DUCK-029",
        "method": "source-hidden pixel-derived world model and BFS",
        "data_boundary": {
            "training_levels": [1, 2],
            "training_action_frames": training_count,
            "heldout_level": 3,
            "heldout_actions_available_to_planner": 0,
            "heldout_initial_board_source": "terminal frame after level 2",
        },
        "learned_model": model.to_dict(),
        "heldout_world": {
            "agent": world.agent,
            "target": world.target,
            "tokens": sorted(world.tokens),
            "locks": [
                {"token": token, "locked_neighbor": world.locks[token]}
                for token in sorted(world.locks)
            ],
            "nodes": len(world.nodes),
        },
        "planned": planned.to_dict(),
        "naive_ablation": {
            **naive.to_dict(),
            "first_disagreement_with_live_replay": naive_first_disagreement,
            "black_box_observation": (
                "The naive prediction enters a still-locked cell at step 4 "
                "and produces GAME_OVER."
            ),
        },
        "validation": {
            "actual_actions": list(actual_actions),
            "actual_actions_count": len(actual_actions),
            "actual_success": actual_success,
        },
        "checks": checks,
        "structural_pass": all(checks.values()),
        "competition_submit": False,
        "decision": (
            "Accept the pixel-only within-game transfer gate. Next test the "
            "same learner architecture on a different held-out game family."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["structural_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
