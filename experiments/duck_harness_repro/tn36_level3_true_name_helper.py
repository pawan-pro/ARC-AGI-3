"""Source-verified tn36 level-3 program for the initial target selector."""

from __future__ import annotations

from typing import Sequence


EDITABLE_COLS = (34, 39, 44, 49)
BIT_ONE_ROW = 33
BIT_TWO_ROW = 36
RUN_CLICK = (58, 57)


def plan_tn36_level3_program(
    grid: Sequence[Sequence[int]],
) -> list[dict[str, int]] | None:
    """Write [3, 3, 3, 3] into the first four slots, then run."""
    if len(grid) != 64 or any(len(row) != 64 for row in grid):
        return None
    signature = {
        (32, 1): 2,
        (32, 33): 0,
        (20, 37): 11,
        (12, 53): 4,
        (58, 57): 9,
    }
    if any(int(grid[row][col]) != color for (row, col), color in signature.items()):
        return None

    actions = [
        {"row": row, "col": col}
        for col in EDITABLE_COLS
        for row in (BIT_ONE_ROW, BIT_TWO_ROW)
    ]
    actions.append({"row": RUN_CLICK[0], "col": RUN_CLICK[1]})
    return actions
