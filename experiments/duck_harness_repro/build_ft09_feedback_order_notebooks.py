#!/usr/bin/env python3
"""Build two unlaunched EXP-DUCK-035 feedback-order notebooks."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260730_duck_ft09_bounded_gray_reasoner.ipynb"
MODEL = ROOT / "experiments/duck_harness_repro/two_action_feedback_gate.py"
MEMORY = ROOT / "experiments/duck_harness_repro/exp_duck_034_mechanics_memory.json"
TOP = "ft09-level5-magenta-top"
MIDDLE = "ft09-level5-magenta-middle"
ARMS = (
    ("top-middle", (TOP, MIDDLE)),
    ("middle-top", (MIDDLE, TOP)),
)


FEEDBACK_HELPER = '''    def _feedback_order_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "feedback_order_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        if str(policy.get("game_id")) != game_id:
            return {}
        return policy

    def _try_feedback_order_gate(self) -> bool:
        policy = self._feedback_order_policy()
        if not policy or _level_number(self.game) != int(policy.get("level", -1)):
            return False
        if bool(getattr(self, "_feedback_order_tried", False)):
            return False
        self._feedback_order_tried = True

        from pathlib import Path
        from .bounded_reasoning_loop import MechanicsMemory, ReasoningContext
        from .two_action_feedback_gate import (
            FeedbackHypothesis,
            TwoActionFeedbackController,
        )

        run = self.game.game_run
        initial = _grid_from_state(self.game.current_state)
        try:
            controller = TwoActionFeedbackController(
                memory=MechanicsMemory.from_dict(dict(policy["memory"])),
                context=ReasoningContext(
                    game_family=str(policy["game_family"]),
                    game_id=str(policy["game_id"]),
                    level=int(policy["level"]),
                ),
                initial_board=initial,
                action_order=tuple(policy["action_order"]),
                feedback=FeedbackHypothesis(
                    point=tuple(policy["feedback_point"]),
                    inactive_value=int(policy["feedback_inactive"]),
                    active_value=int(policy["feedback_active"]),
                    active_rules=frozenset(policy["feedback_active_rules"]),
                ),
            )
        except Exception as exc:
            note = (
                "feedback_order=rejected_before_action; "
                f"reason={type(exc).__name__}:{exc}"
            )
            if run is not None:
                run.solver_note = f"{note}; {run.solver_note}" if run.solver_note else note
            self.solver.max_actions_per_game = self.action_count
            self.write_viewer_payload()
            return True

        while not controller.stopped:
            current = _grid_from_state(self.game.current_state)
            planned = controller.next_action(current)
            if planned is None:
                break
            action = arcengine.ActionInput(
                id=arcengine.GameAction.ACTION6,
                data={"x": planned.col, "y": planned.row},
            )
            payload = self._execute_action(
                action,
                batch_index=planned.index,
                batch_size=2,
                generated_tokens=0,
                flush_viewer_payload=False,
            )
            controller.observe(
                _grid_from_state(self.game.current_state),
                level_completed=bool(payload.get("level_completed")),
                game_over=bool(payload.get("game_over")),
                run_complete=bool(payload.get("run_complete")),
            )

        trace_path = Path(str(policy["trace_path"]))
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        controller.save_trace(trace_path)
        exact = all(
            record.get("prediction_check") == "match"
            for record in controller.records
        )
        note = (
            f"feedback_order=attempted; arm={policy['arm']}; "
            f"runtime_llm=False; planned=2; executed={len(controller.records)}; "
            f"exact={exact}; stop={controller.stop_reason}; trace={trace_path.name}"
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


def build(
    arm: str,
    order: tuple[str, str],
    *,
    experiment_id: str = "EXP-DUCK-035",
    feedback_active_rules: tuple[str, str] = (TOP, MIDDLE),
    date_slug: str = "20260730",
    purpose: str = "two-action order test of regional XOR plus corner feedback",
) -> tuple[Path, Path]:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    model_source = MODEL.read_text(encoding="utf-8")
    memory = json.loads(MEMORY.read_text(encoding="utf-8"))
    output = PACKAGE_DIR / f"arc3_{date_slug}_duck_ft09_feedback_{arm}.ipynb"
    metadata_path = PACKAGE_DIR / f"kernel-metadata-ft09-feedback-{arm}.json"

    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck Two-Action Feedback Order Gate\n\n"
        f"{experiment_id} arm `{arm}` replays the validated ft09 levels 1-4 "
        "prefix, executes exactly two regional operators, predicts every pixel "
        "under the regional-XOR plus corner-feedback hypothesis, and stops. "
        "No runtime LLM is used.\n",
    )

    patch_cell = source(cells[12])
    write_marker = 'solver_py.write_text(text, encoding="utf-8")'
    insert_at = patch_cell.index(write_marker)
    addition = (
        f"# {experiment_id}: two-action feedback-order gate.\n"
        f"feedback_gate_source = {model_source!r}\n"
        "(PATCH_REPO / 'inference' / 'framework' / "
        "'two_action_feedback_gate.py').write_text("
        "feedback_gate_source, encoding='utf-8')\n\n"
        f"feedback_gate_helper = {FEEDBACK_HELPER!r}\n"
        "marker = '    def should_stop(self) -> bool:\\n'\n"
        "if marker not in text:\n"
        "    raise RuntimeError('Could not find feedback-gate insertion marker')\n"
        "text = text.replace(marker, feedback_gate_helper + marker, 1)\n"
        "old_hook = '''                if self._try_bounded_reasoning_loop():\n"
        "                    continue\n'''\n"
        "new_hook = old_hook + '''\n"
        "                if self._try_feedback_order_gate():\n"
        "                    continue\n'''\n"
        "if old_hook not in text:\n"
        "    raise RuntimeError('Could not find feedback-gate play hook')\n"
        "text = text.replace(old_hook, new_hook, 1)\n\n"
    )
    patch_cell = patch_cell[:insert_at] + addition + patch_cell[insert_at:]
    set_source(cells[12], patch_cell)

    config = source(cells[16])
    config = config.replace(
        "# EXP-DUCK-034 bounded, prediction-checked Gray-code gate.",
        f"# {experiment_id} isolated feedback-order arm: {arm}.",
        1,
    )
    config = config.replace(
        'DUCK_REPRO_LABEL = "duck-ft09-bounded-gray-reasoner-20260730"',
        f'DUCK_REPRO_LABEL = "duck-ft09-feedback-{arm}-{date_slug}"',
        1,
    )
    bounded_prefix = '''BOUNDED_REASONING_POLICY = {
    "enabled": True,
'''
    if bounded_prefix not in config:
        raise RuntimeError("Could not find bounded-reasoning policy")
    config = config.replace(
        bounded_prefix,
        bounded_prefix.replace('"enabled": True', '"enabled": False'),
        1,
    )
    policy = f'''
FEEDBACK_ORDER_POLICY = {{
    "enabled": True,
    "arm": "{arm}",
    "game_family": "ft09",
    "game_id": "ft09-0d8bbf25",
    "level": 5,
    "action_order": {list(order)!r},
    "feedback_point": [63, 63],
    "feedback_inactive": 12,
    "feedback_active": 11,
    "feedback_active_rules": {list(feedback_active_rules)!r},
    "trace_path": "/kaggle/working/{experiment_id.lower().replace("-", "_")}_{arm}_trace.json",
    "memory": {memory!r},
}}
'''
    config = config.replace("\ntry:\n    bm.label", policy + "\ntry:\n    bm.label", 1)
    attr_marker = (
        "    bm.solver.bounded_reasoning_policy = "
        "dict(BOUNDED_REASONING_POLICY)\n"
    )
    config = config.replace(
        attr_marker,
        attr_marker
        + "    bm.solver.feedback_order_policy = "
        "dict(FEEDBACK_ORDER_POLICY)\n",
        1,
    )
    config = config.replace(
        "bm.solver.max_actions_per_game = 77",
        "bm.solver.max_actions_per_game = 72",
        1,
    )
    required_config = (
        'BOUNDED_REASONING_POLICY = {\n    "enabled": False',
        f'"arm": "{arm}"',
        f'"action_order": {list(order)!r}',
        "bm.solver.feedback_order_policy",
        "bm.solver.max_actions_per_game = 72",
    )
    missing = [token for token in required_config if token not in config]
    if missing:
        raise RuntimeError(f"Feedback policy validation failed: {missing}")
    set_source(cells[16], config)

    notebook.setdefault("metadata", {})["exp_duck_id"] = experiment_id
    notebook["metadata"]["experiment_arm"] = arm
    notebook["metadata"]["experiment_purpose"] = (
        purpose
    )
    notebook["metadata"]["runtime_llm_for_helper"] = False

    compile("class _Helper:\n" + FEEDBACK_HELPER, "<feedback-helper>", "exec")
    for index, cell in enumerate(cells):
        if cell.get("cell_type") == "code":
            compile(
                source(cell),
                f"{output.name}:cell-{index}",
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
    rendered = json.dumps(notebook)
    required = (
        "_try_feedback_order_gate",
        "TwoActionFeedbackController",
        "feedback_order_policy",
        "ARC_COMPETITION_ROOT",
        "runtime_llm=False",
    )
    missing_rendered = [token for token in required if token not in rendered]
    if missing_rendered:
        raise RuntimeError(f"Feedback notebook validation failed: {missing_rendered}")
    output.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")

    metadata = {
        "id": f"jatalepawan/arc-agi-3-duck-ft09-feedback-{arm}",
        "title": f"ARC-AGI-3 Duck ft09 Feedback {arm.title()}",
        "code_file": output.name,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "keywords": ["arc-agi-3", "duck", "ft09", "feedback"],
        "dataset_sources": [
            "driessmit1/arc3-vllm-h100-wheelhouse-v3",
            "jeroencottaar/taaf-kaggle-source-share",
            "driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot",
        ],
        "kernel_sources": [],
        "competition_sources": ["arc-prize-2026-arc-agi-3"],
        "model_sources": [],
        "machine_shape": "NvidiaRtxPro6000",
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return output, metadata_path


def main() -> int:
    for arm, order in ARMS:
        output, metadata = build(arm, order)
        print(output)
        print(metadata)
    print("validated: two private two-action arms; neither launched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
