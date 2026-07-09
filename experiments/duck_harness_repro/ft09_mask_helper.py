"""Candidate generator for the ft09 level-3 mask puzzle.

This is an experiment scaffold, not a broad solver. It encodes the structure
seen in the clean targeted rerun:

- level 3 has a diamond of red/orange toggle cells
- four special cells contain tiny 3x3 white/gray masks
- clicking a normal cell toggles red <-> orange

The helper produces candidate click sequences from several mask-combination
rules so a future notebook patch can try them deterministically before falling
back to the LLM.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

RED = 8
ORANGE = 12
WHITE = 0
GRAY = 2

FT09_LEVEL3_REGULAR_CELLS: tuple[tuple[int, int], ...] = (
    (6, 22),
    (6, 30),
    (6, 38),
    (14, 22),
    (14, 38),
    (22, 14),
    (22, 22),
    (22, 30),
    (22, 38),
    (22, 46),
    (30, 14),
    (30, 30),
    (30, 46),
    (38, 14),
    (38, 22),
    (38, 30),
    (38, 38),
    (38, 46),
    (46, 22),
    (46, 38),
    (54, 22),
    (54, 30),
    (54, 38),
)

FT09_LEVEL3_SPECIAL_CELLS: tuple[tuple[int, int], ...] = (
    (14, 30),
    (30, 22),
    (30, 38),
    (46, 30),
)


def load_level3_initial_board(events_jsonl: Path) -> list[list[int]]:
    for line in events_jsonl.read_text().splitlines():
        event = json.loads(line)
        if event.get("game_id") and event.get("game_id") != "ft09-0d8bbf25":
            continue
        if event.get("level") == 3 and "board" in event:
            return event["board"]
    raise ValueError(f"no ft09 level-3 board found in {events_jsonl}")


def mask_values(board: list[list[int]], special_cell: tuple[int, int]) -> dict[tuple[int, int], int]:
    row, col = special_cell
    values: dict[tuple[int, int], int] = {}
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            values[(dr, dc)] = int(board[row + dr * 2][col + dc * 2])
    return values


def mask_neighbor(cell: tuple[int, int], offset: tuple[int, int]) -> tuple[int, int]:
    row, col = cell
    dr, dc = offset
    return row + dr * 8, col + dc * 8


def infer_target_votes(
    board: list[list[int]],
    *,
    white_policy: str,
) -> dict[tuple[int, int], list[int]]:
    """Return color votes for regular cells covered by the special masks.

    `white_policy` controls how a white/gray mask mark maps to the output:

    - `white_is_orange`: white means orange, gray means red
    - `white_is_center`: white means the special cell center color, gray means the other color
    - `gray_is_center`: gray means the special cell center color, white means the other color
    """

    votes: dict[tuple[int, int], list[int]] = {cell: [] for cell in FT09_LEVEL3_REGULAR_CELLS}
    regular = set(FT09_LEVEL3_REGULAR_CELLS)
    for special in FT09_LEVEL3_SPECIAL_CELLS:
        center_color = int(board[special[0]][special[1]])
        other_color = RED if center_color == ORANGE else ORANGE
        for offset, value in mask_values(board, special).items():
            if offset == (0, 0):
                continue
            target_cell = mask_neighbor(special, offset)
            if target_cell not in regular:
                continue
            if white_policy == "white_is_orange":
                color = ORANGE if value == WHITE else RED
            elif white_policy == "white_is_center":
                color = center_color if value == WHITE else other_color
            elif white_policy == "gray_is_center":
                color = center_color if value == GRAY else other_color
            else:
                raise ValueError(f"unknown white_policy: {white_policy}")
            votes[target_cell].append(color)
    return votes


def combine_votes(votes: Iterable[int], *, combine: str) -> int:
    vote_list = list(votes)
    if not vote_list:
        return RED
    if combine == "orange_wins":
        return ORANGE if ORANGE in vote_list else RED
    if combine == "red_wins":
        return RED if RED in vote_list else ORANGE
    if combine == "majority":
        counts = Counter(vote_list)
        return ORANGE if counts[ORANGE] >= counts[RED] else RED
    if combine == "parity":
        return ORANGE if sum(1 for value in vote_list if value == ORANGE) % 2 else RED
    if combine == "last":
        return vote_list[-1]
    raise ValueError(f"unknown combine rule: {combine}")


def candidate_clicks(
    board: list[list[int]],
    *,
    white_policy: str,
    combine: str,
) -> tuple[tuple[int, int], ...]:
    votes = infer_target_votes(board, white_policy=white_policy)
    clicks = []
    for cell in FT09_LEVEL3_REGULAR_CELLS:
        current = int(board[cell[0]][cell[1]])
        target = combine_votes(votes[cell], combine=combine)
        if current != target:
            clicks.append(cell)
    return tuple(clicks)


def candidate_suite(board: list[list[int]]) -> dict[str, tuple[tuple[int, int], ...]]:
    candidates: dict[str, tuple[tuple[int, int], ...]] = {}
    for white_policy in ("white_is_orange", "white_is_center", "gray_is_center"):
        for combine in ("orange_wins", "red_wins", "majority", "parity", "last"):
            name = f"{white_policy}+{combine}"
            candidates[name] = candidate_clicks(board, white_policy=white_policy, combine=combine)
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "events_jsonl",
        type=Path,
        default=Path("artifacts/kaggle/duck_controlled_stall_policy/latest/artifacts/ft09-0d8bbf25_p0_events.jsonl"),
        nargs="?",
    )
    args = parser.parse_args()

    board = load_level3_initial_board(args.events_jsonl)
    for name, clicks in sorted(candidate_suite(board).items(), key=lambda item: (len(item[1]), item[0])):
        click_text = ", ".join(f"({row},{col})" for row, col in clicks)
        print(f"{name}: {len(clicks)} clicks: {click_text}")


if __name__ == "__main__":
    main()
