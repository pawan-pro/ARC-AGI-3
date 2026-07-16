#!/usr/bin/env python3
"""Reconstruct the EXP-DUCK-005 ft09 level-4 helper candidate trace.

The Kaggle event stream records the board after each environment action, but
the helper did not log candidate names per action. This script mirrors the
candidate generator from the notebook and aligns generated candidate actions
with the recorded events.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


BLUE = 9
RED = 8
ORANGE = 12
WHITE = 0
GRAY = 2
CYCLE = [BLUE, RED, ORANGE]
COLOR_NAME = {
    BLUE: "b",
    RED: "R",
    ORANGE: "O",
    WHITE: "W",
    GRAY: "g",
    4: "c",
}

NORMAL_CELLS = [
    (16, 14),
    (16, 22),
    (16, 30),
    (16, 38),
    (16, 46),
    (24, 14),
    (24, 30),
    (24, 46),
    (32, 14),
    (32, 22),
    (32, 30),
    (32, 38),
    (32, 46),
    (40, 22),
    (40, 38),
    (48, 22),
    (48, 30),
    (48, 38),
]
SPECIAL_CELLS = [(24, 22), (24, 38), (40, 30)]
NORMAL_SET = set(NORMAL_CELLS)


def color(value: int) -> str:
    return COLOR_NAME.get(int(value), str(value))


def center_string(values: dict[tuple[int, int], int]) -> str:
    return "".join(color(values[cell]) for cell in NORMAL_CELLS)


def mask_values(board: list[list[int]], special: tuple[int, int]) -> dict[tuple[int, int], int]:
    row, col = special
    return {
        (dr, dc): int(board[row + dr * 2][col + dc * 2])
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
    }


def cycle_distance(current: int, target: int) -> int:
    if current == target:
        return 0
    if current not in CYCLE or target not in CYCLE:
        return 0
    start = CYCLE.index(current)
    for steps in range(1, len(CYCLE) + 1):
        if CYCLE[(start + steps) % len(CYCLE)] == target:
            return steps
    return 0


def level4_candidates(board: list[list[int]]) -> list[tuple[str, dict[tuple[int, int], int]]]:
    def votes_for(policy_name: str) -> dict[tuple[int, int], list[int]]:
        votes = {cell: [] for cell in NORMAL_CELLS}
        palette_by_index = [BLUE, RED, ORANGE]
        for special_index, special in enumerate(SPECIAL_CELLS):
            center_color = int(board[special[0]][special[1]])
            other_colors = [item for item in CYCLE if item != center_color]
            for (dr, dc), value in mask_values(board, special).items():
                if (dr, dc) == (0, 0):
                    continue
                target_cell = (special[0] + dr * 8, special[1] + dc * 8)
                if target_cell not in NORMAL_SET:
                    continue
                if policy_name == "white_is_center":
                    target_color = center_color if value == WHITE else other_colors[0]
                elif policy_name == "gray_is_center":
                    target_color = center_color if value == GRAY else other_colors[0]
                elif policy_name == "white_is_palette":
                    target_color = palette_by_index[special_index % len(palette_by_index)] if value == WHITE else center_color
                elif policy_name == "gray_is_palette":
                    target_color = palette_by_index[special_index % len(palette_by_index)] if value == GRAY else center_color
                elif policy_name == "white_cycles_from_center":
                    offset = 1 if value == WHITE else 2 if value == GRAY else 0
                    target_color = CYCLE[(CYCLE.index(center_color) + offset) % len(CYCLE)]
                else:
                    target_color = center_color
                votes[target_cell].append(target_color)
        return votes

    def combine(values: list[int], rule: str) -> int:
        if not values:
            return BLUE
        if rule == "last":
            return values[-1]
        if rule == "majority":
            counts = {item: sum(1 for value in values if value == item) for item in CYCLE}
            return max(CYCLE, key=lambda item: (counts[item], -CYCLE.index(item)))
        if rule == "parity":
            index_sum = sum(CYCLE.index(value) for value in values if value in CYCLE)
            return CYCLE[index_sum % len(CYCLE)]
        if rule.endswith("_wins"):
            winner = {"blue": BLUE, "red": RED, "orange": ORANGE}.get(rule.removesuffix("_wins"), BLUE)
            return winner if winner in values else values[-1]
        return values[-1]

    candidates: list[tuple[str, dict[tuple[int, int], int]]] = []
    seen: set[tuple[tuple[tuple[int, int], int], ...]] = set()
    policies = ["white_is_center", "gray_is_center", "white_is_palette", "gray_is_palette", "white_cycles_from_center"]
    rules = ["parity", "majority", "blue_wins", "red_wins", "orange_wins", "last"]
    for policy_name in policies:
        votes = votes_for(policy_name)
        for rule in rules:
            target = {cell: combine(votes[cell], rule) for cell in NORMAL_CELLS}
            signature = tuple((cell, target[cell]) for cell in NORMAL_CELLS)
            if signature in seen:
                continue
            seen.add(signature)
            candidates.append((f"level4:{policy_name}+{rule}", target))
    candidates.sort(
        key=lambda item: (
            sum(cycle_distance(int(board[row][col]), target_color) for (row, col), target_color in item[1].items()),
            item[0],
        )
    )
    return candidates


def changed_pixels(before: list[list[int]], after: list[list[int]]) -> int:
    return sum(a != b for row_a, row_b in zip(before, after) for a, b in zip(row_a, row_b))


def parse_action_cell(action_display: str) -> tuple[int, int]:
    match = re.search(r"row=(\d+), col=(\d+)", action_display)
    if not match:
        raise ValueError(f"Could not parse action display: {action_display}")
    return int(match.group(1)), int(match.group(2))


def reconstruct(events_path: Path, *, max_candidates: int = 8) -> dict[str, object]:
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    action_events = {
        int(event["action_num"]): event
        for event in events
        if isinstance(event, dict) and event.get("type") == "action" and event.get("action_num") is not None
    }
    level4_start = next(
        event
        for event in action_events.values()
        if int(event.get("level") or 0) == 4 and bool(event.get("level_completed"))
    )
    start_action = int(level4_start["action_num"])
    initial_board = level4_start["board"]

    rows = []
    current_board = [row[:] for row in initial_board]
    action_num = start_action + 1
    for candidate_index, (candidate_name, target) in enumerate(level4_candidates(initial_board)[:max_candidates], start=1):
        before = {cell: int(current_board[cell[0]][cell[1]]) for cell in NORMAL_CELLS}
        requested: list[tuple[int, int]] = []
        for cell, target_color in target.items():
            requested.extend([cell] * cycle_distance(before[cell], int(target_color)))

        start = action_num
        executed = 0
        changed = 0
        mismatches: list[str] = []
        stop_reason = ""
        for cell in requested:
            event = action_events.get(action_num)
            if event is None:
                stop_reason = "missing_action_event"
                break
            action_display = str(event.get("action_display") or "")
            try:
                actual_cell = parse_action_cell(action_display)
            except ValueError:
                stop_reason = f"non_mouse_action:{action_display}"
                break
            if actual_cell != cell:
                mismatches.append(f"{action_num}: expected {cell}, saw {actual_cell}")
            previous_board = action_events[action_num - 1]["board"]
            changed += changed_pixels(previous_board, event["board"])
            current_board = [row[:] for row in event["board"]]
            executed += 1
            action_num += 1

        if requested:
            after = {cell: int(current_board[cell[0]][cell[1]]) for cell in NORMAL_CELLS}
            rows.append(
                {
                    "candidate_index": candidate_index,
                    "candidate": candidate_name,
                    "start_action": start,
                    "end_action": action_num - 1 if executed else None,
                    "planned_actions": len(requested),
                    "executed_actions": executed,
                    "completed_candidate": executed == len(requested),
                    "changed_pixels": changed,
                    "before": center_string(before),
                    "target": center_string(target),
                    "after": center_string(after),
                    "mismatches": mismatches,
                    "stop_reason": stop_reason,
                }
            )
        if stop_reason:
            break
        if action_num > max(action_events):
            break

    special_masks = []
    for special in SPECIAL_CELLS:
        values = mask_values(initial_board, special)
        special_masks.append(
            {
                "cell": special,
                "center": color(initial_board[special[0]][special[1]]),
                "mask": ["".join(color(values[(dr, dc)]) for dc in (-1, 0, 1)) for dr in (-1, 0, 1)],
            }
        )

    return {
        "level4_start_action": start_action,
        "level4_start_centers": center_string({cell: int(initial_board[cell[0]][cell[1]]) for cell in NORMAL_CELLS}),
        "special_masks": special_masks,
        "rows": rows,
        "last_recorded_action": max(action_events),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--events",
        type=Path,
        default=Path("artifacts/kaggle/duck_ft09_level4_isolated/latest/artifacts/ft09-0d8bbf25_p0_events.jsonl"),
    )
    args = parser.parse_args()
    result = reconstruct(args.events)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
