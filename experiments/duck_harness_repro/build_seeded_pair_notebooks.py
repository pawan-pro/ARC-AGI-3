#!/usr/bin/env python3
"""Build matched seeded Duck notebooks with and without the tn36 helper."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
EXPERIMENT_DIR = Path(__file__).parent
CONTROL_SOURCE = PACKAGE_DIR / "arc3_20260704_duck_public_repro_full_eval_overlap.ipynb"
CANDIDATE_SOURCE = PACKAGE_DIR / "arc3_20260721_duck_full_eval_ft09_tn36.ipynb"
CONTROL_OUTPUT = PACKAGE_DIR / "arc3_20260722_duck_seeded_pair_control.ipynb"
CANDIDATE_OUTPUT = PACKAGE_DIR / "arc3_20260722_duck_seeded_pair_tn36.ipynb"

TARGET_GAMES = [
    "ft09-0d8bbf25",
    "tn36-ef4dde99",
    "ar25-0c556536",
    "cd82-fb555c5d",
    "cn04-2fe56bfb",
    "r11l-495a7899",
    "vc33-5430563c",
    "m0r0-492f87ba",
]
SEED_SALT = "exp-duck-015-paired-v1"


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, value: str) -> None:
    cell["source"] = value.splitlines(keepends=True)


def deterministic_seed_patch(module_source: str) -> str:
    return f"""# EXP-DUCK-015: scheduling-independent per-game request seeds.
seed_module_py = PATCH_REPO / "inference" / "agent" / "deterministic_request_seed.py"
seed_module_py.write_text({module_source!r}, encoding="utf-8")

tool_agent_py = PATCH_REPO / "inference" / "agent" / "tool_agent.py"
tool_text = tool_agent_py.read_text(encoding="utf-8")
seed_import = "from inference.agent.deterministic_request_seed import RequestSeedSequence\\n"
import_anchor = "from inference.agent.action_names import to_engine_action, to_model_action\\n"
if seed_import not in tool_text:
    if import_anchor not in tool_text:
        raise RuntimeError("Could not add deterministic seed import.")
    tool_text = tool_text.replace(import_anchor, seed_import + import_anchor, 1)

signature_anchor = "        provider: str | None = None,\\n    ) -> None:"
signature_replacement = "        provider: str | None = None,\\n        seed_namespace: str | None = None,\\n    ) -> None:"
if signature_anchor not in tool_text:
    raise RuntimeError("Could not add ToolAgent seed namespace.")
tool_text = tool_text.replace(signature_anchor, signature_replacement, 1)

state_anchor = "        self._save_request_logs = bool(save_request_logs)\\n"
state_replacement = state_anchor + '''        self._request_seed_sequence = RequestSeedSequence(
            seed_namespace,
            salt=os.environ.get("LOCAL_ANALYZER_SEED_SALT", "exp-duck-paired-v1"),
            fallback_seed=_LOCAL_ANALYZER_SEED,
        )
'''
if state_anchor not in tool_text:
    raise RuntimeError("Could not initialize deterministic request seeds.")
tool_text = tool_text.replace(state_anchor, state_replacement, 1)

seed_anchor = "            seed=_LOCAL_ANALYZER_SEED,\\n"
seed_replacement = "            seed=self._request_seed_sequence.next_seed(),\\n"
if seed_anchor not in tool_text:
    raise RuntimeError("Could not route request seed through the per-game sequence.")
tool_text = tool_text.replace(seed_anchor, seed_replacement, 1)
tool_agent_py.write_text(tool_text, encoding="utf-8")

solver_text = solver_py.read_text(encoding="utf-8")
solver_anchor = '            provider="vllm" if local_server is not None else None,\\n        )'
solver_replacement = '''            provider="vllm" if local_server is not None else None,
            seed_namespace=(
                game.game_run.game_id
                if game.game_run is not None
                else str(index)
            ),
        )'''
if solver_anchor not in solver_text:
    raise RuntimeError("Could not pass the game id to ToolAgent.")
solver_text = solver_text.replace(solver_anchor, solver_replacement, 1)
solver_py.write_text(solver_text, encoding="utf-8")

for module_name in [
    "inference.agent.deterministic_request_seed",
    "inference.agent.tool_agent",
    "inference.framework.solver",
]:
    sys.modules.pop(module_name, None)
print("Enabled deterministic per-game request seeds.")
"""


def configure(notebook: dict, *, candidate: bool) -> None:
    cells = notebook["cells"]
    title = "candidate with tn36 helper" if candidate else "control without tn36 helper"
    set_source(
        cells[0],
        "# ARC-AGI-3 - Seeded Paired Duck Evaluation\n\n"
        f"**EXP-DUCK-015 {'B' if candidate else 'A'}:** {title}.\n\n"
        "Both notebooks use the same per-game request seeds. This isolates the tn36 "
        "helper from unrelated LLM sampling changes.\n",
    )

    module_source = (EXPERIMENT_DIR / "deterministic_request_seed.py").read_text(
        encoding="utf-8"
    )
    set_source(cells[12], source(cells[12]) + "\n\n" + deterministic_seed_patch(module_source))

    config = source(cells[16])
    old_label = (
        'DUCK_REPRO_LABEL = "duck-full-eval-ft09-tn36-20260721"'
        if candidate
        else 'DUCK_REPRO_LABEL = "duck-full-eval-ft09-overlap-20260717"'
    )
    new_label = (
        'DUCK_REPRO_LABEL = "duck-seeded-pair-tn36-20260722"'
        if candidate
        else 'DUCK_REPRO_LABEL = "duck-seeded-pair-control-20260722"'
    )
    if old_label not in config:
        raise RuntimeError(f"Missing source label: {old_label}")
    config = config.replace(old_label, new_label, 1)
    config = config.replace("LIMIT_TO_GAME_IDS = []", f"LIMIT_TO_GAME_IDS = {TARGET_GAMES!r}", 1)
    config = (
        f'os.environ["LOCAL_ANALYZER_SEED_SALT"] = {SEED_SALT!r}\n' + config
    )
    set_source(cells[16], config)

    experiment_id = "EXP-DUCK-015B" if candidate else "EXP-DUCK-015A"
    notebook.setdefault("metadata", {})["experiment_id"] = experiment_id
    notebook["metadata"]["experiment_purpose"] = title
    notebook["metadata"]["seed_salt"] = SEED_SALT


def write_notebook(source_path: Path, output_path: Path, *, candidate: bool) -> None:
    notebook = json.loads(source_path.read_text(encoding="utf-8"))
    configure(notebook, candidate=candidate)
    for index, cell in enumerate(notebook["cells"]):
        if cell.get("cell_type") == "code":
            compile(
                source(cell),
                f"{output_path.name}:cell-{index}",
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
    output_path.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    print(output_path)


def main() -> int:
    write_notebook(CONTROL_SOURCE, CONTROL_OUTPUT, candidate=False)
    write_notebook(CANDIDATE_SOURCE, CANDIDATE_OUTPUT, candidate=True)
    print(f"selected_games={len(TARGET_GAMES)} seed_salt={SEED_SALT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
