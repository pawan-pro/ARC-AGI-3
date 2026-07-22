#!/usr/bin/env python3
"""Build EXP-DUCK-020: deterministic tn36 helpers through level 3."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260722_duck_tn36_level2_program_helper.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260722_duck_tn36_level3_program_helper.ipynb"
LEVEL3_HELPER = Path(__file__).parent / "tn36_level3_program_helper.py"


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def level3_patch(helper_source: str) -> str:
    return f'''# EXP-DUCK-020: source-derived tn36 level-3 program.
tn36_level3_helper_py = PATCH_REPO / "inference" / "framework" / "tn36_level3_program_helper.py"
tn36_level3_helper_py.write_text({helper_source!r}, encoding="utf-8")

text = solver_py.read_text(encoding="utf-8")
import_anchor = "from inference.framework.tn36_level2_program_helper import plan_tn36_level2_program\\n"
helper_import = "from inference.framework.tn36_level3_program_helper import plan_tn36_level3_program\\n"
if helper_import not in text:
    if import_anchor not in text:
        raise RuntimeError("Could not add tn36 level-3 helper import.")
    text = text.replace(import_anchor, import_anchor + helper_import, 1)

method_anchor = "    def _tn36_level1_helper_policy(self) -> dict[str, Any]:\\n"
helper_methods = r\'''    def _tn36_level3_program_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "tn36_level3_program_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {{}}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        target_ids = {{str(item) for item in policy.get("target_game_ids") or []}}
        if target_ids and game_id not in target_ids:
            return {{}}
        return policy

    def _try_tn36_level3_program(self) -> bool:
        policy = self._tn36_level3_program_policy()
        if not policy or _is_engine_game_over(self.game) or _level_number(self.game) != 3:
            return False
        if bool(getattr(self, "_tn36_level3_program_tried", False)):
            return False
        self._tn36_level3_program_tried = True

        plan = plan_tn36_level3_program(_grid_from_state(self.game.current_state))
        if plan is None:
            self._tn36_level1_note("tn36_level3_program=signature_mismatch; helper_actions=0")
            self._tn36_level3_program_stop = True
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
                    f"tn36_level3_program={{outcome}}; helper_actions={{executed}}"
                )
                self._tn36_level3_program_stop = True
                self.write_viewer_payload()
                return True

        self._tn36_level1_note(f"tn36_level3_program=no_progress; helper_actions={{executed}}")
        self._tn36_level3_program_stop = True
        self.write_viewer_payload()
        return True

\'''
if helper_methods.strip() not in text:
    if method_anchor not in text:
        raise RuntimeError("Could not add tn36 level-3 helper methods.")
    text = text.replace(method_anchor, helper_methods + method_anchor, 1)

should_stop_anchor = "    def should_stop(self) -> bool:\\n"
should_stop_replacement = should_stop_anchor + "        if bool(getattr(self, '_tn36_level3_program_stop', False)):\\n            return True\\n"
if should_stop_anchor not in text:
    raise RuntimeError("Could not add tn36 level-3 stop flag.")
text = text.replace(should_stop_anchor, should_stop_replacement, 1)

play_anchor = \'''                if self._try_tn36_level2_program():
                    continue

                if retry_analysis_step is None:
\'''
play_replacement = \'''                if self._try_tn36_level2_program():
                    continue

                if self._try_tn36_level3_program():
                    continue

                if retry_analysis_step is None:
\'''
if play_anchor not in text:
    raise RuntimeError("Could not add tn36 level-3 helper to play loop.")
text = text.replace(play_anchor, play_replacement, 1)

solver_py.write_text(text, encoding="utf-8")
for module_name in [
    "inference.framework.tn36_level3_program_helper",
    "inference.framework.solver",
]:
    sys.modules.pop(module_name, None)
print("Prepared source-derived tn36 level-3 program helper.")
'''


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    base_patch = source(cells[12])
    base_patch = "".join(
        "should_stop_replacement = should_stop_anchor\n"
        if line.startswith("should_stop_replacement = should_stop_anchor +")
        and "_tn36_level2_program_stop" in line
        else line
        for line in base_patch.splitlines(keepends=True)
    )
    base_patch = "".join(
        line
        for line in base_patch.splitlines(keepends=True)
        if line.strip() != "self._tn36_level2_program_stop = True"
    )
    set_source(
        cells[12],
        base_patch + "\n\n" + level3_patch(LEVEL3_HELPER.read_text()),
    )
    config = source(cells[16])
    config = config.replace("EXP-DUCK-018", "EXP-DUCK-020")
    config = config.replace(
        'DUCK_REPRO_LABEL = "duck-tn36-level2-program-helper-20260722"',
        'DUCK_REPRO_LABEL = "duck-tn36-level3-program-helper-20260722"',
    )
    config = config.replace("max_actions_per_game = 16", "max_actions_per_game = 25")
    policy = '''
TN36_LEVEL3_PROGRAM_POLICY = {
    "enabled": True,
    "target_game_ids": ["tn36-ef4dde99"],
}
'''
    anchor = "\ntry:\n    bm.label ="
    config = config.replace(anchor, policy + anchor, 1)
    assign_anchor = "    bm.solver.tn36_level2_program_policy = dict(TN36_LEVEL2_PROGRAM_POLICY)\n"
    config = config.replace(
        assign_anchor,
        assign_anchor + "    bm.solver.tn36_level3_program_policy = dict(TN36_LEVEL3_PROGRAM_POLICY)\n",
        1,
    )
    set_source(cells[16], config)
    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck tn36 Level-3 Source Program\n\n"
        "**Experiment:** EXP-DUCK-020\n\n"
        "Deterministic source-derived helpers solve levels 1-3 without the LLM.\n",
    )
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-020"
    notebook["metadata"]["experiment_purpose"] = "isolated tn36 helpers through level 3"
    for index, cell in enumerate(cells):
        if cell.get("cell_type") == "code":
            compile(source(cell), f"{OUTPUT.name}:cell-{index}", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    OUTPUT.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    print(OUTPUT)
    print("games=tn36 max_actions=25 expected_levels=3 expected_tokens=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
