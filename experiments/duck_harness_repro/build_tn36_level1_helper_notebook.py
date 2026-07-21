#!/usr/bin/env python3
"""Build the isolated Duck tn36 level-1 deterministic helper notebook."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = REPO_ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260704_duck_public_repro_stall_policy.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260721_duck_tn36_level1_helper.ipynb"
HELPER_DIR = Path(__file__).parent


def source_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def build_helper_patch(reki_source: str, helper_source: str) -> str:
    return f"""# Signature-gated tn36 level-1 helper patch.
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

methods_anchor = "    def _controlled_stall_policy(self) -> dict[str, Any]:\\n"
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
            self._tn36_level1_helper_stop = True
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
                    f"tn36_level1_helper={{outcome}}; helper_actions={{executed}}"
                )
                self._tn36_level1_helper_stop = True
                self.write_viewer_payload()
                return True

        self._tn36_level1_note(f"tn36_level1_helper=no_progress; helper_actions={{executed}}")
        self._tn36_level1_helper_stop = True
        self.write_viewer_payload()
        return True

'''
if helper_methods.strip() not in text:
    if methods_anchor not in text:
        raise RuntimeError("Could not add tn36 helper methods; stall patch missing.")
    text = text.replace(methods_anchor, helper_methods + methods_anchor, 1)

should_stop_anchor = "    def should_stop(self) -> bool:\\n        run = self.game.game_run\\n"
should_stop_replacement = "    def should_stop(self) -> bool:\\n        if bool(getattr(self, '_tn36_level1_helper_stop', False)):\\n            return True\\n        run = self.game.game_run\\n"
if should_stop_anchor not in text:
    raise RuntimeError("Could not add tn36 helper stop flag.")
text = text.replace(should_stop_anchor, should_stop_replacement, 1)

play_anchor = "            while not self.should_stop():\\n                if (\\n"
play_replacement = "            while not self.should_stop():\\n                if self._try_tn36_level1_helper():\\n                    continue\\n                if (\\n"
if play_anchor not in text:
    raise RuntimeError("Could not add tn36 helper to play loop.")
text = text.replace(play_anchor, play_replacement, 1)

solver_py.write_text(text, encoding="utf-8")
for module_name in [
    "inference.framework.reki_fallback",
    "inference.framework.tn36_level1_helper",
    "inference.framework.solver",
]:
    sys.modules.pop(module_name, None)
print("Added signature-gated tn36 level-1 helper:", tn36_helper_py)
"""


CONFIG = '''# EXP-DUCK-013 isolated tn36 level-1 helper validation.
DUCK_REPRO_LABEL = "duck-tn36-level1-helper-20260721"
LIMIT_TO_GAME_IDS = ["tn36-ef4dde99"]
MAX_GAMES_FOR_DEBUG = None

TN36_LEVEL1_HELPER_POLICY = {
    "enabled": True,
    "target_game_ids": LIMIT_TO_GAME_IDS,
    "stop_after_attempt": True,
}

bm.label = f"{getattr(bm, 'label', 'duck')}-{DUCK_REPRO_LABEL}"
bm.solver.controlled_stall_policy = {"enabled": False}
bm.solver.tn36_level1_helper_policy = dict(TN36_LEVEL1_HELPER_POLICY)
bm.solver.max_actions_per_game = 8
bm.solver.max_runtime_s_per_game = min(
    float(getattr(bm.solver, "max_runtime_s_per_game", 7920.0) or 7920.0),
    1200.0,
)
bm.solver.concurrency = 1
print("Benchmark label:", bm.label)
print("tn36 level-1 helper policy:", json.dumps(TN36_LEVEL1_HELPER_POLICY, sort_keys=True))

def _game_id(g):
    for attr in ("game_id", "env_name", "name"):
        value = getattr(g, attr, None)
        if value:
            return str(value)
    return str(g)

def _apply_target_game_filter(games):
    filtered = list(games)
    original_n_games = len(filtered)
    wanted = set(LIMIT_TO_GAME_IDS)
    filtered = [g for g in filtered if _game_id(g) in wanted]
    print(f"Filtered games after game-list construction: {original_n_games} -> {len(filtered)}")
    print("Selected games:", [_game_id(g) for g in filtered])
    return filtered
'''


def main() -> None:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    reki_source = (HELPER_DIR / "reki_fallback.py").read_text(encoding="utf-8")
    helper_source = (HELPER_DIR / "tn36_level1_helper.py").read_text(encoding="utf-8")

    set_source(
        notebook["cells"][0],
        "# ARC-AGI-3 - Duck tn36 Level-1 Helper\n\n"
        "**Experiment:** EXP-DUCK-013\n\n"
        "This isolated validation uses a board-signature gate to identify the observed "
        "six toggles and submit object. It clicks each toggle once, submits, and stops. "
        "The LLM is not called, so success must come from the inferred mechanic itself.\n",
    )
    patch = source_text(notebook["cells"][12])
    set_source(notebook["cells"][12], patch + "\n\n" + build_helper_patch(reki_source, helper_source))
    set_source(notebook["cells"][16], CONFIG)
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-013"
    notebook["metadata"]["experiment_purpose"] = "isolated tn36 level-1 helper validation"
    OUTPUT.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
