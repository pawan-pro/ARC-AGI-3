#!/usr/bin/env python3
"""Validate the source-verified tn36 level-3 true-name program."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "artifacts/kaggle/duck_tn36_level3_true_name/latest/benchmark.json"


def main() -> int:
    payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    run = payload["game_runs"][0]
    history = run.get("history", [])
    result = {
        "levels_completed": int(run.get("levels_completed", 0) or 0),
        "actions": len(history),
        "tokens": sum(int(row.get("generated_tokens", 0) or 0) for row in history),
        "actions_per_level": run.get("actions_per_level"),
        "solver_note": run.get("solver_note", ""),
    }
    print(json.dumps(result, indent=2))
    if result["levels_completed"] < 3:
        raise SystemExit("FAIL: true-name program did not reach level 4")
    if result["actions"] != 25 or result["tokens"] != 0:
        raise SystemExit("FAIL: expected exactly 25 actions and zero tokens")
    if "tn36_level3_program=success" not in result["solver_note"]:
        raise SystemExit("FAIL: missing level-3 success note")
    print("PASS: tn36 levels 1-3 solved in 25 deterministic zero-token actions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
