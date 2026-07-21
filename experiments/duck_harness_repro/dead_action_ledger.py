#!/usr/bin/env python3
"""Measure repeated Duck actions that produced no observable effect.

This is an observation-only diagnostic. It reconstructs action transitions from
Kaggle benchmark history and event logs, then simulates two possible guards:

1. exact-state: same level, same board, and same action twice with no effect;
2. structural: same level and action/object shape twice with no effect.

Neither guard is applied to the solver by this script.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


DEFAULT_GAMES = ("sc25", "tr87", "r11l", "tn36")


def board_signature(board: list[list[Any]]) -> tuple[tuple[Any, ...], ...]:
    return tuple(tuple(row) for row in board)


def changed_cells(before: list[list[Any]], after: list[list[Any]]) -> int:
    """Count changed cells, including cells added by a shape change."""
    rows = max(len(before), len(after))
    changed = 0
    missing = object()
    for row in range(rows):
        before_row = before[row] if row < len(before) else []
        after_row = after[row] if row < len(after) else []
        cols = max(len(before_row), len(after_row))
        for col in range(cols):
            left = before_row[col] if col < len(before_row) else missing
            right = after_row[col] if col < len(after_row) else missing
            changed += left != right
    return changed


def _component_at(
    board: list[list[Any]], row: int, col: int
) -> tuple[Any, set[tuple[int, int]]] | None:
    if row < 0 or row >= len(board) or col < 0 or col >= len(board[row]):
        return None

    color = board[row][col]
    component = {(row, col)}
    queue = deque([(row, col)])
    while queue:
        current_row, current_col = queue.popleft()
        for next_row, next_col in (
            (current_row - 1, current_col),
            (current_row + 1, current_col),
            (current_row, current_col - 1),
            (current_row, current_col + 1),
        ):
            if (next_row, next_col) in component:
                continue
            if next_row < 0 or next_row >= len(board):
                continue
            if next_col < 0 or next_col >= len(board[next_row]):
                continue
            if board[next_row][next_col] != color:
                continue
            component.add((next_row, next_col))
            queue.append((next_row, next_col))
    return color, component


def _component_shape(
    color: Any, component: set[tuple[int, int]]
) -> tuple[Any, int, int, int, bool]:
    rows = [position[0] for position in component]
    cols = [position[1] for position in component]
    height = max(rows) - min(rows) + 1
    width = max(cols) - min(cols) + 1
    return color, len(component), height, width, len(component) == height * width


def object_signature(board: list[list[Any]], row: int, col: int) -> str:
    selected = _component_at(board, row, col)
    if selected is None:
        return "outside-board"

    color, component = selected
    shape = _component_shape(color, component)
    visited: set[tuple[int, int]] = set()
    twins = 0
    for board_row, values in enumerate(board):
        for board_col in range(len(values)):
            if (board_row, board_col) in visited:
                continue
            candidate = _component_at(board, board_row, board_col)
            if candidate is None:
                continue
            candidate_color, candidate_component = candidate
            visited.update(candidate_component)
            if _component_shape(candidate_color, candidate_component) == shape:
                twins += 1

    color_value, size, height, width, rectangular = shape
    return (
        f"color={color_value}|pixels={size}|bbox={height}x{width}"
        f"|rect={int(rectangular)}|twins={twins}"
    )


def action_signatures(
    action: dict[str, Any], board: list[list[Any]]
) -> tuple[str, str]:
    action_id = action.get("id", "UNKNOWN")
    data = action.get("data") or {}
    exact = f"{action_id}:{json.dumps(data, sort_keys=True, separators=(',', ':'))}"
    if action_id != "ACTION6":
        return exact, action_id

    row = int(data.get("y", -1))
    col = int(data.get("x", -1))
    structural = f"ACTION6:{object_signature(board, row, col)}"
    return exact, structural


def _is_progress(before: dict[str, Any], after: dict[str, Any]) -> bool:
    return bool(
        after.get("level", 0) > before.get("level", 0)
        or after.get("score", 0) > before.get("score", 0)
        or (after.get("reward") or 0) > 0
        or after.get("state") == "WIN"
    )


def analyze_game(
    game_run: dict[str, Any], events: Iterable[dict[str, Any]], threshold: int = 2
) -> dict[str, Any]:
    action_events = [event for event in events if event.get("type") == "action"]
    initial_events = [event for event in events if event.get("type") == "initial"]
    history = game_run.get("history", [])
    if len(initial_events) != 1:
        raise ValueError(f"{game_run['game_id']}: expected one initial event")
    if len(action_events) != len(history):
        raise ValueError(
            f"{game_run['game_id']}: {len(action_events)} action events != "
            f"{len(history)} history records"
        )

    previous = initial_events[0]
    exact_noops: Counter[tuple[Any, ...]] = Counter()
    structural_noops: Counter[tuple[int, str]] = Counter()
    structural_effective: set[tuple[int, str]] = set()
    signature_stats: dict[tuple[int, str], Counter[str]] = defaultdict(Counter)
    result: Counter[str] = Counter()
    exact_candidates: list[dict[str, Any]] = []
    structural_candidates: list[dict[str, Any]] = []
    streaks: list[dict[str, Any]] = []
    current_streak: dict[str, Any] | None = None

    for event, history_record in zip(action_events, history):
        action = history_record.get("action") or {}
        before_board = previous.get("board") or []
        after_board = event.get("board") or []
        level = int(previous.get("level") or 0)
        delta = changed_cells(before_board, after_board)
        progress = _is_progress(previous, event)
        effectful = bool(
            delta
            or progress
            or event.get("state") != previous.get("state")
            or event.get("run_status") != previous.get("run_status")
        )
        exact_action, structural_action = action_signatures(action, before_board)
        exact_key = (level, board_signature(before_board), exact_action)
        structural_key = (level, structural_action)

        exact_would_block = exact_noops[exact_key] >= threshold
        structural_would_block = (
            structural_noops[structural_key] >= threshold
            and structural_key not in structural_effective
        )
        candidate = {
            "action_num": event.get("action_num"),
            "level": level,
            "action": event.get("action_display") or exact_action,
            "changed_cells": delta,
            "progress": progress,
        }
        if exact_would_block:
            exact_candidates.append(candidate)
            result["exact_guard_candidates"] += 1
            result["exact_guard_unsafe"] += effectful
        if structural_would_block:
            structural_candidates.append(candidate)
            result["structural_guard_candidates"] += 1
            result["structural_guard_unsafe"] += effectful

        result["actions"] += 1
        result["changed_cells"] += delta
        result["effectful_actions"] += effectful
        result["exact_no_effect_actions"] += not effectful
        result["progress_actions"] += progress
        result["no_progress_actions"] += not progress
        signature_stats[structural_key]["attempts"] += 1
        signature_stats[structural_key]["effectful"] += effectful
        signature_stats[structural_key]["no_effect"] += not effectful
        signature_stats[structural_key]["progress"] += progress

        if effectful:
            structural_effective.add(structural_key)
        else:
            exact_noops[exact_key] += 1
            structural_noops[structural_key] += 1

        action_id = action.get("id", "UNKNOWN")
        if current_streak is None or current_streak["action_id"] != action_id:
            if current_streak is not None:
                streaks.append(current_streak)
            current_streak = {
                "action_id": action_id,
                "start_action": event.get("action_num"),
                "end_action": event.get("action_num"),
                "length": 1,
                "progress_actions": int(progress),
                "exact_no_effect_actions": int(not effectful),
            }
        else:
            current_streak["end_action"] = event.get("action_num")
            current_streak["length"] += 1
            current_streak["progress_actions"] += int(progress)
            current_streak["exact_no_effect_actions"] += int(not effectful)
        previous = event

    if current_streak is not None:
        streaks.append(current_streak)
    streaks.sort(key=lambda item: item["length"], reverse=True)

    top_signatures = []
    for (level, signature), stats in signature_stats.items():
        top_signatures.append(
            {
                "level": level,
                "signature": signature,
                **dict(stats),
            }
        )
    top_signatures.sort(
        key=lambda item: (item.get("no_effect", 0), item.get("attempts", 0)),
        reverse=True,
    )

    return {
        "game_id": game_run["game_id"],
        "levels_completed": game_run.get("levels_completed"),
        "final_score": game_run.get("final_score"),
        **dict(result),
        "exact_guard_examples": exact_candidates[:10],
        "structural_guard_examples": structural_candidates[:10],
        "longest_action_streaks": streaks[:10],
        "top_structural_signatures": top_signatures[:10],
    }


def analyze_run(
    run_root: Path, game_prefixes: Iterable[str], threshold: int = 2
) -> dict[str, Any]:
    benchmark = json.loads((run_root / "benchmark.json").read_text())
    game_runs = benchmark.get("game_runs", [])
    selected = []
    for prefix in game_prefixes:
        matches = [run for run in game_runs if run.get("game_id", "").startswith(prefix)]
        if len(matches) != 1:
            raise ValueError(f"expected one game matching {prefix!r}, found {len(matches)}")
        game_run = matches[0]
        event_path = run_root / "artifacts" / f"{game_run['game_id']}_p0_events.jsonl"
        events = [json.loads(line) for line in event_path.read_text().splitlines() if line]
        selected.append(analyze_game(game_run, events, threshold=threshold))

    totals: Counter[str] = Counter()
    metric_names = (
        "actions",
        "effectful_actions",
        "exact_no_effect_actions",
        "progress_actions",
        "no_progress_actions",
        "exact_guard_candidates",
        "exact_guard_unsafe",
        "structural_guard_candidates",
        "structural_guard_unsafe",
    )
    for game in selected:
        for name in metric_names:
            totals[name] += game.get(name, 0)
    return {
        "run_root": str(run_root),
        "threshold": threshold,
        "games": selected,
        "totals": dict(totals),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", type=Path)
    parser.add_argument("--games", nargs="+", default=list(DEFAULT_GAMES))
    parser.add_argument("--threshold", type=int, default=2)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.threshold < 1:
        parser.error("--threshold must be at least 1")

    report = analyze_run(args.run_root, args.games, threshold=args.threshold)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
