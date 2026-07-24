#!/usr/bin/env python3
"""Validate EXP-DUCK-024 against the scored EXP-DUCK-009 benchmark."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TN36 = "tn36-ef4dde99"
FT09 = "ft09-0d8bbf25"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def runs_by_id(benchmark: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(run["game_id"]): run for run in benchmark.get("game_runs", [])}


def aggregate(runs: dict[str, dict[str, Any]], field: str) -> float:
    return sum(float(run.get(field) or 0) for run in runs.values())


def validate(
    baseline: dict[str, Any], candidate: dict[str, Any], candidate_root: Path
) -> dict[str, Any]:
    base_runs = runs_by_id(baseline)
    runs = runs_by_id(candidate)
    ft09 = runs.get(FT09, {})
    tn36 = runs.get(TN36, {})
    note = str(tn36.get("solver_note") or "")

    event_path = candidate_root / "artifacts" / f"{TN36}_p0_events.jsonl"
    events = [
        json.loads(line)
        for line in event_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ] if event_path.exists() else []
    actions = [event for event in events if event.get("type") == "action"]
    analyses = [event for event in events if event.get("type") == "analysis"]
    duck_actions_match = re.search(r"tn36_postlude=start;[^;]*; duck_actions=(\d+)", note)
    duck_actions = int(duck_actions_match.group(1)) if duck_actions_match else None
    postlude_reset = (
        actions[duck_actions]
        if duck_actions is not None and duck_actions < len(actions)
        else {}
    )

    checks: dict[str, bool] = {
        "same_game_ids": set(base_runs) == set(runs),
        "expected_25_games": len(runs) == 25,
        "ft09_preserved": int(ft09.get("levels_completed") or 0) >= 4,
        "ft09_helper_note": "ft09_overlap_target=" in str(
            ft09.get("solver_note") or ""
        ),
        "tn36_three_levels": int(tn36.get("levels_completed") or 0) >= 3,
        "postlude_started": "tn36_postlude=start" in note,
        "postlude_finished": "tn36_postlude=finished" in note,
        "postlude_zero_tokens": "postlude_tokens=0" in note,
        "duck_analyzed_before_postlude": bool(analyses)
        and duck_actions is not None
        and duck_actions > 0,
        "postlude_begins_with_reset": postlude_reset.get("action_name") == "RESET",
    }
    helper_markers = (
        "tn36_postlude=",
        "tn36_level1_helper=",
        "tn36_level2_program=",
        "tn36_level3_program=",
    )
    checks["helper_did_not_leak"] = all(
        not any(marker in str(run.get("solver_note") or "") for marker in helper_markers)
        for game_id, run in runs.items()
        if game_id != TN36
    )

    base_score = aggregate(base_runs, "final_score")
    candidate_score = aggregate(runs, "final_score")
    base_levels = int(aggregate(base_runs, "levels_completed"))
    candidate_levels = int(aggregate(runs, "levels_completed"))
    checks["aggregate_not_weaker_than_scored_baseline"] = (
        candidate_score >= base_score and candidate_levels >= base_levels
    )
    structural_names = [
        name for name in checks if name != "aggregate_not_weaker_than_scored_baseline"
    ]
    structural_pass = all(checks[name] for name in structural_names)
    return {
        "checks": checks,
        "details": {
            "baseline_score_sum": base_score,
            "candidate_score_sum": candidate_score,
            "score_delta": candidate_score - base_score,
            "baseline_levels": base_levels,
            "candidate_levels": candidate_levels,
            "level_delta": candidate_levels - base_levels,
            "ft09_levels": int(ft09.get("levels_completed") or 0),
            "tn36_levels": int(tn36.get("levels_completed") or 0),
            "tn36_actions": len(actions),
            "tn36_analysis_events": len(analyses),
            "first_postlude_action_index": duck_actions,
        },
        "structural_pass": structural_pass,
        "recommended_submit": (
            structural_pass and checks["aggregate_not_weaker_than_scored_baseline"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(
        load_json(args.baseline), load_json(args.candidate), args.candidate_root
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["structural_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
