#!/usr/bin/env python3
"""Build EXP-DUCK-009 from the confirmed EXP-DUCK-008 notebook."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260704_duck_public_repro_ft09_level4_overlap.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260704_duck_public_repro_full_eval_overlap.ipynb"


def source(cell: dict[str, object]) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def set_source(cell: dict[str, object], value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]

    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck Full Evaluation with Confirmed ft09 Helper\n\n"
        "EXP-DUCK-009 runs every baseline game once and changes only ft09.\n",
    )

    patch_cell = source(cells[12])
    patch_cell = patch_cell.replace(
        "# EXP-DUCK-008: replace candidate cycling with one overlap-consistent target.",
        "# EXP-DUCK-009: keep the confirmed target but stop only this game runner.",
    )
    patch_cell = patch_cell.replace(
        "self.solver.max_actions_per_game = self.action_count",
        "self._ft09_overlap_stop = True",
    )
    overlap_patch_anchor = "text = text[:start] + ft09_overlap_helper + text[end:]\n\n"
    per_game_stop_patch = '''text = text[:start] + ft09_overlap_helper + text[end:]

old_should_stop = "    def should_stop(self) -> bool:\\n        run = self.game.game_run\\n"
new_should_stop = "    def should_stop(self) -> bool:\\n        if bool(getattr(self, '_ft09_overlap_stop', False)):\\n            return True\\n        run = self.game.game_run\\n"
if old_should_stop not in text:
    raise RuntimeError("Could not add per-game ft09 stop flag; source shape changed.")
text = text.replace(old_should_stop, new_should_stop, 1)

'''
    if overlap_patch_anchor not in patch_cell:
        raise RuntimeError("Could not find EXP-DUCK-008 helper replacement anchor.")
    patch_cell = patch_cell.replace(overlap_patch_anchor, per_game_stop_patch, 1)
    set_source(cells[12], patch_cell)

    config_cell = source(cells[16])
    config_cell = config_cell.replace(
        "# EXP-DUCK-008 overlap-consistent level-4 diagnostic.\n"
        "# This variant is intentionally targeted: inspect known high-signal games first, not the full leaderboard.",
        "# EXP-DUCK-009 controlled full evaluation.\n"
        "# Run every baseline game once; helper policies remain gated to ft09 only.",
    )
    config_cell = config_cell.replace(
        'DUCK_REPRO_LABEL = "duck-ft09-level4-overlap-20260717"',
        'DUCK_REPRO_LABEL = "duck-full-eval-ft09-overlap-20260717"',
    )
    limit_start = config_cell.index("LIMIT_TO_GAME_IDS = [")
    limit_end = config_cell.index("MAX_GAMES_FOR_DEBUG", limit_start)
    config_cell = config_cell[:limit_start] + "LIMIT_TO_GAME_IDS = []\n" + config_cell[limit_end:]
    config_cell = config_cell.replace('"enabled": True,\n    "target_game_ids": LIMIT_TO_GAME_IDS,', '"enabled": False,\n    "target_game_ids": ["ft09-0d8bbf25"],', 1)
    for assignment in (
        "    bm.solver.max_actions_per_game = 120\n",
        "    bm.solver.max_runtime_s_per_game = min(float(getattr(bm.solver, \"max_runtime_s_per_game\", 7920.0) or 7920.0), 1800.0)\n",
        "    bm.solver.concurrency = min(int(getattr(bm.solver, \"concurrency\", 28) or 28), max(1, len(LIMIT_TO_GAME_IDS) or 4))\n",
    ):
        if assignment not in config_cell:
            raise RuntimeError(f"Expected targeted cap assignment missing: {assignment.strip()}")
        config_cell = config_cell.replace(assignment, "", 1)
    config_cell = config_cell.replace(
        "    # Preserve the model/prompt; use existing solver caps only as a safety rail.\n",
        "    # Preserve the baseline model, prompt, action/runtime caps, and concurrency.\n",
    )
    set_source(cells[16], config_cell)

    notebook.setdefault("metadata", {})["exp_duck_id"] = "EXP-DUCK-009"
    notebook["metadata"]["experiment_purpose"] = "full baseline evaluation plus confirmed ft09 path"

    for index, cell in enumerate(cells):
        if cell.get("cell_type") == "code":
            compile(
                source(cell),
                f"{OUTPUT.name}:cell-{index}",
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )

    OUTPUT.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    print(OUTPUT)
    print("cells=23 games=all passes=1 non_ft09_caps=unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
