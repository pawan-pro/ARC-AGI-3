#!/usr/bin/env python3
"""Validate EXP-DUCK-014 against the scored EXP-DUCK-009 benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TN36 = "tn36-ef4dde99"
FT09 = "ft09-0d8bbf25"
EXPECTED_TN36_ACTIONS = [
    "MOUSE(row=42, col=26)",
    "MOUSE(row=42, col=36)",
    "MOUSE(row=42, col=41)",
    "MOUSE(row=45, col=26)",
    "MOUSE(row=45, col=36)",
    "MOUSE(row=45, col=41)",
    "MOUSE(row=55, col=36)",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def runs_by_id(benchmark: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(run["game_id"]): run for run in benchmark.get("game_runs", [])}


def score_sum(runs: dict[str, dict[str, Any]]) -> float:
    return sum(float(run.get("final_score") or 0) for run in runs.values())


def level_sum(runs: dict[str, dict[str, Any]]) -> int:
    return sum(int(run.get("levels_completed") or 0) for run in runs.values())


def validate(
    baseline: dict[str, Any], candidate: dict[str, Any], candidate_root: Path
) -> dict[str, Any]:
    base_runs = runs_by_id(baseline)
    candidate_runs = runs_by_id(candidate)
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}

    checks["same_game_ids"] = set(base_runs) == set(candidate_runs)
    checks["expected_25_games"] = len(candidate_runs) == 25

    ft09 = candidate_runs.get(FT09, {})
    tn36 = candidate_runs.get(TN36, {})
    checks["ft09_preserved"] = int(ft09.get("levels_completed") or 0) >= 4
    checks["ft09_helper_note"] = "ft09_overlap_target=" in str(ft09.get("solver_note") or "")
    checks["tn36_level1_preserved"] = int(tn36.get("levels_completed") or 0) >= 1
    checks["tn36_helper_note"] = "tn36_level1_helper=success; helper_actions=7" in str(
        tn36.get("solver_note") or ""
    )
    checks["helper_did_not_leak"] = all(
        "tn36_level1_helper=" not in str(run.get("solver_note") or "")
        for game_id, run in candidate_runs.items()
        if game_id != TN36
    )

    event_path = candidate_root / "artifacts" / f"{TN36}_p0_events.jsonl"
    actions: list[dict[str, Any]] = []
    if event_path.exists():
        events = [
            json.loads(line)
            for line in event_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        actions = [item for item in events if item.get("type") == "action"]
    first_seven = actions[:7]
    checks["tn36_exact_prefix"] = [
        item.get("action_display") for item in first_seven
    ] == EXPECTED_TN36_ACTIONS
    checks["tn36_prefix_zero_tokens"] = sum(
        int(item.get("generated_tokens") or 0) for item in first_seven
    ) == 0
    checks["tn36_action7_completed_level"] = bool(
        len(first_seven) == 7 and first_seven[-1].get("level_completed")
    )
    checks["tn36_continued_after_prefix"] = len(actions) > 7

    baseline_score = score_sum(base_runs)
    candidate_score = score_sum(candidate_runs)
    baseline_levels = level_sum(base_runs)
    candidate_levels = level_sum(candidate_runs)
    checks["aggregate_not_weaker"] = (
        candidate_score >= baseline_score and candidate_levels >= baseline_levels
    )
    structural_names = [name for name in checks if name != "aggregate_not_weaker"]
    structural_pass = all(checks[name] for name in structural_names)
    recommended_submit = structural_pass and checks["aggregate_not_weaker"]

    details.update(
        {
            "baseline_score_sum": baseline_score,
            "candidate_score_sum": candidate_score,
            "score_delta": candidate_score - baseline_score,
            "baseline_levels": baseline_levels,
            "candidate_levels": candidate_levels,
            "level_delta": candidate_levels - baseline_levels,
            "ft09_levels": int(ft09.get("levels_completed") or 0),
            "tn36_levels": int(tn36.get("levels_completed") or 0),
            "tn36_actions": sum(tn36.get("actions_per_level") or []),
            "tn36_event_actions": len(actions),
        }
    )
    return {
        "checks": checks,
        "details": details,
        "structural_pass": structural_pass,
        "recommended_submit": recommended_submit,
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
