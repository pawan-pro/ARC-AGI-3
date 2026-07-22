#!/usr/bin/env python3
"""Build isolated EXP-DUCK-018 from the validated replay notebook."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260722_duck_tn36_level2_replay_helper.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260722_duck_tn36_level2_program_helper.ipynb"
OLD_HELPER = Path(__file__).parent / "tn36_level2_replay_helper.py"
NEW_HELPER = Path(__file__).parent / "tn36_level2_program_helper.py"


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    old_helper = OLD_HELPER.read_text(encoding="utf-8")
    new_helper = NEW_HELPER.read_text(encoding="utf-8")

    replacements = (
        (repr(old_helper), repr(new_helper)),
        ("EXP-DUCK-017", "EXP-DUCK-018"),
        ("tn36_level2_replay", "tn36_level2_program"),
        ("level-2 replay", "level-2 program"),
        ("Level-2 Proven Replay", "Level-2 Source Program"),
        ("level2-replay-helper", "level2-program-helper"),
        ("max_actions_per_game = 33", "max_actions_per_game = 16"),
        ("max_actions=33", "max_actions=16"),
        ("expected_levels=2 expected_tokens=0", "expected_levels=2 expected_tokens=0"),
        ("exact 26-click level-2 sequence from the successful July 4 Duck trace", "source-derived nine-click level-2 program: write command 33 into all four slots, then run it"),
    )
    for cell in notebook["cells"]:
        text = source(cell)
        for old, new in replacements:
            text = text.replace(old, new)
        set_source(cell, text)

    set_source(
        notebook["cells"][0],
        "# ARC-AGI-3 - Duck tn36 Level-2 Source Program\n\n"
        "**Experiment:** EXP-DUCK-018\n\n"
        "This isolated run executes the validated seven-action level-1 helper, "
        "writes command 33 into all four level-2 program slots using eight "
        "marker clicks, then runs the program. It stops without calling the LLM.\n",
    )
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-018"
    notebook["metadata"]["experiment_purpose"] = (
        "isolated source-derived nine-click tn36 level-2 program validation"
    )
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
    print("games=tn36 max_actions=16 expected_levels=2 expected_tokens=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
