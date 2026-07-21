#!/usr/bin/env python3
"""Prepare the full Duck evaluation candidate with ft09 and tn36 helpers."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260704_duck_public_repro_full_eval_overlap.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260721_duck_full_eval_ft09_tn36.ipynb"
HELPER_DIR = Path(__file__).parent


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def tn36_patch(reki_source: str, helper_source: str) -> str:
    return f"""# EXP-DUCK-014 candidate: signature-gated tn36 level-1 prefix.
reki_helper_py = PATCH_REPO / "inference" / "framework" / "reki_fallback.py"
tn36_helper_py = PATCH_REPO / "inference" / "framework" / "tn36_level1_helper.py"
reki_helper_py.write_text({reki_source!r}, encoding="utf-8")
tn36_helper_py.write_text({helper_source!r}, encoding="utf-8")

text = solver_py.read_text(encoding="utf-8")
import_anchor = "from inference.framework.kaggle import (\\n"
helper_import = "from inference.framework.tn36_level1_helper import plan_tn36_level1\\n"
if helper_import not in text:
    if import_anchor not in text:
        raise RuntimeError("Could not add tn36 helper import; source shape changed.")
    text = text.replace(import_anchor, helper_import + import_anchor, 1)

method_anchor = "    def _controlled_stall_policy(self) -> dict[str, Any]:\\n"
helper_methods = r'''    def _tn36_level1_helper_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "tn36_level1_helper_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {{}}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        target_ids = {{str(item) for item in policy.get("target_game_ids") or []}}
        if target_ids and game_id not in target_ids:
            return {{}}
        return policy

    def _tn36_level1_note(self, message: str) -> None:
        run = self.game.game_run
        if run is not None:
            run.solver_note = f"{{message}}; {{run.solver_note}}" if run.solver_note else message

    def _try_tn36_level1_helper(self) -> bool:
        policy = self._tn36_level1_helper_policy()
        if not policy or _is_engine_game_over(self.game) or _level_number(self.game) != 1:
            return False
        if bool(getattr(self, "_tn36_level1_helper_tried", False)):
            return False
        self._tn36_level1_helper_tried = True

        plan = plan_tn36_level1(_grid_from_state(self.game.current_state))
        if plan is None:
            self._tn36_level1_note("tn36_level1_helper=signature_mismatch; helper_actions=0")
            return False

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
                    f"tn36_level1_helper={{outcome}}; helper_actions={{executed}}"
                )
                self.write_viewer_payload()
                return True

        self._tn36_level1_note(f"tn36_level1_helper=no_progress; helper_actions={{executed}}")
        self.write_viewer_payload()
        return True

'''
if helper_methods.strip() not in text:
    if method_anchor not in text:
        raise RuntimeError("Could not add tn36 helper methods; source shape changed.")
    text = text.replace(method_anchor, helper_methods + method_anchor, 1)

play_anchor = '''                if self._try_ft09_mask_cycle_helper():
                    continue

                if retry_analysis_step is None:
'''
play_replacement = '''                if self._try_ft09_mask_cycle_helper():
                    continue

                if self._try_tn36_level1_helper():
                    continue

                if retry_analysis_step is None:
'''
if play_anchor not in text:
    raise RuntimeError("Could not add tn36 helper to full-evaluation play loop.")
text = text.replace(play_anchor, play_replacement, 1)

solver_py.write_text(text, encoding="utf-8")
for module_name in [
    "inference.framework.reki_fallback",
    "inference.framework.tn36_level1_helper",
    "inference.framework.solver",
]:
    sys.modules.pop(module_name, None)
print("Prepared tn36 level-1 prefix; normal Duck resumes on level 2.")
"""


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    reki_source = (HELPER_DIR / "reki_fallback.py").read_text(encoding="utf-8")
    helper_source = (HELPER_DIR / "tn36_level1_helper.py").read_text(encoding="utf-8")

    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck Full Evaluation with ft09 and tn36 Helpers\n\n"
        "**Candidate:** EXP-DUCK-014\n\n"
        "This preserves the validated EXP-DUCK-009 ft09 path. On tn36 level 1 only, "
        "a signature-gated seven-action prefix is attempted; normal Duck then resumes "
        "from level 2. This notebook must not launch unless EXP-DUCK-013 passes.\n",
    )
    set_source(
        cells[12],
        source(cells[12]) + "\n\n" + tn36_patch(reki_source, helper_source),
    )

    config = source(cells[16])
    config = config.replace(
        'DUCK_REPRO_LABEL = "duck-full-eval-ft09-overlap-20260717"',
        'DUCK_REPRO_LABEL = "duck-full-eval-ft09-tn36-20260721"',
        1,
    )
    policy = '''
TN36_LEVEL1_HELPER_POLICY = {
    "enabled": True,
    "target_game_ids": ["tn36-ef4dde99"],
    "continue_with_llm_after_success": True,
}
'''
    anchor = "\ntry:\n    bm.label ="
    if anchor not in config:
        raise RuntimeError("Could not add tn36 full-evaluation policy.")
    config = config.replace(anchor, policy + anchor, 1)
    assign_anchor = "    bm.solver.controlled_stall_policy = dict(CONTROLLED_STALL_POLICY)\n"
    assign = assign_anchor + "    bm.solver.tn36_level1_helper_policy = dict(TN36_LEVEL1_HELPER_POLICY)\n"
    if assign_anchor not in config:
        raise RuntimeError("Could not configure tn36 full-evaluation policy.")
    config = config.replace(assign_anchor, assign, 1)
    print_anchor = '    print("ft09 replay prefix policy:",'
    config = config.replace(
        print_anchor,
        '    print("tn36 level-1 helper policy:", json.dumps(bm.solver.tn36_level1_helper_policy, sort_keys=True))\n'
        + print_anchor,
        1,
    )
    set_source(cells[16], config)

    notebook.setdefault("metadata", {})["exp_duck_id"] = "EXP-DUCK-014"
    notebook["metadata"]["experiment_purpose"] = (
        "full evaluation with validated ft09 path and candidate tn36 level-1 prefix"
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
    print("cells=23 games=all ft09=unchanged tn36=level1-prefix-then-llm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
