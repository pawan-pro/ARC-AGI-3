#!/usr/bin/env python3
"""Replay Duck action batches and measure feedback-aware early-stop candidates."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def action_batches(events: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for event in (item for item in events if item.get("type") == "action"):
        batch_index = int(event.get("batch_index") or 1)
        if batch_index == 1 or not current:
            if current:
                batches.append(current)
            current = [event]
        else:
            current.append(event)
    if current:
        batches.append(current)
    return batches


def analyze_events(events: list[dict[str, Any]]) -> dict[str, int]:
    initial = next(item for item in events if item.get("type") == "initial")
    previous_board = initial.get("board") or []
    previous_level = initial.get("level")
    recent_states = [(previous_level, previous_board)]
    result: Counter[str] = Counter()

    for batch in action_batches(events):
        result["batches"] += 1
        result["multi_action_batches"] += len(batch) > 1
        no_change_trigger = None
        repeated_state_trigger = None

        for index, event in enumerate(batch):
            level = event.get("level")
            board = event.get("board") or []
            no_change = board == previous_board and level == previous_level
            repeated_state = any(
                old_level == level and old_board == board
                for old_level, old_board in recent_states[-11:]
            )
            if index < len(batch) - 1:
                if no_change and no_change_trigger is None:
                    no_change_trigger = index
                if repeated_state and repeated_state_trigger is None:
                    repeated_state_trigger = index
            recent_states.append((level, board))
            previous_board = board
            previous_level = level

        for name, trigger in (
            ("no_change", no_change_trigger),
            ("repeated_state", repeated_state_trigger),
        ):
            if trigger is None:
                continue
            trailing = batch[trigger + 1 :]
            result[f"{name}_triggered_batches"] += 1
            result[f"{name}_trailing_actions"] += len(trailing)
            if any(
                bool(item.get("level_completed")) or float(item.get("reward") or 0) > 0
                for item in trailing
            ):
                result[f"{name}_unsafe_batches"] += 1
    return dict(result)


def analyze_run(run_root: Path, exempt_prefixes: set[str]) -> dict[str, Any]:
    artifacts = run_root / "artifacts"
    games = []
    totals: Counter[str] = Counter()
    included_totals: Counter[str] = Counter()
    for path in sorted(artifacts.glob("*_p0_events.jsonl")):
        game_id = path.name.split("_p0_events.jsonl", 1)[0]
        events = [json.loads(line) for line in path.read_text().splitlines() if line]
        metrics = analyze_events(events)
        exempt = any(game_id.startswith(prefix) for prefix in exempt_prefixes)
        games.append({"game_id": game_id, "exempt": exempt, **metrics})
        totals.update(metrics)
        if not exempt:
            included_totals.update(metrics)
    return {
        "run_root": str(run_root),
        "exempt_prefixes": sorted(exempt_prefixes),
        "totals": dict(totals),
        "included_totals": dict(included_totals),
        "games": games,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", type=Path)
    parser.add_argument("--exempt", nargs="*", default=["ft09"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = analyze_run(args.run_root, set(args.exempt))
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
