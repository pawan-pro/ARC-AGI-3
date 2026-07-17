#!/usr/bin/env python3
"""Build the EXP-DUCK-008 notebook from the validated exhaustive variant."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260704_duck_public_repro_ft09_level4_exhaustive.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260704_duck_public_repro_ft09_level4_overlap.ipynb"


OVERLAP_HELPER = '''    def _try_ft09_mask_cycle_helper(self) -> bool:
        policy = self._ft09_mask_cycle_helper_policy()
        if not policy:
            return False
        level = _level_number(self.game)
        target_levels = set(int(item) for item in policy.get("levels", [4]))
        if level not in target_levels:
            return False
        tried_key = f"_ft09_overlap_helper_tried_level_{level}"
        if bool(getattr(self, tried_key, False)):
            return False
        setattr(self, tried_key, True)

        board = _grid_from_state(self.game.current_state)
        normal_cells = [
            (16, 14), (16, 22), (16, 30), (16, 38), (16, 46),
            (24, 14), (24, 30), (24, 46),
            (32, 14), (32, 22), (32, 30), (32, 38), (32, 46),
            (40, 22), (40, 38),
            (48, 22), (48, 30), (48, 38),
        ]
        special_cells = [(24, 22), (24, 38), (40, 30)]
        cycle = [9, 8, 12]
        target_string = str(policy.get("target_centers", "RORbRRRRRORRbRROOO"))
        color_by_name = {"b": 9, "R": 8, "O": 12}
        expected_masks = {
            (24, 22): (12, ("gWg", "gOg", "gWg")),
            (24, 38): (9, ("gWg", "gbg", "ggW")),
            (40, 30): (12, ("Wgg", "gOg", "WWW")),
        }

        def mask_signature(special: tuple[int, int]) -> tuple[str, str, str]:
            names = {0: "W", 2: "g", 8: "R", 9: "b", 12: "O"}
            row, col = special
            return tuple(
                "".join(names.get(int(board[row + dr * 2][col + dc * 2]), "?") for dc in (-1, 0, 1))
                for dr in (-1, 0, 1)
            )

        signature_ok = (
            bool(board)
            and len(board) >= 64
            and len(board[0]) >= 64
            and len(target_string) == len(normal_cells)
            and set(target_string) <= set(color_by_name)
            and all(int(board[row][col]) in cycle for row, col in normal_cells)
            and all(
                int(board[row][col]) == expected_masks[(row, col)][0]
                and mask_signature((row, col)) == expected_masks[(row, col)][1]
                for row, col in special_cells
            )
        )
        if not signature_ok:
            run = self.game.game_run
            if run is not None:
                prefix = "ft09_overlap_signature_mismatch"
                run.solver_note = f"{prefix}; {run.solver_note}" if run.solver_note else prefix
            if bool(policy.get("stop_after_attempt", True)):
                self.solver.max_actions_per_game = self.action_count
            return True

        target = {
            cell: color_by_name[target_name]
            for cell, target_name in zip(normal_cells, target_string)
        }
        requested: list[tuple[int, int]] = []
        for (row, col), target_color in target.items():
            steps = self._ft09_cycle_distance(int(board[row][col]), target_color, cycle)
            requested.extend([(row, col)] * steps)

        planned_actions = len(requested)
        executed_actions = 0
        solved = False
        stop_reason = "target_exhausted"
        for batch_index, (row, col) in enumerate(requested, start=1):
            if self.should_stop():
                stop_reason = "should_stop"
                break
            action = arcengine.ActionInput(
                id=arcengine.GameAction.ACTION6,
                data={"x": col, "y": row},
            )
            payload = self._execute_action(
                action,
                batch_index=batch_index,
                batch_size=planned_actions,
                generated_tokens=0,
                flush_viewer_payload=False,
            )
            executed_actions += 1
            if payload.get("level_completed") or payload.get("run_complete") or payload.get("game_over"):
                solved = bool(payload.get("level_completed"))
                stop_reason = "level_completed" if solved else "game_over_or_run_complete"
                break

        run = self.game.game_run
        if run is not None:
            prefix = (
                f"ft09_overlap_target={target_string}; planned={planned_actions}; "
                f"executed={executed_actions}; solved={solved}; stop={stop_reason}"
            )
            run.solver_note = f"{prefix}; {run.solver_note}" if run.solver_note else prefix
        if bool(policy.get("stop_after_attempt", True)):
            self.solver.max_actions_per_game = self.action_count
        self.write_viewer_payload()
        return True

'''


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
        "# ARC-AGI-3 - Duck ft09 Level-4 Overlap-Consistent Diagnostic\n\n"
        "EXP-DUCK-008 replays the known prefix, applies one 21-click target, and stops.\n",
    )

    patch_cell = source(cells[12])
    block_start = patch_cell.index("# EXP-DUCK-006:")
    block_end = patch_cell.index("solver_py.write_text(text, encoding=\"utf-8\")", block_start)
    replacement = (
        "# EXP-DUCK-008: replace candidate cycling with one overlap-consistent target.\n\n"
        f"ft09_overlap_helper = {OVERLAP_HELPER!r}\n\n"
        "start = text.index('    def _try_ft09_mask_cycle_helper')\n"
        "end = text.index('    def should_stop', start)\n"
        "text = text[:start] + ft09_overlap_helper + text[end:]\n\n"
    )
    patch_cell = patch_cell[:block_start] + replacement + patch_cell[block_end:]
    set_source(cells[12], patch_cell)

    config_cell = source(cells[16])
    config_cell = config_cell.replace(
        "# 2026-07-08 controlled stall-policy hook.",
        "# EXP-DUCK-008 overlap-consistent level-4 diagnostic.",
    )
    config_cell = config_cell.replace(
        'DUCK_REPRO_LABEL = "duck-ft09-level4-exhaustive-20260715"',
        'DUCK_REPRO_LABEL = "duck-ft09-level4-overlap-20260717"',
    )
    policy_start = config_cell.index("FT09_MASK_CYCLE_HELPER_POLICY = {")
    policy_end = config_cell.index("\n\ntry:", policy_start)
    overlap_policy = '''FT09_MASK_CYCLE_HELPER_POLICY = {
    "enabled": True,
    "game_id": "ft09-0d8bbf25",
    "levels": [4],
    "target_centers": "RORbRRRRRORRbRROOO",
    "stop_after_attempt": True,
}'''
    config_cell = config_cell[:policy_start] + overlap_policy + config_cell[policy_end:]
    config_cell = config_cell.replace(
        'print("ft09 mask-cycle helper policy:",',
        'print("ft09 overlap helper policy:",',
    )
    config_cell = config_cell.replace("bm.solver.max_actions_per_game = 420", "bm.solver.max_actions_per_game = 120")
    config_cell = config_cell.replace(", 3600.0)", ", 1800.0)")
    set_source(cells[16], config_cell)

    notebook.setdefault("metadata", {})["exp_duck_id"] = "EXP-DUCK-008"
    notebook["metadata"]["experiment_purpose"] = "ft09 level-4 overlap-consistent isolated test"

    compile("class _Helper:\n" + OVERLAP_HELPER, "<overlap-helper>", "exec")
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
    print(f"cells={len(cells)} target=RORbRRRRRORRbRROOO planned_clicks=21")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
