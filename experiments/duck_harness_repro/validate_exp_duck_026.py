#!/usr/bin/env python3
"""Validate EXP-DUCK-026 against the scored EXP-DUCK-024 benchmark."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TU93 = "tu93-0768757b"
TN36 = "tn36-ef4dde99"
FT09 = "ft09-0d8bbf25"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def runs_by_id(benchmark: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(run["game_id"]): run for run in benchmark.get("game_runs", [])}


def aggregate(runs: dict[str, dict[str, Any]], field: str) -> float:
    return sum(float(run.get(field) or 0) for run in runs.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    base_runs = runs_by_id(load(args.baseline))
    runs = runs_by_id(load(args.candidate))
    ft09 = runs.get(FT09, {})
    tn36 = runs.get(TN36, {})
    tu93 = runs.get(TU93, {})
    tu93_note = str(tu93.get("solver_note") or "")

    event_path = args.candidate_root / "artifacts" / f"{TU93}_p0_events.jsonl"
    events = [
        json.loads(line)
        for line in event_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ] if event_path.exists() else []
    actions = [event for event in events if event.get("type") == "action"]
    analyses = [event for event in events if event.get("type") == "analysis"]
    duck_actions_match = re.search(
        r"tu93_postlude=start;[^;]*; duck_actions=(\d+)", tu93_note
    )
    duck_actions = int(duck_actions_match.group(1)) if duck_actions_match else None
    first_postlude_action = (
        actions[duck_actions]
        if duck_actions is not None and duck_actions < len(actions)
        else {}
    )

    checks = {
        "same_game_ids": set(base_runs) == set(runs),
        "expected_25_games": len(runs) == 25,
        "ft09_preserved": int(ft09.get("levels_completed") or 0) >= 4,
        "tn36_preserved": int(tn36.get("levels_completed") or 0) >= 3,
        "tu93_two_levels": int(tu93.get("levels_completed") or 0) >= 2,
        "tu93_normal_duck_first": len(analyses) > 0,
        "tu93_postlude_observed": (
            "tu93_postlude=start" in tu93_note
            or "tu93_postlude=already_complete" in tu93_note
        ),
        "tu93_postlude_zero_tokens": (
            "postlude_tokens=0" in tu93_note
            or "tu93_postlude=already_complete" in tu93_note
        ),
        "tu93_reset_before_repair": (
            first_postlude_action.get("action_name") == "RESET"
            or "tu93_postlude=already_complete" in tu93_note
        ),
    }
    helper_markers = ("tu93_postlude=",)
    checks["tu93_helper_did_not_leak"] = all(
        not any(marker in str(run.get("solver_note") or "") for marker in helper_markers)
        for game_id, run in runs.items()
        if game_id != TU93
    )

    base_score = aggregate(base_runs, "final_score")
    score = aggregate(runs, "final_score")
    base_levels = int(aggregate(base_runs, "levels_completed"))
    levels = int(aggregate(runs, "levels_completed"))
    checks["aggregate_not_weaker_than_active_baseline"] = (
        score >= base_score and levels >= base_levels
    )
    structural_names = [
        name
        for name in checks
        if name != "aggregate_not_weaker_than_active_baseline"
    ]
    structural_pass = all(checks[name] for name in structural_names)
    result = {
        "checks": checks,
        "details": {
            "baseline_score_sum": base_score,
            "candidate_score_sum": score,
            "score_delta": score - base_score,
            "baseline_levels": base_levels,
            "candidate_levels": levels,
            "level_delta": levels - base_levels,
            "ft09_levels": int(ft09.get("levels_completed") or 0),
            "tn36_levels": int(tn36.get("levels_completed") or 0),
            "tu93_levels": int(tu93.get("levels_completed") or 0),
            "tu93_actions": len(actions),
            "tu93_analysis_events": len(analyses),
            "first_tu93_postlude_action_index": duck_actions,
        },
        "structural_pass": structural_pass,
        "recommended_submit": (
            structural_pass
            and checks["aggregate_not_weaker_than_active_baseline"]
        ),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if structural_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
