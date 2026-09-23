#!/usr/bin/env python3
"""Validate the live EXP-DUCK-034 bounded Gray-code result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = ROOT / "artifacts/kaggle/duck_ft09_bounded_gray_reasoner/latest"
DEFAULT_OUTPUT = ROOT / "experiments/duck_harness_repro/exp_duck_034_validation.json"
EXPECTED_PLAN = [
    "ft09-level5-magenta-top",
    "ft09-level5-magenta-middle",
    "ft09-level5-magenta-top",
    "ft09-level5-magenta-bottom_right",
    "ft09-level5-magenta-top",
    "ft09-level5-magenta-middle",
    "ft09-level5-magenta-top",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    benchmark = json.loads((args.root / "benchmark.json").read_text(encoding="utf-8"))
    trace = json.loads(
        (args.root / "exp_duck_034_reasoning_trace.json").read_text(encoding="utf-8")
    )
    memory = json.loads(
        (
            args.root / "exp_duck_034_mechanics_memory_observed.json"
        ).read_text(encoding="utf-8")
    )
    events = [
        json.loads(line)
        for line in (
            args.root / "artifacts/ft09-0d8bbf25_p0_events.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    action_events = [event for event in events if event.get("type") == "action"]
    run = benchmark["game_runs"][0]
    records = trace["records"]
    memory_rules = memory["rules"]

    checks = {
        "one_target_game": len(benchmark["game_runs"]) == 1
        and run["game_id"] == "ft09-0d8bbf25",
        "validated_prefix_preserved": run["actions_per_level"][:4]
        == [9, 7, 32, 21],
        "zero_llm_tokens": int(run["final_generated_tokens"]) == 0
        and trace["runtime_llm"] is False,
        "seven_action_budget": int(trace["action_budget"]) == 7
        and trace["planned_actions"] == EXPECTED_PLAN,
        "stopped_after_two_actions": int(trace["executed_actions"]) == 2
        and run["actions_per_level"][4] == 2
        and len(action_events) == 71,
        "first_known_effect_exact": records[0]["prediction_check"] == "match"
        and int(records[0]["mismatch_count"]) == 0,
        "second_action_guard_fired": records[1]["prediction_check"] == "mismatch"
        and trace["stop_reason"] == "prediction_mismatch",
        "single_corner_feedback_mismatch": records[1]["mismatch_count"] == 1
        and records[1]["mismatch_sample"] == [[63, 63, 12, 11]],
        "no_terminal_failure": all(
            not bool(record[key])
            for record in records
            for key in ("level_completed", "game_over", "run_complete")
        ),
        "level_did_not_advance": int(run["levels_completed"]) == 4,
        "no_rule_auto_promoted": all(
            rule["status"] == "observed_forward_only"
            and rule["transfer_scope"] == "exact_board"
            for rule in memory_rules
        ),
        "exact_probe_order": [
            action_events[-2]["action_display"],
            action_events[-1]["action_display"],
        ]
        == [
            "MOUSE(row=14, col=24)",
            "MOUSE(row=30, col=24)",
        ],
    }
    structural_pass = all(checks.values())
    result = {
        "experiment": "EXP-DUCK-034",
        "structural_pass": structural_pass,
        "checks": checks,
        "levels_completed": int(run["levels_completed"]),
        "actions_per_level": run["actions_per_level"],
        "tokens": int(run["final_generated_tokens"]),
        "planned_actions": trace["planned_actions"],
        "executed_actions": int(trace["executed_actions"]),
        "stop_reason": trace["stop_reason"],
        "prediction_records": records,
        "hypotheses": trace["hypotheses"],
        "rule_evidence": trace["rule_evidence"],
        "interpretation": (
            "The regional binary-XOR prediction matched all modeled operator "
            "pixels through action 2, while an additional combination-dependent "
            "corner pixel changed from 12 to 11. The strict full-board guard "
            "correctly stopped the run. Level 5 did not advance."
        ),
        "next_gate": (
            "Repeat only top-then-middle from a clean level-5 start to test "
            "whether the (63,63) 12->11 feedback is deterministic. Do not "
            "resume the remaining Gray-code actions yet."
        ),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if structural_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
