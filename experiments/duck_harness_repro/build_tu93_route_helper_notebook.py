#!/usr/bin/env python3
"""Build EXP-DUCK-025: isolated zero-token tu93 route validation."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260704_duck_public_repro_stall_policy.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260725_duck_tu93_route_helper.ipynb"
HELPER = Path(__file__).with_name("tu93_route_helper.py")


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def helper_patch(helper_source: str) -> str:
    return f'''# EXP-DUCK-025: exact-board tu93 movement route.
tu93_helper_py = PATCH_REPO / "inference" / "framework" / "tu93_route_helper.py"
tu93_helper_py.write_text({helper_source!r}, encoding="utf-8")

text = solver_py.read_text(encoding="utf-8")
import_anchor = "from inference.framework.kaggle import (\\n"
helper_import = "from inference.framework.tu93_route_helper import plan_tu93_route\\n"
if helper_import not in text:
    if import_anchor not in text:
        raise RuntimeError("Could not add tu93 helper import; source shape changed.")
    text = text.replace(import_anchor, helper_import + import_anchor, 1)

methods_anchor = "    def _controlled_stall_policy(self) -> dict[str, Any]:\\n"
helper_methods = r"""    def _tu93_route_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "tu93_route_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {{}}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        target_ids = {{str(item) for item in policy.get("target_game_ids") or []}}
        if target_ids and game_id not in target_ids:
            return {{}}
        return policy

    def _tu93_route_note(self, message: str) -> None:
        run = self.game.game_run
        if run is not None:
            run.solver_note = f"{{message}}; {{run.solver_note}}" if run.solver_note else message

    def _try_tu93_route(self) -> bool:
        policy = self._tu93_route_policy()
        level = _level_number(self.game)
        if not policy or _is_engine_game_over(self.game) or level not in (1, 2):
            return False

        tried = getattr(self, "_tu93_route_tried_levels", set())
        if level in tried:
            return False
        tried.add(level)
        self._tu93_route_tried_levels = tried

        plan = plan_tu93_route(_grid_from_state(self.game.current_state), level)
        if plan is None:
            self._tu93_route_note(
                f"tu93_route=signature_mismatch; level={{level}}; helper_actions=0"
            )
            self._tu93_route_stop = True
            self.write_viewer_payload()
            return True

        executed = 0
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
            executed += 1
            if payload.get("level_completed"):
                self._tu93_route_note(
                    f"tu93_route=success; level={{level}}; helper_actions={{executed}}"
                )
                if level >= 2:
                    self._tu93_route_stop = True
                self.write_viewer_payload()
                return True
            if payload.get("run_complete") or payload.get("game_over"):
                self._tu93_route_note(
                    f"tu93_route=terminal_without_progress; "
                    f"level={{level}}; helper_actions={{executed}}"
                )
                self._tu93_route_stop = True
                self.write_viewer_payload()
                return True

        self._tu93_route_note(
            f"tu93_route=no_progress; level={{level}}; helper_actions={{executed}}"
        )
        self._tu93_route_stop = True
        self.write_viewer_payload()
        return True

"""
if helper_methods.strip() not in text:
    if methods_anchor not in text:
        raise RuntimeError("Could not add tu93 helper methods; stall patch missing.")
    text = text.replace(methods_anchor, helper_methods + methods_anchor, 1)

should_stop_anchor = "    def should_stop(self) -> bool:\\n        run = self.game.game_run\\n"
should_stop_replacement = "    def should_stop(self) -> bool:\\n        if bool(getattr(self, '_tu93_route_stop', False)):\\n            return True\\n        run = self.game.game_run\\n"
if should_stop_anchor not in text:
    raise RuntimeError("Could not add tu93 helper stop flag.")
text = text.replace(should_stop_anchor, should_stop_replacement, 1)

play_anchor = "            while not self.should_stop():\\n                if (\\n"
play_replacement = "            while not self.should_stop():\\n                if self._try_tu93_route():\\n                    continue\\n                if (\\n"
if play_anchor not in text:
    raise RuntimeError("Could not add tu93 helper to play loop.")
text = text.replace(play_anchor, play_replacement, 1)

solver_py.write_text(text, encoding="utf-8")
for module_name in [
    "inference.framework.tu93_route_helper",
    "inference.framework.solver",
]:
    sys.modules.pop(module_name, None)
print("Added signature-gated tu93 route helper:", tu93_helper_py)
'''


CONFIG = '''# EXP-DUCK-025 isolated tu93 route validation.
DUCK_REPRO_LABEL = "duck-tu93-route-helper-20260725"
LIMIT_TO_GAME_IDS = ["tu93-0768757b"]
MAX_GAMES_FOR_DEBUG = None

TU93_ROUTE_POLICY = {
    "enabled": True,
    "target_game_ids": LIMIT_TO_GAME_IDS,
}

bm.label = f"{getattr(bm, 'label', 'duck')}-{DUCK_REPRO_LABEL}"
bm.solver.controlled_stall_policy = {"enabled": False}
bm.solver.tu93_route_policy = dict(TU93_ROUTE_POLICY)
bm.solver.max_actions_per_game = 30
bm.solver.max_runtime_s_per_game = 1200.0
bm.solver.concurrency = 1
print("Benchmark label:", bm.label)
print("tu93 route policy:", json.dumps(TU93_ROUTE_POLICY, sort_keys=True))

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
    print(f"Filtered games after game-list construction: {{original_n_games}} -> {{len(filtered)}}")
    print("Selected games:", [_game_id(g) for g in filtered])
    return filtered
'''


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck tu93 Route Helper\n\n"
        "**Experiment:** EXP-DUCK-025\n\n"
        "This isolated test recognizes the exact clean starting boards for "
        "`tu93` levels 1 and 2, then replays routes seen succeeding in several "
        "independent Duck runs. It uses no LLM tokens.\n",
    )
    set_source(cells[12], source(cells[12]) + "\n\n" + helper_patch(HELPER.read_text()))
    set_source(cells[16], CONFIG)
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-025"
    notebook["metadata"]["experiment_purpose"] = (
        "isolated signature-gated tu93 level 1 and 2 route validation"
    )

    all_source = "\n".join(source(cell) for cell in cells)
    checks = {
        "one_game": 'LIMIT_TO_GAME_IDS = ["tu93-0768757b"]' in all_source,
        "helper_patch": "def _try_tu93_route(self)" in all_source,
        "zero_tokens": "generated_tokens=0" in all_source,
        "action_limit": "max_actions_per_game = 30" in all_source,
    }
    if not all(checks.values()):
        raise RuntimeError(f"EXP-DUCK-025 wiring checks failed: {checks}")

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
    print("games=1 target=tu93 expected_levels=2 expected_actions=28 expected_tokens=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
