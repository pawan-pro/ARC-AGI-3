#!/usr/bin/env python3
"""Build EXP-DUCK-022 from the isolated EXP-DUCK-021 harness."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260723_duck_tn36_level3_true_name_helper.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260723_duck_tn36_level3_wall_route_helper.ipynb"
OLD_HELPER = Path(__file__).parent / "tn36_level3_true_name_helper.py"
NEW_HELPER = Path(__file__).parent / "tn36_level3_wall_route_helper.py"


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    old_literal = repr(OLD_HELPER.read_text(encoding="utf-8"))
    new_literal = repr(NEW_HELPER.read_text(encoding="utf-8"))
    helper_replacements = 0

    for cell in notebook["cells"]:
        text = source(cell)
        if old_literal in text:
            text = text.replace(old_literal, new_literal, 1)
            helper_replacements += 1
        text = text.replace("EXP-DUCK-021", "EXP-DUCK-022")
        text = text.replace(
            "duck-tn36-level3-true-name-helper-20260723",
            "duck-tn36-level3-wall-route-helper-20260723",
        )
        set_source(cell, text)

    if helper_replacements != 1:
        raise RuntimeError(
            f"Expected one embedded helper replacement, found {helper_replacements}"
        )
    set_source(
        notebook["cells"][0],
        "# ARC-AGI-3 - Duck tn36 Level-3 Switching-Wall Route\n\n"
        "**Experiment:** EXP-DUCK-022\n\n"
        "The local official engine verifies route `[2,33,2,2,2,33]`: "
        "right, up, right, right, right, up.\n",
    )
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-022"
    notebook["metadata"]["experiment_purpose"] = (
        "isolated engine-verified tn36 level-3 switching-wall route"
    )
    all_source = "\n".join(source(cell) for cell in notebook["cells"])
    if "Write [3, 3, 3, 3]" in all_source:
        raise RuntimeError("EXP-DUCK-021 helper source remains embedded")
    if "COMMANDS = (2, 33, 2, 2, 2, 33)" not in all_source:
        raise RuntimeError("Engine-verified route was not embedded")
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
    print("games=tn36 max_actions=25 route=[2,33,2,2,2,33] expected_tokens=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
