#!/usr/bin/env python3
"""Build the unlaunched EXP-DUCK-034 bounded Gray-code notebook."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260729_duck_ft09_level5_probe_bottom-right.ipynb"
OUTPUT = PACKAGE_DIR / "arc3_20260730_duck_ft09_bounded_gray_reasoner.ipynb"
METADATA = PACKAGE_DIR / "kernel-metadata-ft09-bounded-gray-reasoner.json"
MODEL = ROOT / "experiments/duck_harness_repro/bounded_reasoning_loop.py"
MEMORY = ROOT / "experiments/duck_harness_repro/exp_duck_034_mechanics_memory.json"


REASONING_HELPER = '''    def _bounded_reasoning_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "bounded_reasoning_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        if str(policy.get("game_id")) != game_id:
            return {}
        return policy

    def _try_bounded_reasoning_loop(self) -> bool:
        policy = self._bounded_reasoning_policy()
        if not policy or _level_number(self.game) != int(policy.get("level", -1)):
            return False
        if bool(getattr(self, "_bounded_reasoning_tried", False)):
            return False
        self._bounded_reasoning_tried = True

        from pathlib import Path
        from .bounded_reasoning_loop import (
            BoundedReasoningController,
            MechanicsMemory,
            ReasoningContext,
        )

        run = self.game.game_run
        initial = _grid_from_state(self.game.current_state)
        try:
            memory = MechanicsMemory.from_dict(dict(policy["memory"]))
            controller = BoundedReasoningController.from_memory(
                memory=memory,
                context=ReasoningContext(
                    game_family=str(policy["game_family"]),
                    game_id=str(policy["game_id"]),
                    level=int(policy["level"]),
                ),
                initial_board=initial,
                selected_hypothesis=str(
                    policy.get("selected_hypothesis", "binary-xor")
                ),
                max_actions=int(policy.get("max_actions", 7)),
            )
        except Exception as exc:
            note = (
                "bounded_reasoning=rejected_before_action; "
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
                batch_size=controller.max_actions,
                generated_tokens=0,
                flush_viewer_payload=False,
            )
            observed = _grid_from_state(self.game.current_state)
            controller.observe(
                observed,
                level_completed=bool(payload.get("level_completed")),
                game_over=bool(payload.get("game_over")),
                run_complete=bool(payload.get("run_complete")),
            )

        trace_path = Path(
            str(
                policy.get(
                    "trace_path",
                    "/kaggle/working/exp_duck_034_reasoning_trace.json",
                )
            )
        )
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        controller.save_trace(trace_path)
        memory_path = Path(
            str(
                policy.get(
                    "memory_output_path",
                    "/kaggle/working/exp_duck_034_mechanics_memory_observed.json",
                )
            )
        )
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        controller.memory_snapshot().save(memory_path)
        trace = controller.trace_dict()
        hypothesis_state = controller.hypotheses[controller.selected_hypothesis]
        note = (
            "bounded_reasoning=attempted; runtime_llm=False; "
            f"candidates={len(controller.matches)}; "
            f"hypotheses={len(controller.hypotheses)}; "
            f"selected={controller.selected_hypothesis}; "
            f"planned={len(controller.plan)}; "
            f"executed={len(controller.records)}; "
            f"verified={hypothesis_state.verified_steps}; "
            f"stop={controller.stop_reason}; trace={trace_path.name}; "
            f"memory={memory_path.name}"
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
    memory = json.loads(MEMORY.read_text(encoding="utf-8"))
    model_source = MODEL.read_text(encoding="utf-8")

    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck Bounded Mechanics Reasoner\n\n"
        "EXP-DUCK-034 replays the validated ft09 levels 1-4 prefix, retrieves "
        "three forward-only action-effect rules from EXP-DUCK-033, proposes "
        "set and reversible-XOR hypotheses, and prospectively tests the XOR "
        "hypothesis through at most seven Gray-code actions. Every complete "
        "board transition is checked. No runtime LLM is used.\n",
    )

    patch_cell = source(cells[12])
    write_marker = 'solver_py.write_text(text, encoding="utf-8")'
    insert_at = patch_cell.index(write_marker)
    addition = (
        "# EXP-DUCK-034: bounded mechanics reasoning loop.\n"
        f"bounded_reasoning_source = {model_source!r}\n"
        "(PATCH_REPO / 'inference' / 'framework' / "
        "'bounded_reasoning_loop.py').write_text("
        "bounded_reasoning_source, encoding='utf-8')\n\n"
        f"bounded_reasoning_helper = {REASONING_HELPER!r}\n"
        "marker = '    def should_stop(self) -> bool:\\n'\n"
        "if marker not in text:\n"
        "    raise RuntimeError('Could not find bounded-reasoning insertion marker')\n"
        "text = text.replace(marker, bounded_reasoning_helper + marker, 1)\n"
        "old_hook = '''                if self._try_ft09_level5_magenta_probe():\n"
        "                    continue\n'''\n"
        "new_hook = old_hook + '''\n"
        "                if self._try_bounded_reasoning_loop():\n"
        "                    continue\n'''\n"
        "if old_hook not in text:\n"
        "    raise RuntimeError('Could not find bounded-reasoning play hook')\n"
        "text = text.replace(old_hook, new_hook, 1)\n\n"
    )
    patch_cell = patch_cell[:insert_at] + addition + patch_cell[insert_at:]
    set_source(cells[12], patch_cell)

    config = source(cells[16])
    config = config.replace(
        "# EXP-DUCK-033 isolated magenta probe: bottom_right.",
        "# EXP-DUCK-034 bounded, prediction-checked Gray-code gate.",
        1,
    )
    config = config.replace(
        'DUCK_REPRO_LABEL = "duck-ft09-level5-probe-bottom-right-20260729"',
        'DUCK_REPRO_LABEL = "duck-ft09-bounded-gray-reasoner-20260730"',
        1,
    )
    probe_block = '''FT09_LEVEL5_MAGENTA_PROBE_POLICY = {
    "enabled": True,
    "game_id": "ft09-0d8bbf25",
    "level": 5,
    "arm": "bottom_right",
    "row": 46,
    "col": 40,
}
'''
    if probe_block not in config:
        raise RuntimeError("Could not find EXP-DUCK-033 probe policy")
    config = config.replace(
        probe_block,
        probe_block.replace('"enabled": True', '"enabled": False'),
        1,
    )
    reasoning_policy = f'''
BOUNDED_REASONING_POLICY = {{
    "enabled": True,
    "game_family": "ft09",
    "game_id": "ft09-0d8bbf25",
    "level": 5,
    "selected_hypothesis": "binary-xor",
    "max_actions": 7,
    "trace_path": "/kaggle/working/exp_duck_034_reasoning_trace.json",
    "memory_output_path": "/kaggle/working/exp_duck_034_mechanics_memory_observed.json",
    "memory": {memory!r},
}}
'''
    config = config.replace("\ntry:\n    bm.label", reasoning_policy + "\ntry:\n    bm.label", 1)
    attr_marker = (
        "    bm.solver.ft09_level5_magenta_probe_policy = "
        "dict(FT09_LEVEL5_MAGENTA_PROBE_POLICY)\n"
    )
    if attr_marker not in config:
        raise RuntimeError("Could not find EXP-DUCK-033 policy assignment")
    config = config.replace(
        attr_marker,
        attr_marker
        + "    bm.solver.bounded_reasoning_policy = "
        "dict(BOUNDED_REASONING_POLICY)\n",
        1,
    )
    config = config.replace(
        "bm.solver.max_actions_per_game = 71",
        "bm.solver.max_actions_per_game = 77",
        1,
    )
    config_required = (
        '"max_actions": 7',
        '"selected_hypothesis": "binary-xor"',
        'FT09_LEVEL5_MAGENTA_PROBE_POLICY = {\n    "enabled": False',
        "bm.solver.bounded_reasoning_policy",
    )
    missing_config = [token for token in config_required if token not in config]
    if missing_config:
        raise RuntimeError(
            f"EXP-DUCK-034 policy validation failed; missing={missing_config}"
        )
    set_source(cells[16], config)

    notebook.setdefault("metadata", {})["exp_duck_id"] = "EXP-DUCK-034"
    notebook["metadata"]["experiment_purpose"] = (
        "bounded prediction-checked mechanics reasoning gate"
    )
    notebook["metadata"]["runtime_llm_for_helper"] = False

    compile("class _Helper:\n" + REASONING_HELPER, "<bounded-reasoner>", "exec")
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
        "_try_bounded_reasoning_loop",
        "BoundedReasoningController",
        "runtime_llm=False",
        "ARC_COMPETITION_ROOT",
    )
    missing = [token for token in required if token not in rendered]
    if missing:
        raise RuntimeError(
            f"EXP-DUCK-034 notebook validation failed; missing={missing}"
        )
    OUTPUT.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")

    metadata = {
        "id": "jatalepawan/arc-agi-3-duck-ft09-bounded-gray-reasoner",
        "title": "ARC-AGI-3 Duck ft09 Bounded Gray Reasoner",
        "code_file": OUTPUT.name,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "keywords": ["arc-agi-3", "duck", "ft09", "bounded-reasoning"],
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
    print("validated: deterministic seven-action maximum; notebook not launched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
