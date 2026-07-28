#!/usr/bin/env python3
"""Build the isolated EXP-DUCK-032 calibrated ft09 level-5 notebook."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260704_duck_public_repro_ft09_level4_overlap.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260728_duck_ft09_level5_calibrated.ipynb"
MODEL = ROOT / "experiments/duck_harness_repro/ft09_operator_calibration.py"


LEVEL5_HELPER = '''    def _ft09_level5_calibrated_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "ft09_level5_calibrated_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        if str(policy.get("game_id", "ft09-0d8bbf25")) != game_id:
            return {}
        return policy

    def _try_ft09_level5_calibrated_helper(self) -> bool:
        policy = self._ft09_level5_calibrated_policy()
        if not policy or _level_number(self.game) != int(policy.get("level", 5)):
            return False
        if bool(getattr(self, "_ft09_level5_calibrated_tried", False)):
            return False
        self._ft09_level5_calibrated_tried = True

        from .ft09_operator_calibration import infer_calibrated_level5_objective

        board = _grid_from_state(self.game.current_state)
        run = self.game.game_run
        try:
            objective = infer_calibrated_level5_objective(
                board, {0: "same", 2: "different"}
            )
            requested = list(objective.clicks(board))
        except Exception as exc:
            note = f"ft09_level5_calibrated=rejected; reason={type(exc).__name__}:{exc}"
            if run is not None:
                run.solver_note = f"{note}; {run.solver_note}" if run.solver_note else note
            self.solver.max_actions_per_game = self.action_count
            self.write_viewer_payload()
            return True

        target = objective.target_dict()
        planned = len(requested)
        executed = 0
        solved = False
        effects_ok = True
        stop_reason = "target_exhausted"
        for batch_index, (row, col) in enumerate(requested, start=1):
            if self.should_stop():
                stop_reason = "should_stop"
                break
            current = _grid_from_state(self.game.current_state)
            target_color = int(target[(row, col)])
            if int(current[row][col]) == target_color:
                continue
            action = arcengine.ActionInput(
                id=arcengine.GameAction.ACTION6,
                data={"x": col, "y": row},
            )
            payload = self._execute_action(
                action,
                batch_index=batch_index,
                batch_size=planned,
                generated_tokens=0,
                flush_viewer_payload=False,
            )
            executed += 1
            if payload.get("level_completed"):
                solved = True
                stop_reason = "level_completed"
                break
            if payload.get("run_complete") or payload.get("game_over"):
                stop_reason = "game_over_or_run_complete"
                break
            observed = _grid_from_state(self.game.current_state)
            if int(observed[row][col]) != target_color:
                effects_ok = False
                stop_reason = (
                    f"effect_mismatch_at_{row}_{col}; "
                    f"expected={target_color}; observed={int(observed[row][col])}"
                )
                break

        note = (
            f"ft09_level5_calibrated=attempted; normal={len(objective.normal_cells)}; "
            f"clues={len(objective.clue_cells)}; obstacles={len(objective.obstacle_cells)}; "
            f"unknown_models={len(objective.unknown_role_models)}; "
            f"uncovered={len(objective.uncovered_cells)}; target_signatures=1; "
            f"planned={planned}; executed={executed}; effects_ok={effects_ok}; "
            f"solved={solved}; stop={stop_reason}"
        )
        if run is not None:
            run.solver_note = f"{note}; {run.solver_note}" if run.solver_note else note
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
        "# ARC-AGI-3 - Duck ft09 Level-5 Calibrated Operator Test\n\n"
        "EXP-DUCK-032 replays validated levels 1-4, applies mark roles learned "
        "under four leave-one-level-out gates, excludes fixed obstacles, "
        "verifies each effect, and stops.\n",
    )

    patch_cell = source(cells[12])
    write_marker = 'solver_py.write_text(text, encoding="utf-8")'
    insert_at = patch_cell.index(write_marker)
    model_source = MODEL.read_text(encoding="utf-8")
    addition = (
        "# EXP-DUCK-032: calibrated level-5 operator learner.\n"
        f"operator_model_source = {model_source!r}\n"
        "(PATCH_REPO / 'inference' / 'framework' / "
        "'ft09_operator_calibration.py').write_text("
        "operator_model_source, encoding='utf-8')\n\n"
        f"ft09_level5_helper = {LEVEL5_HELPER!r}\n"
        "marker = '    def should_stop(self) -> bool:\\n'\n"
        "if marker not in text:\n"
        "    raise RuntimeError('Could not find calibrated helper insertion marker')\n"
        "text = text.replace(marker, ft09_level5_helper + marker, 1)\n"
        "old_hook = '''                if self._try_ft09_mask_cycle_helper():\n"
        "                    continue\n'''\n"
        "new_hook = old_hook + '''\n"
        "                if self._try_ft09_level5_calibrated_helper():\n"
        "                    continue\n'''\n"
        "if old_hook not in text:\n"
        "    raise RuntimeError('Could not find calibrated play hook')\n"
        "text = text.replace(old_hook, new_hook, 1)\n\n"
    )
    patch_cell = patch_cell[:insert_at] + addition + patch_cell[insert_at:]
    set_source(cells[12], patch_cell)

    config = source(cells[16])
    config = config.replace(
        "# EXP-DUCK-008 overlap-consistent level-4 diagnostic.",
        "# EXP-DUCK-032 calibrated level-5 operator diagnostic.",
    )
    config = config.replace(
        'DUCK_REPRO_LABEL = "duck-ft09-level4-overlap-20260717"',
        'DUCK_REPRO_LABEL = "duck-ft09-level5-calibrated-20260728"',
    )
    config = config.replace(
        '"stop_after_attempt": True,\n}',
        '"stop_after_attempt": False,\n}',
        1,
    )
    policy_marker = "\ntry:\n    bm.label"
    level5_policy = '''\nFT09_LEVEL5_CALIBRATED_POLICY = {
    "enabled": True,
    "game_id": "ft09-0d8bbf25",
    "level": 5,
    "stop_after_attempt": True,
}
'''
    config = config.replace(policy_marker, level5_policy + policy_marker, 1)
    attr_marker = (
        "    bm.solver.ft09_mask_cycle_helper_policy = "
        "dict(FT09_MASK_CYCLE_HELPER_POLICY)\n"
    )
    config = config.replace(
        attr_marker,
        attr_marker
        + "    bm.solver.ft09_level5_calibrated_policy = "
        "dict(FT09_LEVEL5_CALIBRATED_POLICY)\n",
        1,
    )
    print_marker = (
        '    print("ft09 overlap helper policy:", '
        "json.dumps(bm.solver.ft09_mask_cycle_helper_policy, sort_keys=True))\n"
    )
    config = config.replace(
        print_marker,
        print_marker
        + '    print("ft09 level-5 calibrated policy:", '
        "json.dumps(bm.solver.ft09_level5_calibrated_policy, sort_keys=True))\n",
        1,
    )
    config = config.replace(
        "bm.solver.max_actions_per_game = 120",
        "bm.solver.max_actions_per_game = 90",
        1,
    )
    set_source(cells[16], config)

    notebook.setdefault("metadata", {})["exp_duck_id"] = "EXP-DUCK-032"
    notebook["metadata"]["experiment_purpose"] = (
        "prospective calibrated ft09 level-5 operator test"
    )

    compile("class _Helper:\n" + LEVEL5_HELPER, "<calibrated-helper>", "exec")
    for index, cell in enumerate(cells):
        if cell.get("cell_type") == "code":
            compile(
                source(cell),
                f"{OUTPUT.name}:cell-{index}",
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
    required = (
        "ft09_level5_calibrated_policy",
        "_try_ft09_level5_calibrated_helper",
        "obstacles=",
        "target_signatures=1",
    )
    rendered = json.dumps(notebook)
    if not all(token in rendered for token in required):
        raise RuntimeError("calibrated notebook validation failed")
    OUTPUT.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    print(OUTPUT)
    print("validated: level4 stop disabled; calibrated 9-click level5 helper; cap=90")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
