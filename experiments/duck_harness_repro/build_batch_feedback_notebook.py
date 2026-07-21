#!/usr/bin/env python3
"""Build targeted Duck notebook that interrupts a batch after exact no-change."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = REPO_ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260704_duck_public_repro_stall_policy.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260721_duck_batch_feedback.ipynb"


def text(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_text(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


BATCH_PATCH = r"""# Forge-style feedback patch: stop only the remainder of a batch after exact no-change.
text = solver_py.read_text(encoding="utf-8")

method_anchor = "    def step_env(self, arguments: dict[str, Any]) -> dict[str, Any]:\n"
batch_method = '''    def _batch_feedback_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "batch_feedback_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        target_ids = {str(item) for item in policy.get("target_game_ids") or []}
        exempt_ids = {str(item) for item in policy.get("exempt_game_ids") or []}
        if target_ids and game_id not in target_ids:
            return {}
        if game_id in exempt_ids:
            return {}
        return policy

'''
if batch_method.strip() not in text:
    if method_anchor not in text:
        raise RuntimeError("Could not add batch-feedback policy method.")
    text = text.replace(method_anchor, batch_method + method_anchor, 1)

loop_anchor = '''            executed_payloads.append(payload)
            total_reward += float(payload.get("reward", 0.0) or 0.0)

            if payload.get("run_complete"):
'''
loop_replacement = '''            executed_payloads.append(payload)
            total_reward += float(payload.get("reward", 0.0) or 0.0)

            batch_feedback_policy = self._batch_feedback_policy()
            if (
                batch_feedback_policy
                and batch_index < batch_size
                and not bool(payload.get("board_changed"))
                and not bool(payload.get("level_completed"))
            ):
                payload["batch_feedback_stop"] = True
                payload["batch_feedback_reason"] = "exact_no_board_change"
                if self.viewer_events and self.viewer_events[-1].get("type") == "action":
                    self.viewer_events[-1]["batch_feedback_stop"] = True
                    self.viewer_events[-1]["batch_feedback_reason"] = "exact_no_board_change"
                stop_reason = "batch_feedback_no_change"
                break

            if payload.get("run_complete"):
'''
if loop_anchor not in text:
    raise RuntimeError("Could not add exact no-change interruption to step_env().")
text = text.replace(loop_anchor, loop_replacement, 1)

solver_py.write_text(text, encoding="utf-8")
sys.modules.pop("inference.framework.solver", None)
print("Added exact no-change batch interruption; LLM actions remain unrestricted.")
"""


CONFIG = '''# EXP-DUCK-012 targeted Forge-style batch-feedback test.
DUCK_REPRO_LABEL = "duck-batch-feedback-20260721"
LIMIT_TO_GAME_IDS = [
    "sk48-d8078629",
    "g50t-5849a774",
    "ka59-38d34dbb",
    "dc22-fdcac232",
]
MAX_GAMES_FOR_DEBUG = None

BATCH_FEEDBACK_POLICY = {
    "enabled": True,
    "target_game_ids": LIMIT_TO_GAME_IDS,
    "exempt_game_ids": ["ft09-0d8bbf25"],
    "trigger": "exact_no_board_change_inside_multi_action_batch",
}

bm.label = f"{getattr(bm, 'label', 'duck')}-{DUCK_REPRO_LABEL}"
bm.solver.controlled_stall_policy = {"enabled": False}
bm.solver.batch_feedback_policy = dict(BATCH_FEEDBACK_POLICY)
bm.solver.concurrency = min(
    int(getattr(bm.solver, "concurrency", 28) or 28),
    len(LIMIT_TO_GAME_IDS),
)
print("Benchmark label:", bm.label)
print("Batch feedback policy:", json.dumps(bm.solver.batch_feedback_policy, sort_keys=True))

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
    set_text(
        notebook["cells"][0],
        "# ARC-AGI-3 - Duck Exact No-Change Batch Feedback\n\n"
        "**Experiment:** EXP-DUCK-012\n\n"
        "The LLM and prompt are unchanged. If an action inside a multi-action batch "
        "leaves the board exactly unchanged, only the unexecuted remainder of that "
        "batch is cancelled so Duck can observe and reason again. `ft09` is explicitly exempt.\n",
    )
    set_text(notebook["cells"][12], text(notebook["cells"][12]) + "\n\n" + BATCH_PATCH)
    set_text(notebook["cells"][16], CONFIG)
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-012"
    notebook["metadata"]["experiment_purpose"] = (
        "targeted exact no-change batch interruption test"
    )
    OUTPUT.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
