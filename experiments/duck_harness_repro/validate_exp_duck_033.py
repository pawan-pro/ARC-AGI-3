#!/usr/bin/env python3
"""Validate the three live EXP-DUCK-033 one-click probe arms."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOTS = (
    ROOT / "artifacts/kaggle/duck_ft09_level5_probe_top/latest",
    ROOT / "artifacts/kaggle/duck_ft09_level5_probe_middle/latest",
    ROOT / "artifacts/kaggle/duck_ft09_level5_probe_bottom_right/latest",
)
DEFAULT_OUTPUT = ROOT / "experiments/duck_harness_repro/exp_duck_033_validation.json"
EXPECTED = {
    "top": (14, 24),
    "middle": (30, 24),
    "bottom_right": (46, 40),
}


def parse_note(note: str) -> dict[str, str]:
    prefix = note.split("; ft09_overlap_target=", 1)[0]
    fields: dict[str, str] = {}
    for item in prefix.split("; "):
        if "=" in item:
            key, value = item.split("=", 1)
            fields[key] = value
    return fields


def load_arm(root: Path) -> dict[str, object]:
    benchmark = json.loads((root / "benchmark.json").read_text(encoding="utf-8"))
    run = benchmark["game_runs"][0]
    note = str(run["solver_note"])
    fields = parse_note(note)
    arm = fields["arm"]
    event_path = root / "artifacts/ft09-0d8bbf25_p0_events.jsonl"
    events = [
        json.loads(line)
        for line in event_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    probe_events = events[70:]
    expected = EXPECTED[arm]
    action_match = re.search(
        r"row=(\d+), col=(\d+)", str(probe_events[0]["action_display"])
    )
    observed = tuple(map(int, action_match.groups())) if action_match else None
    return {
        "arm": arm,
        "root": str(root),
        "levels_completed": int(run["levels_completed"]),
        "actions_per_level": run["actions_per_level"],
        "total_actions": len(run["history"]),
        "tokens": int(run["final_generated_tokens"]),
        "expected_cell": list(expected),
        "observed_cell": list(observed) if observed else None,
        "one_probe_action": len(probe_events) == 1,
        "prefix_reached_level5": int(events[69]["level"]) == 5
        and int(events[69]["action_num"]) == 69,
        "changed_pixels": int(fields["changed"]),
        "changed_cells": fields["changed_cells"],
        "before_color": int(fields["before"]),
        "after_color": int(fields["after"]),
        "level_after": int(fields["level_after"]),
        "level_completed": fields["level_completed"] == "True",
        "game_over": fields["game_over"] == "True",
        "solver_note": note,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="*", type=Path, default=list(DEFAULT_ROOTS))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    arms = [load_arm(root) for root in args.roots]
    observed_names = {str(arm["arm"]) for arm in arms}
    checks = {
        "all_three_arms_present": observed_names == set(EXPECTED),
        "all_prefixes_reached_level5": all(
            bool(arm["prefix_reached_level5"]) for arm in arms
        ),
        "exactly_one_probe_per_arm": all(
            bool(arm["one_probe_action"]) for arm in arms
        ),
        "all_probe_coordinates_exact": all(
            arm["expected_cell"] == arm["observed_cell"] for arm in arms
        ),
        "all_zero_token": all(int(arm["tokens"]) == 0 for arm in arms),
        "no_unplanned_actions": all(int(arm["total_actions"]) == 70 for arm in arms),
    }
    structural_pass = all(checks.values())
    result = {
        "experiment": "EXP-DUCK-033",
        "structural_pass": structural_pass,
        "checks": checks,
        "arms": arms,
        "mechanic_identified": len(
            {
                (
                    int(arm["changed_pixels"]),
                    str(arm["changed_cells"]),
                    bool(arm["level_completed"]),
                    bool(arm["game_over"]),
                )
                for arm in arms
            }
        )
        > 1
        or any(bool(arm["level_completed"]) for arm in arms),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if structural_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
