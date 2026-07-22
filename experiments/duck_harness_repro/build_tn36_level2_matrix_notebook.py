#!/usr/bin/env python3
"""Build the isolated tn36 level-1 plus level-2 matrix-helper notebook."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260721_duck_full_eval_ft09_tn36.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260722_duck_tn36_level2_matrix_helper.ipynb"
HELPER = Path(__file__).parent / "tn36_level2_matrix_helper.py"


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def level2_patch(helper_source: str) -> str:
    return f"""# EXP-DUCK-016: signature-gated tn36 level-2 matrix-copy helper.
tn36_level2_helper_py = PATCH_REPO / "inference" / "framework" / "tn36_level2_matrix_helper.py"
tn36_level2_helper_py.write_text({helper_source!r}, encoding="utf-8")

text = solver_py.read_text(encoding="utf-8")
import_anchor = "from inference.framework.tn36_level1_helper import plan_tn36_level1\\n"
helper_import = "from inference.framework.tn36_level2_matrix_helper import plan_tn36_level2\\n"
if helper_import not in text:
    if import_anchor not in text:
        raise RuntimeError("Could not add tn36 level-2 helper import.")
    text = text.replace(import_anchor, import_anchor + helper_import, 1)

method_anchor = "    def _tn36_level1_helper_policy(self) -> dict[str, Any]:\\n"
helper_methods = r'''    def _tn36_level2_helper_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "tn36_level2_helper_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {{}}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        target_ids = {{str(item) for item in policy.get("target_game_ids") or []}}
        if target_ids and game_id not in target_ids:
            return {{}}
        return policy

    def _try_tn36_level2_helper(self) -> bool:
        policy = self._tn36_level2_helper_policy()
        if not policy or _is_engine_game_over(self.game) or _level_number(self.game) != 2:
            return False
        if bool(getattr(self, "_tn36_level2_helper_tried", False)):
            return False
        self._tn36_level2_helper_tried = True

        plan = plan_tn36_level2(_grid_from_state(self.game.current_state))
        if plan is None:
            self._tn36_level1_note("tn36_level2_helper=signature_mismatch; helper_actions=0")
            self._tn36_level2_helper_stop = True
            self.write_viewer_payload()
            return True

        executed = 0
        for batch_index, click in enumerate(plan, start=1):
            action = arcengine.ActionInput(
                id=arcengine.GameAction.ACTION6,
                data={{"x": int(click["col"]), "y": int(click["row"])}} ,
            )
            payload = self._execute_action(
                action,
                batch_index=batch_index,
                batch_size=len(plan),
                generated_tokens=0,
                flush_viewer_payload=False,
            )
            executed += 1
            if payload.get("level_completed") or payload.get("run_complete") or payload.get("game_over"):
                outcome = "success" if payload.get("level_completed") else "terminal_without_progress"
                self._tn36_level1_note(
                    f"tn36_level2_helper={{outcome}}; helper_actions={{executed}}"
                )
                self._tn36_level2_helper_stop = True
                self.write_viewer_payload()
                return True

        self._tn36_level1_note(f"tn36_level2_helper=no_progress; helper_actions={{executed}}")
        self._tn36_level2_helper_stop = True
        self.write_viewer_payload()
        return True

'''
if helper_methods.strip() not in text:
    if method_anchor not in text:
        raise RuntimeError("Could not add tn36 level-2 helper methods.")
    text = text.replace(method_anchor, helper_methods + method_anchor, 1)

should_stop_anchor = "    def should_stop(self) -> bool:\\n"
should_stop_replacement = should_stop_anchor + "        if bool(getattr(self, '_tn36_level2_helper_stop', False)):\\n            return True\\n"
if should_stop_anchor not in text:
    raise RuntimeError("Could not add tn36 level-2 helper stop flag.")
text = text.replace(should_stop_anchor, should_stop_replacement, 1)

play_anchor = '''                if self._try_tn36_level1_helper():
                    continue

                if retry_analysis_step is None:
'''
play_replacement = '''                if self._try_tn36_level1_helper():
                    continue

                if self._try_tn36_level2_helper():
                    continue

                if retry_analysis_step is None:
'''
if play_anchor not in text:
    raise RuntimeError("Could not add tn36 level-2 helper to play loop.")
text = text.replace(play_anchor, play_replacement, 1)

solver_py.write_text(text, encoding="utf-8")
for module_name in [
    "inference.framework.tn36_level2_matrix_helper",
    "inference.framework.solver",
]:
    sys.modules.pop(module_name, None)
print("Prepared signature-gated tn36 level-2 matrix helper.")
"""


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    helper_source = HELPER.read_text(encoding="utf-8")

    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck tn36 Level-2 Matrix Helper\n\n"
        "**Experiment:** EXP-DUCK-016\n\n"
        "This isolated run executes the validated seven-action level-1 helper, "
        "copies the lower-left 6x4 target matrix into the lower-right editable "
        "matrix, presses submit, and stops without calling the LLM.\n",
    )
    set_source(cells[12], source(cells[12]) + "\n\n" + level2_patch(helper_source))

    config = source(cells[16])
    config = config.replace(
        'DUCK_REPRO_LABEL = "duck-full-eval-ft09-tn36-20260721"',
        'DUCK_REPRO_LABEL = "duck-tn36-level2-matrix-helper-20260722"',
        1,
    )
    config = config.replace(
        "LIMIT_TO_GAME_IDS = []",
        'LIMIT_TO_GAME_IDS = ["tn36-ef4dde99"]',
        1,
    )
    policy = '''
TN36_LEVEL2_HELPER_POLICY = {
    "enabled": True,
    "target_game_ids": ["tn36-ef4dde99"],
    "stop_after_attempt": True,
}
'''
    anchor = "\ntry:\n    bm.label ="
    if anchor not in config:
        raise RuntimeError("Could not add tn36 level-2 policy.")
    config = config.replace(anchor, policy + anchor, 1)

    assign_anchor = "    bm.solver.tn36_level1_helper_policy = dict(TN36_LEVEL1_HELPER_POLICY)\n"
    assign = assign_anchor + "    bm.solver.tn36_level2_helper_policy = dict(TN36_LEVEL2_HELPER_POLICY)\n"
    if assign_anchor not in config:
        raise RuntimeError("Could not configure tn36 level-2 helper policy.")
    config = config.replace(assign_anchor, assign, 1)

    caps_anchor = "    # Preserve the baseline model, prompt, action/runtime caps, and concurrency.\n"
    caps = (
        "    bm.solver.max_actions_per_game = 12\n"
        "    bm.solver.max_runtime_s_per_game = 1200.0\n"
        "    bm.solver.concurrency = 1\n"
    )
    if caps_anchor not in config:
        raise RuntimeError("Could not configure isolated tn36 caps.")
    config = config.replace(caps_anchor, caps + caps_anchor, 1)
    set_source(cells[16], config)

    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-016"
    notebook["metadata"]["experiment_purpose"] = (
        "isolated tn36 level-1 plus level-2 matrix helper validation"
    )
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
    print("games=tn36 max_actions=12 expected_levels=2 expected_tokens=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
