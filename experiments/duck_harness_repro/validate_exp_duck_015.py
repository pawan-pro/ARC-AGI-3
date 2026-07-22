#!/usr/bin/env python3
"""Validate the matched EXP-DUCK-015 control and tn36 candidate outputs."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT / "artifacts/kaggle/duck_seeded_pair_control/latest/benchmark.json"
CANDIDATE = ROOT / "artifacts/kaggle/duck_seeded_pair_tn36/latest/benchmark.json"
TARGET = "tn36-ef4dde99"


def load(path: Path) -> dict[str, dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {row["game_id"]: row for row in payload["game_runs"]}


def signature(row: dict) -> dict:
    return {
        "levels_completed": int(row.get("levels_completed", 0) or 0),
        "final_score": float(row.get("final_score", 0.0) or 0.0),
        "actions": [entry.get("action") for entry in row.get("history", [])],
        "tokens": [int(entry.get("generated_tokens", 0) or 0) for entry in row.get("history", [])],
    }


def main() -> int:
    control = load(CONTROL)
    candidate = load(CANDIDATE)
    if set(control) != set(candidate):
        raise SystemExit("FAIL: paired runs selected different games")

    drift = [
        game_id
        for game_id in sorted(control)
        if game_id != TARGET and signature(control[game_id]) != signature(candidate[game_id])
    ]
    target_control = signature(control[TARGET])
    target_candidate = signature(candidate[TARGET])
    print(json.dumps({
        "non_target_games": len(control) - 1,
        "non_target_drift": drift,
        "tn36_control_levels": target_control["levels_completed"],
        "tn36_candidate_levels": target_candidate["levels_completed"],
        "tn36_control_actions": len(target_control["actions"]),
        "tn36_candidate_actions": len(target_candidate["actions"]),
    }, indent=2))
    if drift:
        raise SystemExit("FAIL: fixed-seed non-target trajectories drifted")
    if target_candidate["levels_completed"] < target_control["levels_completed"]:
        raise SystemExit("FAIL: tn36 helper lost level progress")
    print("PASS: non-target trajectories match; tn36 comparison is isolated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
