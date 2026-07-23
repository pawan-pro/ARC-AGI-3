#!/usr/bin/env python3
"""Build EXP-DUCK-021 from the validated EXP-DUCK-020 harness."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260722_duck_tn36_level3_program_helper.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260723_duck_tn36_level3_true_name_helper.ipynb"
OLD_HELPER = Path(__file__).parent / "tn36_level3_program_helper.py"
NEW_HELPER = Path(__file__).parent / "tn36_level3_true_name_helper.py"


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
        text = text.replace("EXP-DUCK-020", "EXP-DUCK-021")
        text = text.replace(
            "duck-tn36-level3-program-helper-20260722",
            "duck-tn36-level3-true-name-helper-20260723",
        )
        set_source(cell, text)

    if helper_replacements != 1:
        raise RuntimeError(
            f"Expected one embedded helper replacement, found {helper_replacements}"
        )
    set_source(
        notebook["cells"][0],
        "# ARC-AGI-3 - Duck tn36 Level-3 True-Name Program\n\n"
        "**Experiment:** EXP-DUCK-021\n\n"
        "The exact source-verified initial level-3 program is `[3, 3, 3, 3]`: "
        "turn on bits 1 and 2 in the first four slots, then run.\n",
    )
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-021"
    notebook["metadata"]["experiment_purpose"] = (
        "isolated source-verified tn36 initial level-3 true-name program"
    )
    all_source = "\n".join(source(cell) for cell in notebook["cells"])
    if "Encode two up commands (33), four right commands (2)" in all_source:
        raise RuntimeError("Old level-3 helper source remains embedded")
    if "Write [3, 3, 3, 3]" not in all_source:
        raise RuntimeError("New level-3 helper source was not embedded")
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
    print("games=tn36 max_actions=25 level3_program=[3,3,3,3] expected_tokens=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
