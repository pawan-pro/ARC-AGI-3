#!/usr/bin/env python3
"""Build the three isolated EXP-DUCK-033 ft09 level-5 probe notebooks."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
SOURCE = PACKAGE_DIR / "arc3_20260728_duck_ft09_level5_calibrated.ipynb"

PROBES = (
    ("top", 14, 24),
    ("middle", 30, 24),
    ("bottom_right", 46, 40),
)

PROBE_HELPER = '''    def _ft09_level5_magenta_probe_policy(self) -> dict[str, Any]:
        policy = getattr(self.solver, "ft09_level5_magenta_probe_policy", None)
        if not isinstance(policy, dict) or not policy.get("enabled"):
            return {}
        run = self.game.game_run
        game_id = run.game_id if run is not None else str(self.game_index)
        if str(policy.get("game_id", "ft09-0d8bbf25")) != game_id:
            return {}
        return policy

    def _try_ft09_level5_magenta_probe(self) -> bool:
        policy = self._ft09_level5_magenta_probe_policy()
        if not policy or _level_number(self.game) != int(policy.get("level", 5)):
            return False
        if bool(getattr(self, "_ft09_level5_magenta_probe_tried", False)):
            return False
        self._ft09_level5_magenta_probe_tried = True

        run = self.game.game_run
        row = int(policy["row"])
        col = int(policy["col"])
        arm = str(policy["arm"])
        before = _grid_from_state(self.game.current_state)
        level_before = _level_number(self.game)
        before_color = int(before[row][col])
        action = arcengine.ActionInput(
            id=arcengine.GameAction.ACTION6,
            data={"x": col, "y": row},
        )
        payload = self._execute_action(
            action,
            batch_index=1,
            batch_size=1,
            generated_tokens=0,
            flush_viewer_payload=False,
        )
        after = _grid_from_state(self.game.current_state)
        level_after = _level_number(self.game)
        after_color = int(after[row][col])
        changed = [
            (r, c, int(before[r][c]), int(after[r][c]))
            for r in range(len(before))
            for c in range(len(before[r]))
            if int(before[r][c]) != int(after[r][c])
        ]
        changed_text = "|".join(
            f"{r},{c},{old}>{new}" for r, c, old, new in changed
        ) or "none"
        note = (
            f"ft09_level5_magenta_probe=attempted; arm={arm}; row={row}; col={col}; "
            f"before={before_color}; after={after_color}; changed={len(changed)}; "
            f"changed_cells={changed_text}; level_before={level_before}; "
            f"level_after={level_after}; level_completed={bool(payload.get('level_completed'))}; "
            f"game_over={bool(payload.get('game_over'))}; "
            f"run_complete={bool(payload.get('run_complete'))}"
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


def build(arm: str, row: int, col: int) -> tuple[Path, Path]:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]
    slug = arm.replace("_", "-")
    output = PACKAGE_DIR / f"arc3_20260729_duck_ft09_level5_probe_{slug}.ipynb"
    metadata_path = PACKAGE_DIR / f"kernel-metadata-ft09-level5-probe-{slug}.json"

    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck ft09 Level-5 Magenta Probe\n\n"
        f"EXP-DUCK-033 arm `{arm}` replays validated levels 1-4, clicks only "
        f"the level-5 magenta center at `(row={row}, col={col})`, records the "
        "complete observed effect, and stops.\n",
    )

    patch_cell = source(cells[12])
    write_marker = 'solver_py.write_text(text, encoding="utf-8")'
    insert_at = patch_cell.index(write_marker)
    addition = (
        "# EXP-DUCK-033: one-action magenta mechanic probe.\n"
        f"ft09_level5_magenta_probe = {PROBE_HELPER!r}\n"
        "marker = '    def should_stop(self) -> bool:\\n'\n"
        "if marker not in text:\n"
        "    raise RuntimeError('Could not find magenta probe insertion marker')\n"
        "text = text.replace(marker, ft09_level5_magenta_probe + marker, 1)\n"
        "old_hook = '''                if self._try_ft09_level5_calibrated_helper():\n"
        "                    continue\n'''\n"
        "new_hook = old_hook + '''\n"
        "                if self._try_ft09_level5_magenta_probe():\n"
        "                    continue\n'''\n"
        "if old_hook not in text:\n"
        "    raise RuntimeError('Could not find magenta probe play hook')\n"
        "text = text.replace(old_hook, new_hook, 1)\n\n"
    )
    patch_cell = patch_cell[:insert_at] + addition + patch_cell[insert_at:]
    set_source(cells[12], patch_cell)

    config = source(cells[16])
    config = config.replace(
        "# EXP-DUCK-032 calibrated level-5 operator diagnostic.",
        f"# EXP-DUCK-033 isolated magenta probe: {arm}.",
    )
    config = config.replace(
        'DUCK_REPRO_LABEL = "duck-ft09-level5-calibrated-20260728"',
        f'DUCK_REPRO_LABEL = "duck-ft09-level5-probe-{slug}-20260729"',
    )
    calibrated_block = '''FT09_LEVEL5_CALIBRATED_POLICY = {
    "enabled": True,
    "game_id": "ft09-0d8bbf25",
    "level": 5,
    "stop_after_attempt": True,
}
'''
    disabled_block = calibrated_block.replace('"enabled": True', '"enabled": False')
    if calibrated_block not in config:
        raise RuntimeError("Could not find calibrated policy block")
    config = config.replace(calibrated_block, disabled_block, 1)
    policy = f'''
FT09_LEVEL5_MAGENTA_PROBE_POLICY = {{
    "enabled": True,
    "game_id": "ft09-0d8bbf25",
    "level": 5,
    "arm": "{arm}",
    "row": {row},
    "col": {col},
}}
'''
    config = config.replace("\ntry:\n    bm.label", policy + "\ntry:\n    bm.label", 1)
    attr_marker = (
        "    bm.solver.ft09_level5_calibrated_policy = "
        "dict(FT09_LEVEL5_CALIBRATED_POLICY)\n"
    )
    config = config.replace(
        attr_marker,
        attr_marker
        + "    bm.solver.ft09_level5_magenta_probe_policy = "
        "dict(FT09_LEVEL5_MAGENTA_PROBE_POLICY)\n",
        1,
    )
    print_marker = (
        '    print("ft09 level-5 calibrated policy:", '
        "json.dumps(bm.solver.ft09_level5_calibrated_policy, sort_keys=True))\n"
    )
    config = config.replace(
        print_marker,
        print_marker
        + '    print("ft09 level-5 magenta probe policy:", '
        "json.dumps(bm.solver.ft09_level5_magenta_probe_policy, sort_keys=True))\n",
        1,
    )
    config = config.replace(
        "bm.solver.max_actions_per_game = 90",
        "bm.solver.max_actions_per_game = 71",
        1,
    )
    set_source(cells[16], config)

    if arm == "bottom_right":
        install_cell = source(cells[6])
        old_wheel_path = (
            '        "/kaggle/input/competitions/arc-prize-2026-arc-agi-3/'
            'arc_agi_3_wheels",'
        )
        resolver = '''ARC_COMPETITION_ROOT = next(
    (
        path
        for path in (
            Path("/kaggle/input/competitions/arc-prize-2026-arc-agi-3"),
            Path("/kaggle/input/arc-prize-2026-arc-agi-3"),
        )
        if (path / "arc_agi_3_wheels").exists()
    ),
    None,
)
if ARC_COMPETITION_ROOT is None:
    raise RuntimeError("ARC competition wheels are not mounted")
ARC_WHEEL_DIR = ARC_COMPETITION_ROOT / "arc_agi_3_wheels"
print("Resolved ARC competition root:", ARC_COMPETITION_ROOT)

'''
        if old_wheel_path not in install_cell:
            raise RuntimeError("Could not find fixed ARC wheel path")
        install_cell = resolver + install_cell.replace(
            old_wheel_path, "        str(ARC_WHEEL_DIR),", 1
        )
        set_source(cells[6], install_cell)

        run_cell = source(cells[19])
        old_env_path = (
            'competition_env_files = str(Path("/kaggle/input/competitions/'
            'arc-prize-2026-arc-agi-3/arc_agi_3_wheels").parent / '
            '"environment_files")'
        )
        if old_env_path not in run_cell:
            raise RuntimeError("Could not find fixed ARC environment path")
        run_cell = run_cell.replace(
            old_env_path,
            'competition_env_files = str(ARC_COMPETITION_ROOT / "environment_files")',
            1,
        )
        set_source(cells[19], run_cell)

    notebook.setdefault("metadata", {})["exp_duck_id"] = "EXP-DUCK-033"
    notebook["metadata"]["experiment_arm"] = arm
    notebook["metadata"]["experiment_purpose"] = (
        "single-action ft09 level-5 magenta mechanic probe"
    )

    compile("class _Helper:\n" + PROBE_HELPER, "<magenta-probe>", "exec")
    for index, cell in enumerate(cells):
        if cell.get("cell_type") == "code":
            compile(
                source(cell),
                f"{output.name}:cell-{index}",
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
    rendered = "\n".join(source(cell) for cell in cells)
    required = (
        "_try_ft09_level5_magenta_probe",
        f'"arm": "{arm}"',
        f'"row": {row}',
        f'"col": {col}',
        '"enabled": False',
    )
    if arm == "bottom_right":
        required += ("ARC_COMPETITION_ROOT", "ARC_WHEEL_DIR")
    if not all(token in rendered for token in required):
        raise RuntimeError(f"Notebook validation failed for {arm}")
    output.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")

    metadata = {
        "id": f"jatalepawan/arc-agi-3-duck-ft09-level-5-probe-{slug}",
        "title": f"ARC-AGI-3 Duck ft09 Level 5 Probe {arm.replace('_', ' ').title()}",
        "code_file": output.name,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "keywords": ["arc-agi-3", "duck", "ft09", "probe"],
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
    for probe in PROBES:
        output, metadata = build(*probe)
        print(output)
        print(metadata)
    print("validated: three independent one-click level-5 magenta probe arms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
