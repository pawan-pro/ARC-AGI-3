#!/usr/bin/env python3
"""Build EXP-DUCK-027: isolated tu93 level-1-to-3 route validation."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from build_tu93_route_helper_notebook import (
    HELPER,
    PACKAGE_DIR,
    SOURCE,
    helper_patch,
    set_source,
    source,
)


OUTPUT = PACKAGE_DIR / "arc3_20260727_duck_tu93_level3_route.ipynb"

CONFIG = '''# EXP-DUCK-027 isolated tu93 level-1-to-3 route validation.
DUCK_REPRO_LABEL = "duck-tu93-level3-route-20260727"
LIMIT_TO_GAME_IDS = ["tu93-0768757b"]
MAX_GAMES_FOR_DEBUG = None

TU93_ROUTE_POLICY = {
    "enabled": True,
    "target_game_ids": LIMIT_TO_GAME_IDS,
    "target_level": 3,
}

bm.label = f"{getattr(bm, 'label', 'duck')}-{DUCK_REPRO_LABEL}"
bm.solver.controlled_stall_policy = {"enabled": False}
bm.solver.tu93_route_policy = dict(TU93_ROUTE_POLICY)
bm.solver.max_actions_per_game = 49
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
    print(f"Filtered games after game-list construction: {original_n_games} -> {len(filtered)}")
    print("Selected games:", [_game_id(g) for g in filtered])
    return filtered
'''


def main() -> int:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    helper_source = HELPER.read_text(encoding="utf-8")
    cells = notebook["cells"]
    set_source(
        cells[0],
        "# ARC-AGI-3 - Duck tu93 Level-3 Route\n\n"
        "**Experiment:** EXP-DUCK-027\n\n"
        "Replay the independently validated routes for levels 1-2, then apply "
        "the 19-action level-3 route found by breadth-first search against the "
        "official `tu93.py` source and `arcengine==0.9.3`. No LLM call is made.\n",
    )
    patch = source(cells[12])
    set_source(cells[12], patch + "\n\n" + helper_patch(helper_source))
    set_source(cells[16], CONFIG)
    notebook.setdefault("metadata", {})["experiment_id"] = "EXP-DUCK-027"
    notebook["metadata"]["experiment_purpose"] = (
        "isolated signature-gated tu93 levels 1-3 route validation"
    )

    all_source = "\n".join(source(cell) for cell in cells)
    checks = {
        "one_game": 'LIMIT_TO_GAME_IDS = ["tu93-0768757b"]' in all_source,
        "target_level": '"target_level": 3' in all_source,
        "level3_signature": "0x936EEEB5" in all_source,
        "level3_route": all_source.count('"ACTION1"') >= 6,
        "zero_tokens": "generated_tokens=0" in all_source,
        "action_limit": "max_actions_per_game = 49" in all_source,
    }
    if not all(checks.values()):
        raise RuntimeError(f"EXP-DUCK-027 wiring checks failed: {checks}")

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
    print("games=1 target=tu93 expected_levels=3 expected_actions=47 expected_tokens=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
