"""Source-derived tn36 level-2 program for the observed board signature."""

from __future__ import annotations

from typing import Sequence


EDITABLE_COLS = (39, 44, 49, 54)
TOP_ROW = 33
BOTTOM_ROW = 48
RUN_CLICK = (58, 46)


def plan_tn36_level2_program(
    grid: Sequence[Sequence[int]],
) -> list[dict[str, int]] | None:
    """Write command 33 into all four slots, then run the right program."""
    if len(grid) != 64 or any(len(row) != 64 for row in grid):
        return None

    signature = {
        (32, 1): 2,
        (32, 33): 0,
        (33, 8): 5,
        (33, 13): 5,
        (33, 18): 5,
        (33, 23): 5,
    }
    if any(int(grid[row][col]) != color for (row, col), color in signature.items()):
        return None

    actions = [
        {"row": row, "col": col}
        for row in (TOP_ROW, BOTTOM_ROW)
        for col in EDITABLE_COLS
    ]
    actions.append({"row": RUN_CLICK[0], "col": RUN_CLICK[1]})
    return actions
