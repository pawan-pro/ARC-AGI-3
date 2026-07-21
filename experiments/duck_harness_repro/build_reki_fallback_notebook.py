#!/usr/bin/env python3
"""Build the targeted Duck fallback-only Reki saliency experiment notebook."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = REPO_ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260704_duck_public_repro_stall_policy.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260721_duck_reki_fallback.ipynb"
HELPER = Path(__file__).with_name("reki_fallback.py")


def source_text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, text: str) -> None:
    cell["source"] = text.splitlines(keepends=True)


def build_fallback_patch(helper_source: str) -> str:
    return f"""# Fallback-only Reki saliency/dead-signature patch.
# The LLM's requested actions are never rejected by this feature.
reki_helper_py = PATCH_REPO / "inference" / "framework" / "reki_fallback.py"
reki_helper_py.write_text({helper_source!r}, encoding="utf-8")

text = solver_py.read_text(encoding="utf-8")
import_anchor = "from inference.framework.kaggle import (\\n"
if "from inference.framework.reki_fallback import FallbackClickLedger" not in text:
    if import_anchor not in text:
        raise RuntimeError("Could not add Reki fallback import; source shape changed.")
    text = text.replace(
        import_anchor,
        "from inference.framework.reki_fallback import FallbackClickLedger\\n" + import_anchor,
        1,
    )

methods_anchor = "    def _controlled_stall_policy(self) -> dict[str, Any]:\\n"
fallback_methods = r'''    def _reki_fallback_policy(self) -> dict[str, Any]:
        policy = self._controlled_stall_policy()
        config = policy.get("reki_fallback") if policy else None
        return config if isinstance(config, dict) and config.get("enabled") else {{}}

    def _reki_fallback_ledger(self) -> FallbackClickLedger:
        config = self._reki_fallback_policy()
        ledger = getattr(self, "_reki_click_ledger", None)
        if ledger is None:
            ledger = FallbackClickLedger(
                dead_threshold=int(config.get("dead_signature_threshold", 2) or 2),
                border_ignore=int(config.get("border_ignore", 3) or 0),
            )
            self._reki_click_ledger = ledger
        ledger.ensure_level(_level_number(self.game))
        return ledger

    def _reki_fallback_can_run(self) -> bool:
        config = self._reki_fallback_policy()
        if not config or _is_engine_game_over(self.game):
            return False
        if int(arcengine.GameAction.ACTION6.value) not in self.game.current_state.available_actions:
            return False
        ledger = self._reki_fallback_ledger()
        max_clicks = int(config.get("max_clicks_per_level", 0) or 0)
        return not ledger.fallback_exhausted and (max_clicks <= 0 or ledger.fallback_attempts < max_clicks)

    def _try_reki_stall_fallback(self) -> bool:
        policy = self._controlled_stall_policy()
        config = self._reki_fallback_policy()
        if not policy or not config:
            return False
        min_actions = int(policy.get("min_actions", 0) or 0)
        no_progress_limit = int(policy.get("max_no_level_progress_actions", 0) or 0)
        if self.action_count < min_actions or no_progress_limit <= 0:
            return False
        if int(getattr(self, "_stall_no_level_progress_actions", 0)) < no_progress_limit:
            return False
        if not self._reki_fallback_can_run():
            return False

        ledger = self._reki_fallback_ledger()
        choice = ledger.choose(_grid_from_state(self.game.current_state), _level_number(self.game))
        if choice is None:
            return False
        action = arcengine.ActionInput(
            id=arcengine.GameAction.ACTION6,
            data={{"x": int(choice["col"]), "y": int(choice["row"])}} ,
        )
        self._reki_fallback_context = dict(choice)
        try:
            self._execute_action(
                action,
                batch_index=1,
                batch_size=1,
                generated_tokens=0,
            )
        finally:
            self._reki_fallback_context = None
        return True

    def _reki_fallback_summary(self) -> dict[str, Any]:
        ledger = getattr(self, "_reki_click_ledger", None)
        return ledger.summary() if ledger is not None else {{"total_fallback_attempts": 0}}

'''
if fallback_methods.strip() not in text:
    if methods_anchor not in text:
        raise RuntimeError("Could not add Reki fallback methods; stall patch missing.")
    text = text.replace(methods_anchor, fallback_methods + methods_anchor, 1)

old_no_progress = '''        if no_progress_limit > 0 and int(getattr(self, "_stall_no_level_progress_actions", 0)) >= no_progress_limit:
            return f"no_level_progress_actions>={{no_progress_limit}}"
'''
new_no_progress = '''        if no_progress_limit > 0 and int(getattr(self, "_stall_no_level_progress_actions", 0)) >= no_progress_limit:
            if self._reki_fallback_can_run():
                return None
            return f"no_level_progress_actions>={{no_progress_limit}}"
'''
if old_no_progress not in text:
    raise RuntimeError("Could not gate stall stop on fallback availability.")
text = text.replace(old_no_progress, new_no_progress, 1)

play_anchor = '''            while not self.should_stop():
                if (
'''
play_replacement = '''            while not self.should_stop():
                if self._try_reki_stall_fallback():
                    continue
                if (
'''
if play_anchor not in text:
    raise RuntimeError("Could not add fallback hook to play loop.")
text = text.replace(play_anchor, play_replacement, 1)

