#!/usr/bin/env python3
"""Validate the targeted Duck continuation after the tn36 two-level prefix."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "artifacts/kaggle/duck_tn36_level3_continuation/latest/benchmark.json"
TARGET = "tn36-ef4dde99"


def main() -> int:
    payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    runs = [row for row in payload["game_runs"] if row["game_id"] == TARGET]
    if len(runs) != 1:
        raise SystemExit(f"FAIL: expected one tn36 run, found {len(runs)}")
    run = runs[0]
    history = run.get("history", [])
    result = {
        "levels_completed": int(run.get("levels_completed", 0) or 0),
        "actions": len(history),
        "tokens": sum(int(row.get("generated_tokens", 0) or 0) for row in history),
        "actions_per_level": run.get("actions_per_level"),
        "solver_note": run.get("solver_note", ""),
    }
    print(json.dumps(result, indent=2))
    if result["levels_completed"] < 2:
        raise SystemExit("FAIL: deterministic prefix did not preserve two levels")
    if result["actions"] <= 16 or result["tokens"] <= 0:
        raise SystemExit("FAIL: unchanged Duck did not continue from level 3")
    if "tn36_level2_program=success" not in result["solver_note"]:
        raise SystemExit("FAIL: missing validated level-2 success note")
    print("PASS: deterministic two-level prefix preserved and Duck continued from level 3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
