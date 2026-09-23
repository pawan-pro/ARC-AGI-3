#!/usr/bin/env python3
"""Build the isolated EXP-DUCK-037 all-three objective notebook."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260731_duck_ft09_feedback_top-bottom-right.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260731_duck_ft09_all_three_objective.ipynb"
METADATA = PACKAGE_DIR / "kernel-metadata-ft09-all-three-objective.json"
MODEL = ROOT / "experiments/duck_harness_repro/three_action_objective_gate.py"
MEMORY = ROOT / "experiments/duck_harness_repro/exp_duck_034_mechanics_memory.json"
TOP = "ft09-level5-magenta-top"
MIDDLE = "ft09-level5-magenta-middle"
BOTTOM_RIGHT = "ft09-level5-magenta-bottom_right"


OBJECTIVE_HELPER = '''    def _objective_confirmation_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "objective_confirmation_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        if str(policy.get("game_id")) != game_id:
            return {}
        return policy

    def _try_objective_confirmation_gate(self) -> bool:
        policy = self._objective_confirmation_policy()
        if not policy or _level_number(self.game) != int(policy.get("level", -1)):
            return False
        if bool(getattr(self, "_objective_confirmation_tried", False)):
            return False
        self._objective_confirmation_tried = True

        from pathlib import Path
        from .bounded_reasoning_loop import MechanicsMemory, ReasoningContext
        from .three_action_objective_gate import (
            ThreeActionObjectiveController,
            ThresholdFeedbackHypothesis,
        )

        run = self.game.game_run
        initial = _grid_from_state(self.game.current_state)
        try:
            controller = ThreeActionObjectiveController(
                memory=MechanicsMemory.from_dict(dict(policy["memory"])),
                context=ReasoningContext(
                    game_family=str(policy["game_family"]),
                    game_id=str(policy["game_id"]),
                    level=int(policy["level"]),
                ),
                initial_board=initial,
                action_order=tuple(policy["action_order"]),
                feedback=ThresholdFeedbackHypothesis(
                    point=tuple(policy["feedback_point"]),
                    inactive_value=int(policy["feedback_inactive"]),
                    active_value=int(policy["feedback_active"]),
                    activation_threshold=int(policy["feedback_threshold"]),
                ),
            )
        except Exception as exc:
            note = (
                "objective_confirmation=rejected_before_action; "
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
                batch_size=3,
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
        trace = controller.trace_dict()
        note = (
            "objective_confirmation=attempted; runtime_llm=False; "
            f"planned=3; executed={len(controller.records)}; "
            f"supported={controller.objective_supported}; "
            f"stop={controller.stop_reason}; trace={trace_path.name}"
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


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    model_source = MODEL.read_text(encoding="utf-8")
    memory = json.loads(MEMORY.read_text(encoding="utf-8"))

    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck All-Three Objective Confirmation\n\n"
        "EXP-DUCK-037 replays the validated ft09 levels 1-4 prefix, then "
        "executes only top, middle, and bottom-right. It accepts level "
        "completion only after click three and otherwise stops on the exact "
        "predicted nonterminal board. No runtime LLM is used.\n",
    )

    patch_cell = source(cells[12])
    write_marker = 'solver_py.write_text(text, encoding="utf-8")'
    insert_at = patch_cell.index(write_marker)
    addition = (
        "# EXP-DUCK-037: all-three objective confirmation.\n"
        f"objective_gate_source = {model_source!r}\n"
        "(PATCH_REPO / 'inference' / 'framework' / "
        "'three_action_objective_gate.py').write_text("
        "objective_gate_source, encoding='utf-8')\n\n"
        f"objective_gate_helper = {OBJECTIVE_HELPER!r}\n"
        "marker = '    def should_stop(self) -> bool:\\n'\n"
        "if marker not in text:\n"
        "    raise RuntimeError('Could not find objective-gate insertion marker')\n"
        "text = text.replace(marker, objective_gate_helper + marker, 1)\n"
        "old_hook = '''                if self._try_feedback_order_gate():\n"
        "                    continue\n'''\n"
        "new_hook = old_hook + '''\n"
        "                if self._try_objective_confirmation_gate():\n"
        "                    continue\n'''\n"
        "if old_hook not in text:\n"
        "    raise RuntimeError('Could not find objective-gate play hook')\n"
        "text = text.replace(old_hook, new_hook, 1)\n\n"
    )
    patch_cell = patch_cell[:insert_at] + addition + patch_cell[insert_at:]
    set_source(cells[12], patch_cell)

    config = source(cells[16])
    config = config.replace(
        "# EXP-DUCK-036 isolated feedback-order arm: top-bottom-right.",
        "# EXP-DUCK-037 isolated all-three objective confirmation.",
        1,
    )
    config = config.replace(
        'DUCK_REPRO_LABEL = "duck-ft09-feedback-top-bottom-right-20260731"',
        'DUCK_REPRO_LABEL = "duck-ft09-all-three-objective-20260731"',
        1,
    )
    feedback_prefix = '''FEEDBACK_ORDER_POLICY = {
    "enabled": True,
'''
    if feedback_prefix not in config:
        raise RuntimeError("Could not find feedback-order policy")
    config = config.replace(
        feedback_prefix,
        feedback_prefix.replace('"enabled": True', '"enabled": False'),
        1,
    )
    policy = f'''
OBJECTIVE_CONFIRMATION_POLICY = {{
    "enabled": True,
    "game_family": "ft09",
    "game_id": "ft09-0d8bbf25",
    "level": 5,
    "action_order": {[TOP, MIDDLE, BOTTOM_RIGHT]!r},
    "feedback_point": [63, 63],
    "feedback_inactive": 12,
    "feedback_active": 11,
    "feedback_threshold": 2,
    "trace_path": "/kaggle/working/exp_duck_037_objective_trace.json",
    "memory": {memory!r},
}}
'''
    config = config.replace("\ntry:\n    bm.label", policy + "\ntry:\n    bm.label", 1)
    attr_marker = (
        "    bm.solver.feedback_order_policy = "
        "dict(FEEDBACK_ORDER_POLICY)\n"
    )
    if attr_marker not in config:
        raise RuntimeError("Could not find feedback-order solver attribute")
    config = config.replace(
        attr_marker,
        attr_marker
        + "    bm.solver.objective_confirmation_policy = "
        "dict(OBJECTIVE_CONFIRMATION_POLICY)\n",
        1,
    )
    required_config = (
        'FEEDBACK_ORDER_POLICY = {\n    "enabled": False',
        'OBJECTIVE_CONFIRMATION_POLICY = {\n    "enabled": True',
        f'"action_order": {[TOP, MIDDLE, BOTTOM_RIGHT]!r}',
        '"feedback_threshold": 2',
        "bm.solver.max_actions_per_game = 72",
    )
    missing = [token for token in required_config if token not in config]
    if missing:
        raise RuntimeError(f"Objective policy validation failed: {missing}")
    set_source(cells[16], config)

    notebook.setdefault("metadata", {})["exp_duck_id"] = "EXP-DUCK-037"
    notebook["metadata"]["experiment_arm"] = "all-three-objective"
    notebook["metadata"]["experiment_purpose"] = (
        "single three-click objective confirmation"
    )
    notebook["metadata"]["runtime_llm_for_helper"] = False

    compile("class _Helper:\n" + OBJECTIVE_HELPER, "<objective-helper>", "exec")
    for index, cell in enumerate(cells):
        if cell.get("cell_type") == "code":
            compile(
                source(cell),
                f"{OUTPUT.name}:cell-{index}",
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
    rendered = json.dumps(notebook)
    required = (
        "_try_objective_confirmation_gate",
        "ThreeActionObjectiveController",
        "objective_confirmation_policy",
        "ARC_COMPETITION_ROOT",
        "runtime_llm=False",
    )
    missing_rendered = [token for token in required if token not in rendered]
    if missing_rendered:
        raise RuntimeError(
            f"Objective notebook validation failed: {missing_rendered}"
        )
    OUTPUT.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")

    metadata = {
        "id": "jatalepawan/arc-agi-3-duck-ft09-all-three-objective",
        "title": "ARC-AGI-3 Duck ft09 All-Three Objective",
        "code_file": OUTPUT.name,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "keywords": ["arc-agi-3", "duck", "ft09", "objective"],
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
    METADATA.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)
    print(METADATA)
    print("validated: one private three-click objective arm; not launched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
