#!/usr/bin/env python3
"""Build EXP-DUCK-026: EXP-DUCK-024 plus a post-Duck tu93 repair."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260724_duck_full_eval_tn36_postlude.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260725_duck_full_eval_tu93_postlude.ipynb"
HELPER = Path(__file__).with_name("tu93_route_helper.py")


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def postlude_patch(helper_source: str) -> str:
    return f'''
# EXP-DUCK-026: preserve EXP-DUCK-024, then repair clean tu93 levels.
tu93_helper_py = PATCH_REPO / "inference" / "framework" / "tu93_route_helper.py"
tu93_helper_py.write_text({helper_source!r}, encoding="utf-8")

text = solver_py.read_text(encoding="utf-8")
import_anchor = "from inference.framework.kaggle import (\\n"
helper_import = "from inference.framework.tu93_route_helper import plan_tu93_route\\n"
if helper_import not in text:
    if import_anchor not in text:
        raise RuntimeError("Could not add tu93 helper import; source shape changed.")
    text = text.replace(import_anchor, helper_import + import_anchor, 1)

method_anchor = "    def should_stop(self) -> bool:\\n"
tu93_method = r"""    def _tu93_postlude_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "tu93_postlude_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {{}}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        targets = {{str(item) for item in policy.get("target_game_ids") or []}}
        if targets and game_id not in targets:
            return {{}}
        return policy

    def _tu93_postlude_note(self, message: str) -> None:
        run = self.game.game_run
        if run is not None:
            run.solver_note = f"{{message}}; {{run.solver_note}}" if run.solver_note else message

    def _run_tu93_postlude(self) -> None:
        # Repair only tu93 levels 1-2, after normal Duck has stopped.
        if not self._tu93_postlude_policy():
            return
        run = self.game.game_run
        if run is None:
            return
        if int(self.game.current_state.levels_completed) >= 2:
            self._tu93_postlude_note(
                f"tu93_postlude=already_complete; "
                f"levels={{int(self.game.current_state.levels_completed)}}"
            )
            self.write_viewer_payload()
            return

        start_actions = self.action_count
        start_tokens = _analyzer_reported_tokens(self.analyzer)
        self._tu93_postlude_note(
            f"tu93_postlude=start; level={{_level_number(self.game)}}; "
            f"duck_actions={{start_actions}}; duck_tokens={{start_tokens}}"
        )

        # Normal Duck may leave a partial route or GAME_OVER state.
        self._execute_auto_reset()
        while int(self.game.current_state.levels_completed) < 2:
            level = _level_number(self.game)
            plan = plan_tu93_route(_grid_from_state(self.game.current_state), level)
            if plan is None:
                self._tu93_postlude_note(
                    f"tu93_postlude=signature_mismatch; level={{level}}"
                )
                break

            completed_before = int(self.game.current_state.levels_completed)
            for batch_index, action_name in enumerate(plan, start=1):
                action = arcengine.ActionInput(
                    id=arcengine.GameAction[action_name],
                    data={{}},
                )
                payload = self._execute_action(
                    action,
                    batch_index=batch_index,
                    batch_size=len(plan),
                    generated_tokens=0,
                    flush_viewer_payload=False,
                )
                if (
                    payload.get("level_completed")
                    or payload.get("run_complete")
                    or payload.get("game_over")
                ):
                    break
            if int(self.game.current_state.levels_completed) <= completed_before:
                self._tu93_postlude_note(
                    f"tu93_postlude=no_progress; level={{level}}"
                )
                break

        self._tu93_postlude_note(
            f"tu93_postlude=finished; "
            f"levels={{int(self.game.current_state.levels_completed)}}; "
            f"postlude_actions={{self.action_count - start_actions}}; "
            f"postlude_tokens={{_analyzer_reported_tokens(self.analyzer) - start_tokens}}"
        )
        self.write_viewer_payload()

