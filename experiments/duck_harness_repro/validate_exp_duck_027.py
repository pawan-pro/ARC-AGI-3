#!/usr/bin/env python3
"""Validate isolated EXP-DUCK-027 tu93 level-1-to-3 routes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TU93 = "tu93-0768757b"
EXPECTED_ACTIONS = [
    "RIGHT", "DOWN", "DOWN", "RIGHT", "UP", "RIGHT", "DOWN", "DOWN",
    "LEFT", "LEFT", "DOWN", "RIGHT", "RIGHT", "DOWN", "RIGHT", "UP",
    "RIGHT", "DOWN",
    "UP", "RIGHT", "RIGHT", "DOWN", "RIGHT", "RIGHT", "UP", "RIGHT",
    "RIGHT", "UP",
    "UP", "UP", "RIGHT", "UP", "LEFT", "LEFT", "UP", "LEFT", "LEFT",
    "DOWN", "RIGHT", "DOWN", "LEFT", "LEFT", "LEFT", "DOWN", "RIGHT",
    "DOWN", "RIGHT",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark", type=Path)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    benchmark = json.loads(args.benchmark.read_text(encoding="utf-8"))
    runs = benchmark.get("game_runs", [])
    run = runs[0] if len(runs) == 1 else {}
    note = str(run.get("solver_note") or "")
    event_path = args.candidate_root / "artifacts" / f"{TU93}_p0_events.jsonl"
    events = [
        json.loads(line)
        for line in event_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ] if event_path.exists() else []
    actions = [
        event.get("action_display")
        for event in events
        if event.get("type") == "action"
    ]
    analyses = [event for event in events if event.get("type") == "analysis"]
    checks = {
        "one_target_game": len(runs) == 1 and run.get("game_id") == TU93,
        "three_levels": int(run.get("levels_completed") or 0) >= 3,
        "exact_47_action_route": actions == EXPECTED_ACTIONS,
        "zero_analysis_events": len(analyses) == 0,
        "level1_success": "tu93_route=success; level=1; helper_actions=18" in note,
        "level2_success": "tu93_route=success; level=2; helper_actions=10" in note,
        "level3_success": "tu93_route=success; level=3; helper_actions=19" in note,
    }
    result = {
        "checks": checks,
        "details": {
            "levels_completed": int(run.get("levels_completed") or 0),
            "actions": len(actions),
            "analysis_events": len(analyses),
            "solver_note": note,
        },
        "structural_pass": all(checks.values()),
        "recommended_integration": all(checks.values()),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["structural_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
