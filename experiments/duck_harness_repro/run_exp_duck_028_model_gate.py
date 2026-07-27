#!/usr/bin/env python3
"""Run the EXP-DUCK-028 source-assisted cross-level planning gate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import arcengine

from tn36_cross_level_planner import (
    CandidateResult,
    ObjectiveHypothesis,
    editable_clicks,
    search_program,
    tn36_control_memory,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    ROOT / "experiments/duck_harness_repro/exp_duck_028_model_gate.json"
)
BIT_ROWS = {
    0: (),
    1: (33,),
    2: (36,),
    3: (33, 36),
    33: (33, 48),
}
LEVEL_CONFIG = {
    2: {
        "source_index": 1,
        "length": 4,
        "columns": (39, 44, 49, 54),
        "run_click": (58, 46),
        "target_delta": (0, -4),
        "evidence": (
            "The right robot starts below its target.",
            "Earlier levels establish that command 33 moves up.",
        ),
    },
    3: {
        "source_index": 2,
        "length": 6,
        "columns": (34, 39, 44, 49, 54, 59),
        "run_click": (58, 57),
        "target_delta": (4, -2),
        "evidence": (
            "The right robot starts left and below its target.",
            "Earlier levels preserve the same command editor and movement code.",
            "A new wall state changes after every third command.",
        ),
    },
}


def load_game_class(source: Path) -> type:
    spec = importlib.util.spec_from_file_location("exp_duck_028_tn36", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Tn36


def make_evaluator(game_class: type, level: int):
    config = LEVEL_CONFIG[level]

    def evaluate(program: tuple[int, ...]) -> CandidateResult:
        game = game_class()
        game.set_level(config["source_index"])
        actions = editable_clicks(
            program,
            columns=config["columns"],
            bit_rows=BIT_ROWS,
            run_click=config["run_click"],
        )
        for action in actions:
            frame = game.perform_action(
                arcengine.ActionInput(
                    id=arcengine.GameAction.ACTION6,
                    data={"x": action["col"], "y": action["row"]},
                )
            )
        solved = game.level_index > config["source_index"]
        return CandidateResult(
            program=program,
            solved=solved,
            observed_level=int(game.level_index + 1),
            note=f"state={frame.state.value}; clicks={len(actions)}",
        )

    return evaluate


def run_gate(source: Path) -> dict[str, Any]:
    game_class = load_game_class(source)
    controls = tn36_control_memory()
    searches = {}
    for level in (2, 3):
        config = LEVEL_CONFIG[level]
        dx, dy = config["target_delta"]
        objective = ObjectiveHypothesis(
            statement=(
                f"Move the editable right-side robot onto its target in level {level}."
            ),
            success_test="The official engine advances to the next level.",
            target_dx=dx,
            target_dy=dy,
            evidence=tuple(config["evidence"]),
        )
        searches[str(level)] = search_program(
            objective=objective,
            controls=controls,
            length=config["length"],
            evaluate=make_evaluator(game_class, level),
        ).to_dict()

    level2 = searches["2"]
    level3 = searches["3"]
    copied_demo = make_evaluator(game_class, 3)((3, 3, 3, 3, 0, 0))
    planner_source = (
        Path(__file__).with_name("tn36_cross_level_planner.py").read_text(
            encoding="utf-8"
        )
    )
    known_route_text = "2, 33, 2, 2, 2, 33"
    checks = {
        "objective_declared_before_search": all(
            row["objective"]["statement"] for row in searches.values()
        ),
        "control_memory_reused": all(
            row["command_order"] for row in searches.values()
        ),
        "level2_discovered": level2["winning_program"] is not None,
        "level3_held_out_discovered": level3["winning_program"] is not None,
        "copied_demonstration_rejected": not copied_demo.solved,
        "answer_route_not_stored_in_planner": known_route_text not in planner_source,
        "source_assisted": True,
        "pixel_only_generalization_proven": False,
    }
    result = {
        "experiment": "EXP-DUCK-028",
        "method": "source-assisted model search with cross-level control memory",
        "source": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "controls": [fact.__dict__ for fact in controls],
        "searches": searches,
        "ablation": {
            "name": "copy visible demonstration instead of planning",
            "program": list(copied_demo.program),
            "solved": copied_demo.solved,
            "observed_level": copied_demo.observed_level,
        },
        "checks": checks,
        "research_gate_pass": all(
            value
            for key, value in checks.items()
            if key not in {"pixel_only_generalization_proven"}
        ),
        "competition_submit": False,
        "decision": (
            "Accept as a planning scaffold; reject the claim of general "
            "cross-game autonomy until a pixel-only held-out game passes."
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run_gate(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["research_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