"""
if method_anchor not in text:
    raise RuntimeError("Could not add tu93 postlude method.")
text = text.replace(method_anchor, tu93_method + method_anchor, 1)

play_exit_anchor = "            self._run_tn36_postlude()\\n"
play_exit_replacement = (
    "            self._run_tn36_postlude()\\n"
    "            self._run_tu93_postlude()\\n"
)
if text.count(play_exit_anchor) != 1:
    raise RuntimeError(
        f"Expected one tn36 postlude call, found {{text.count(play_exit_anchor)}}"
    )
text = text.replace(play_exit_anchor, play_exit_replacement, 1)

solver_py.write_text(text, encoding="utf-8")
for module_name in [
    "inference.framework.tu93_route_helper",
    "inference.framework.solver",
]:
    sys.modules.pop(module_name, None)
print(
    "Prepared tu93 postlude after unchanged Duck and the existing tn36 postlude."
)
'''


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck Full Evaluation with tn36 and tu93 Postludes\n\n"
        "**Experiment:** EXP-DUCK-026\n\n"
        "Preserve the complete EXP-DUCK-024 execution. After normal Duck stops, "
        "keep the validated tn36 repair and add an exact-board tu93 repair "
        "through level 2. Neither postlude calls the LLM.\n",
    )
    set_source(
        cells[12],
        source(cells[12]) + "\n\n" + postlude_patch(HELPER.read_text()),
    )

    config = source(cells[16])
    label_old = 'DUCK_REPRO_LABEL = "duck-full-eval-tn36-postlude-20260724"'
    label_new = 'DUCK_REPRO_LABEL = "duck-full-eval-tu93-postlude-20260725"'
    if config.count(label_old) != 1:
        raise RuntimeError("Could not replace EXP-DUCK-024 benchmark label.")
    config = config.replace(label_old, label_new, 1)

    policy_anchor = '''TN36_LEVEL3_PROGRAM_POLICY = {
    "enabled": True,
    "target_game_ids": ["tn36-ef4dde99"],
}
'''
    policy_replacement = policy_anchor + '''
TU93_POSTLUDE_POLICY = {
    "enabled": True,
    "target_game_ids": ["tu93-0768757b"],
}
'''
    if config.count(policy_anchor) != 1:
        raise RuntimeError("Could not add tu93 postlude policy.")
    config = config.replace(policy_anchor, policy_replacement, 1)

    assignment_anchor = (
        "    bm.solver.tn36_level3_program_policy = "
        "dict(TN36_LEVEL3_PROGRAM_POLICY)\n"
    )
    assignment_replacement = (
        assignment_anchor
        + "    bm.solver.tu93_postlude_policy = dict(TU93_POSTLUDE_POLICY)\n"
    )
    if config.count(assignment_anchor) != 1:
        raise RuntimeError("Could not assign tu93 postlude policy.")
    config = config.replace(assignment_anchor, assignment_replacement, 1)

    print_anchor = (
        '    print("tn36 level-3 program policy:", '
        "json.dumps(bm.solver.tn36_level3_program_policy, sort_keys=True))\n"
    )
    print_replacement = (
        print_anchor
        + '    print("tu93 postlude policy:", '
        "json.dumps(bm.solver.tu93_postlude_policy, sort_keys=True))\n"
    )
    if config.count(print_anchor) != 1:
        raise RuntimeError("Could not print tu93 postlude policy.")
    config = config.replace(print_anchor, print_replacement, 1)
    set_source(cells[16], config)

    for cell in cells:
        text = source(cell).replace("EXP-DUCK-024", "EXP-DUCK-026")
        set_source(cell, text)

    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-026"
    notebook["metadata"]["experiment_purpose"] = (
        "full EXP-DUCK-024 evaluation plus post-Duck tu93 level 1-2 repair"
    )

    all_source = "\n".join(source(cell) for cell in cells)
    checks = {
        "all_games": "LIMIT_TO_GAME_IDS = []" in all_source,
        "tn36_preserved": "def _run_tn36_postlude(self)" in all_source,
        "tu93_postlude": "def _run_tu93_postlude(self)" in all_source,
        "postlude_order": (
            'play_exit_replacement = (\n    "            self._run_tn36_postlude()'
            in all_source
            and '"            self._run_tu93_postlude()' in all_source
        ),
        "tu93_policy": "bm.solver.tu93_postlude_policy" in all_source,
        "zero_tokens": "generated_tokens=0" in all_source,
    }
    if not all(checks.values()):
        raise RuntimeError(f"EXP-DUCK-026 wiring checks failed: {checks}")

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
    print("games=25 duck=unchanged-first postludes=tn36,tu93")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
