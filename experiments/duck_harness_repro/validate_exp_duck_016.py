#!/usr/bin/env python3
"""Validate the isolated tn36 level-2 matrix-helper result."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "artifacts/kaggle/duck_tn36_level2_matrix/latest/benchmark.json"
TARGET = "tn36-ef4dde99"


def main() -> int:
    payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    runs = [row for row in payload["game_runs"] if row["game_id"] == TARGET]
    if len(runs) != 1:
        raise SystemExit(f"FAIL: expected one tn36 run, found {len(runs)}")
    run = runs[0]
    actions = len(run.get("history", []))
    tokens = sum(int(row.get("generated_tokens", 0) or 0) for row in run.get("history", []))
    result = {
        "levels_completed": int(run.get("levels_completed", 0) or 0),
        "actions": actions,
        "tokens": tokens,
        "actions_per_level": run.get("actions_per_level"),
        "solver_note": run.get("solver_note", ""),
    }
    print(json.dumps(result, indent=2))
    if result["levels_completed"] < 2:
        raise SystemExit("FAIL: level-2 helper did not reach level 3")
    if actions != 12:
        raise SystemExit(f"FAIL: expected exactly 12 actions, got {actions}")
    if tokens != 0:
        raise SystemExit(f"FAIL: expected zero generated tokens, got {tokens}")
    if "tn36_level2_helper=success" not in result["solver_note"]:
        raise SystemExit("FAIL: missing level-2 helper success note")
    print("PASS: tn36 levels 1 and 2 solved deterministically in 12 actions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
