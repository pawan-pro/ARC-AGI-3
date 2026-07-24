#!/usr/bin/env python3
"""Build EXP-DUCK-024: unchanged Duck first, then a zero-token tn36 repair."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260723_duck_full_eval_ft09_tn36_level3.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260724_duck_full_eval_tn36_postlude.ipynb"


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


POSTLUDE_PATCH = r'''
# EXP-DUCK-024: preserve Duck's complete request stream, then repair tn36.
text = solver_py.read_text(encoding="utf-8")

early_calls = (
    """                if self._try_tn36_level1_helper():
                    continue

""",
    """                if self._try_tn36_level2_program():
                    continue

""",
    """                if self._try_tn36_level3_program():
                    continue

""",
)
removed_early_calls = {}
for call in early_calls:
    call_name = call.split("self.", 1)[1].split("(", 1)[0]
    count = text.count(call)
    removed_early_calls[call_name] = count
    text = text.replace(call, "")
if any(count != 1 for count in removed_early_calls.values()):
    raise RuntimeError(
        f"Expected one early helper call per tn36 level: {removed_early_calls}"
    )

method_anchor = "    def should_stop(self) -> bool:\n"
postlude_method = r"""    def _run_tn36_postlude(self) -> None:
        # Repair clean tn36 levels only after normal Duck has stopped.
        policy = self._tn36_level1_helper_policy()
        if not policy:
            return
        run = self.game.game_run
        if run is None or int(self.game.current_state.levels_completed) >= 3:
            return

        start_level = _level_number(self.game)
        start_actions = self.action_count
        start_tokens = _analyzer_reported_tokens(self.analyzer)
        self._tn36_level1_note(
            f"tn36_postlude=start; level={start_level}; "
            f"duck_actions={start_actions}; duck_tokens={start_tokens}"
        )

        # Duck may leave a level partly edited or in GAME_OVER. RESET restores
        # the current level while keeping already completed levels.
        self._execute_auto_reset()
        helpers = {
            1: self._try_tn36_level1_helper,
            2: self._try_tn36_level2_program,
            3: self._try_tn36_level3_program,
        }
        while int(self.game.current_state.levels_completed) < 3:
            level = _level_number(self.game)
            helper = helpers.get(level)
            if helper is None:
                break
            completed_before = int(self.game.current_state.levels_completed)
            helper()
            completed_after = int(self.game.current_state.levels_completed)
            if completed_after <= completed_before:
                break

        self._tn36_level1_note(
            f"tn36_postlude=finished; "
            f"levels={int(self.game.current_state.levels_completed)}; "
            f"postlude_actions={self.action_count - start_actions}; "
            f"postlude_tokens={_analyzer_reported_tokens(self.analyzer) - start_tokens}"
        )
        self.write_viewer_payload()

"""
if method_anchor not in text:
    raise RuntimeError("Could not add tn36 postlude method.")
text = text.replace(method_anchor, postlude_method + method_anchor, 1)

play_exit_anchor = """                if not result.step_executed:
                    continue
        except Exception as exc:
"""
play_exit_replacement = """                if not result.step_executed:
                    continue
            self._run_tn36_postlude()
        except Exception as exc:
"""
if text.count(play_exit_anchor) != 1:
    raise RuntimeError(
        f"Expected one normal play-loop exit, found {text.count(play_exit_anchor)}"
    )
text = text.replace(play_exit_anchor, play_exit_replacement, 1)

solver_py.write_text(text, encoding="utf-8")
sys.modules.pop("inference.framework.solver", None)
print(
    "Prepared tn36 postlude: unchanged Duck analysis first, "
    "then signature-gated zero-token repair."
)
'''


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]

    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck Full Evaluation with Isolated tn36 Postlude\n\n"
        "**Experiment:** EXP-DUCK-024\n\n"
        "Run the complete EXP-DUCK-009 Duck behavior first. Only after normal "
        "Duck stops on `tn36`, reset its current level and apply the proven "
        "zero-token programs through level 3. This keeps tn36's normal LLM "
        "requests in the shared batch instead of removing them early.\n",
    )
    set_source(cells[12], source(cells[12]) + "\n\n" + POSTLUDE_PATCH)

    for cell in cells:
        text = source(cell)
        text = text.replace("EXP-DUCK-023", "EXP-DUCK-024")
        text = text.replace(
            "duck-full-eval-ft09-tn36-level3-20260723",
            "duck-full-eval-tn36-postlude-20260724",
        )
        set_source(cell, text)

    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-024"
    notebook["metadata"]["experiment_purpose"] = (
        "full evaluation with unchanged Duck request stream followed by tn36 repair"
    )

    all_source = "\n".join(source(cell) for cell in cells)
    checks = {
        "all_games": "LIMIT_TO_GAME_IDS = []" in all_source,
        "postlude_patch": "def _run_tn36_postlude(self)" in all_source,
        "play_exit_patch": "self._run_tn36_postlude()" in all_source,
        "zero_token_helpers": "generated_tokens=0" in all_source,
        "wall_route": "COMMANDS = (2, 33, 2, 2, 2, 33)" in all_source,
    }
    if not all(checks.values()):
        raise RuntimeError(f"EXP-DUCK-024 wiring checks failed: {checks}")

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
    print("games=25 duck=unchanged-first tn36=postlude-through-level3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
