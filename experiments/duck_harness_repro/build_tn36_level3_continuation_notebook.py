#!/usr/bin/env python3
"""Build EXP-DUCK-019: validated tn36 prefix, then normal Duck from level 3."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260722_duck_tn36_level2_program_helper.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260722_duck_tn36_level3_continuation.ipynb"


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    replacements = (
        ("EXP-DUCK-018", "EXP-DUCK-019"),
        ("duck-tn36-level2-program-helper-20260722", "duck-tn36-level3-continuation-20260722"),
        ("max_actions_per_game = 16", "max_actions_per_game = 120"),
        ("max_runtime_s_per_game = 1200.0", "max_runtime_s_per_game = 7920.0"),
    )
    for cell in notebook["cells"]:
        text = source(cell)
        for old, new in replacements:
            text = text.replace(old, new)
        lines = text.splitlines(keepends=True)
        text = "".join(
            "should_stop_replacement = should_stop_anchor\n"
            if line.startswith("should_stop_replacement = should_stop_anchor +")
            and "_tn36_level2_program_stop" in line
            else line
            for line in lines
        )
        text = "".join(
            line
            for line in text.splitlines(keepends=True)
            if line.strip() != "self._tn36_level2_program_stop = True"
        )
        set_source(cell, text)

    set_source(
        notebook["cells"][0],
        "# ARC-AGI-3 - Duck tn36 Level-3 Continuation\n\n"
        "**Experiment:** EXP-DUCK-019\n\n"
        "The validated deterministic helpers solve levels 1 and 2 in 16 actions "
        "and zero tokens. From level 3 onward, the unchanged Duck LLM resumes.\n",
    )
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-019"
    notebook["metadata"]["experiment_purpose"] = (
        "targeted unchanged Duck continuation after the validated tn36 two-level prefix"
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
    print("games=tn36 max_actions=120 prefix_actions=16 continuation=unchanged_duck")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