previous_level_anchor = '''        previous_grid = _grid_from_state(self.game.current_state)
        previous_completed = int(self.game.current_state.levels_completed)
'''
previous_level_replacement = '''        previous_grid = _grid_from_state(self.game.current_state)
        previous_completed = int(self.game.current_state.levels_completed)
        previous_level = _level_number(self.game)
'''
if previous_level_anchor not in text:
    raise RuntimeError("Could not capture pre-action level.")
text = text.replace(previous_level_anchor, previous_level_replacement, 1)

append_anchor = '''        self._update_controlled_stall_counters(payload, generated_tokens)
        self._append_action_viewer_event(payload, current_frame)
'''
append_replacement = '''        self._update_controlled_stall_counters(payload, generated_tokens)
        fallback_config = self._reki_fallback_policy()
        if fallback_config and action.id == arcengine.GameAction.ACTION6:
            fallback_context = getattr(self, "_reki_fallback_context", None)
            observation = self._reki_fallback_ledger().observe(
                previous_grid,
                _grid_from_state(new_state),
                previous_level,
                _level_number(self.game),
                int(action.data.get("y", 0)),
                int(action.data.get("x", 0)),
                fallback=bool(fallback_context),
            )
            payload["reki_fallback_observation"] = observation
            if fallback_context:
                payload["fallback_policy"] = "reki_saliency_deadsig"
                payload["fallback_signature"] = fallback_context.get("signature")
                payload["fallback_saliency"] = fallback_context.get("saliency")
        self._append_action_viewer_event(payload, current_frame)
'''
if append_anchor not in text:
    raise RuntimeError("Could not add fallback observation logging.")
text = text.replace(append_anchor, append_replacement, 1)

viewer_anchor = '''                "batch_size": payload.get("batch_size"),
'''
viewer_replacement = '''                "batch_size": payload.get("batch_size"),
                "fallback_policy": payload.get("fallback_policy"),
                "fallback_signature": payload.get("fallback_signature"),
                "fallback_saliency": payload.get("fallback_saliency"),
                "reki_fallback_observation": payload.get("reki_fallback_observation"),
'''
if viewer_anchor not in text:
    raise RuntimeError("Could not add fallback fields to viewer events.")
text = text.replace(viewer_anchor, viewer_replacement, 1)

note_anchor = '''            if run.solver_note is None:
                run.solver_note = f"tokens={{total_tokens}}"
'''
note_replacement = '''            fallback_summary = json.dumps(self._reki_fallback_summary(), sort_keys=True)
            if run.solver_note is None:
                run.solver_note = f"tokens={{total_tokens}}; reki_fallback={{fallback_summary}}"
            elif "reki_fallback=" not in run.solver_note:
                run.solver_note += f"; reki_fallback={{fallback_summary}}"
'''
if note_anchor not in text:
    raise RuntimeError("Could not add fallback summary to solver note.")
text = text.replace(note_anchor, note_replacement, 1)

solver_py.write_text(text, encoding="utf-8")
for module_name in ["inference.framework.reki_fallback", "inference.framework.solver"]:
    sys.modules.pop(module_name, None)

print("Added fallback-only Reki helper:", reki_helper_py)
print("Fallback actions will be tagged as reki_saliency_deadsig in viewer events.")
"""


def main() -> None:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    helper_source = HELPER.read_text(encoding="utf-8")

    set_source(
        notebook["cells"][0],
        "# ARC-AGI-3 - Duck Fallback-Only Reki Saliency Experiment\n\n"
        "**Experiment:** EXP-DUCK-011\n\n"
        "Run only `sc25` and `tn36`. The normal Duck LLM remains unchanged. "
        "After 90 actions without level progress, a bounded fallback may click "
        "small, rare-colored components while avoiding signatures that were inert twice. "
        "The dead-signature memory never vetoes an LLM action.\n",
    )

    patch_cell = source_text(notebook["cells"][12])
    patch_cell += "\n\n" + build_fallback_patch(helper_source)
    set_source(notebook["cells"][12], patch_cell)

    config = source_text(notebook["cells"][16])
    config = config.replace(
        'DUCK_REPRO_LABEL = "duck-controlled-stall-20260708"',
        'DUCK_REPRO_LABEL = "duck-reki-fallback-20260721"',
    )
    old_games = '''LIMIT_TO_GAME_IDS = [
    "tn36-ef4dde99",
    "sc25-635fd71a",
    "ft09-0d8bbf25",
    "tr87-cd924810",
]'''
    new_games = '''LIMIT_TO_GAME_IDS = [
    "tn36-ef4dde99",
    "sc25-635fd71a",
]'''
    if old_games not in config:
        raise RuntimeError("Could not narrow targeted game list.")
    config = config.replace(old_games, new_games, 1)
    config = config.replace(
        '    "max_consecutive_zero_token_actions": 70,',
        '''    "max_consecutive_zero_token_actions": 0,
    "reki_fallback": {
        "enabled": True,
        "dead_signature_threshold": 2,
        "border_ignore": 3,
        "max_clicks_per_level": 24,
    },''',
        1,
    )
    set_source(notebook["cells"][16], config)

    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-011"
    notebook["metadata"]["experiment_purpose"] = (
        "targeted fallback-only Reki saliency and dead-signature test"
    )
    OUTPUT.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print("games=sc25,tn36 fallback_trigger=90 max_fallback_clicks_per_level=24")


if __name__ == "__main__":
    main()
