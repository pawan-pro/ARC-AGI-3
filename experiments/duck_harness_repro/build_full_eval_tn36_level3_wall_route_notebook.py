#!/usr/bin/env python3
"""Build EXP-DUCK-023: full evaluation with validated ft09 and tn36 paths."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260723_duck_tn36_level3_wall_route_helper.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260723_duck_full_eval_ft09_tn36_level3.ipynb"


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        text = source(cell)
        text = text.replace("EXP-DUCK-022", "EXP-DUCK-023")
        text = text.replace(
            "duck-tn36-level3-wall-route-helper-20260723",
            "duck-full-eval-ft09-tn36-level3-20260723",
        )
        text = text.replace(
            'LIMIT_TO_GAME_IDS = ["tn36-ef4dde99"]',
            "LIMIT_TO_GAME_IDS = []",
        )
        lines = text.splitlines(keepends=True)
        text = "".join(
            "should_stop_replacement = should_stop_anchor\n"
            if line.startswith("should_stop_replacement = should_stop_anchor +")
            and "_tn36_level3_program_stop" in line
            else line
            for line in lines
        )
        text = "".join(
            line
            for line in text.splitlines(keepends=True)
            if line.strip()
            not in {
                "self._tn36_level3_program_stop = True",
                "bm.solver.max_actions_per_game = 25",
                "bm.solver.max_runtime_s_per_game = 1200.0",
                "bm.solver.concurrency = 1",
            }
        )
        set_source(cell, text)

    set_source(
        notebook["cells"][0],
        "# ARC-AGI-3 - Duck Full Evaluation with tn36 Level 3\n\n"
        "**Experiment:** EXP-DUCK-023\n\n"
        "Run all 25 games. Preserve the validated ft09 path, solve tn36 levels "
        "1-3 in 25 zero-token actions, then resume unchanged Duck on level 4.\n",
    )
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-023"
    notebook["metadata"]["experiment_purpose"] = (
        "full evaluation with validated ft09 and tn36 level 1-3 paths"
    )
    all_source = "\n".join(source(cell) for cell in notebook["cells"])
    checks = {
        "all_games": "LIMIT_TO_GAME_IDS = []" in all_source,
        "wall_route": "COMMANDS = (2, 33, 2, 2, 2, 33)" in all_source,
        "no_level3_stop": "_tn36_level3_program_stop" not in all_source,
        "no_target_action_cap": "max_actions_per_game = 25" not in all_source,
        "no_target_runtime_cap": "max_runtime_s_per_game = 1200.0" not in all_source,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Full-evaluation wiring checks failed: {checks}")
    for index, cell in enumerate(notebook["cells"]):
        if cell.get("cell_type") == "code":
            compile(
                source(cell),
                f"{OUTPUT.name}:cell-{index}",
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
    OUTPUT.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    print(OUTPUT)
    print("games=25 ft09=validated tn36_prefix_actions=25 continuation=unchanged_duck")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
