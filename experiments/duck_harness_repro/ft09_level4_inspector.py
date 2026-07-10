"""Inspect ft09 level 4 from downloaded Duck viewer events.

The purpose is to decide whether level 4 should reuse/generalize the ft09
mask/toggle helper or get a separate helper. It prints a compact structural
summary from the first level-4 board and the first few action effects.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


COLOR_CHARS = {
    0: "W",
    2: "g",
    4: "c",
    8: "R",
    9: "b",
    12: "O",
}

LEVEL4_SAMPLE_CENTERS = (
    (16, 14),
    (16, 22),
    (16, 30),
    (16, 38),
    (16, 46),
    (24, 14),
    (24, 22),
    (24, 30),
    (24, 38),
    (24, 46),
    (32, 14),
    (32, 22),
    (32, 30),
    (32, 38),
    (32, 46),
    (40, 22),
    (40, 30),
    (40, 38),
    (48, 22),
    (48, 30),
    (48, 38),
)

LEVEL4_SPECIAL_CENTERS = (
    (24, 22),
    (24, 38),
    (40, 30),
)


def load_events(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def first_level_board(events: list[dict[str, Any]], level: int) -> dict[str, Any]:
    for event in events:
        if event.get("level") == level and "board" in event:
            return event
    raise ValueError(f"no board found for level {level}")


def color_name(value: int) -> str:
    return COLOR_CHARS.get(int(value), str(value))


def crop(board: list[list[int]], center: tuple[int, int], radius: int = 4) -> list[str]:
    row, col = center
    return [
        "".join(color_name(board[r][c]) for c in range(col - radius, col + radius + 1))
        for r in range(row - radius, row + radius + 1)
    ]


def action_diffs(events: list[dict[str, Any]], *, level: int, limit: int = 20) -> list[dict[str, Any]]:
    rows = []
    previous_board: list[list[int]] | None = None
    for event in events:
        if event.get("level") != level or event.get("type") != "action":
            continue
        board = event["board"]
        if previous_board is None:
            diffs = []
        else:
            diffs = [
                (r, c, previous_board[r][c], board[r][c])
                for r in range(len(board))
                for c in range(len(board[r]))
                if previous_board[r][c] != board[r][c]
            ]
        rows.append(
            {
                "action_num": event.get("action_num"),
                "action": event.get("action_display"),
                "reward": event.get("reward"),
                "level_completed": event.get("level_completed"),
                "diff_count": len(diffs),
                "sample_transitions": Counter((a, b) for _, _, a, b in diffs).most_common(4),
            }
        )
        previous_board = board
        if len(rows) >= limit:
            break
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "events_jsonl",
        type=Path,
        nargs="?",
        default=Path("artifacts/kaggle/duck_ft09_helper/latest/artifacts/ft09-0d8bbf25_p0_events.jsonl"),
    )
    args = parser.parse_args()

    events = load_events(args.events_jsonl)
    event = first_level_board(events, 4)
    board = event["board"]

    print(f"first_level4_event: type={event.get('type')} action_num={event.get('action_num')} score={event.get('score')}")
    print("color_counts:", {color_name(k): v for k, v in Counter(cell for row in board for cell in row).most_common()})
    print("\ncenter_sample:")
    for row in (16, 24, 32, 40, 48):
        cells = []
        for col in (14, 22, 30, 38, 46):
            if (row, col) in LEVEL4_SAMPLE_CENTERS:
                cells.append(f"{color_name(board[row][col])}@{row},{col}")
            else:
                cells.append("empty")
        print("  " + " | ".join(cells))

    print("\nspecial_crops:")
    for center in LEVEL4_SPECIAL_CENTERS:
        print(f"  center={center} color={color_name(board[center[0]][center[1]])}")
        for line in crop(board, center):
            print(f"    {line}")

    print("\nfirst_action_diffs:")
    for row in action_diffs(events, level=4):
        transitions = ", ".join(
            f"{color_name(a)}->{color_name(b)} x{count}" for (a, b), count in row["sample_transitions"]
        )
        print(
            f"  action={row['action_num']} {row['action']} reward={row['reward']} "
            f"completed={row['level_completed']} diffs={row['diff_count']} {transitions}"
        )


if __name__ == "__main__":
    main()
