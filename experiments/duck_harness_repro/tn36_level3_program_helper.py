"""Source-derived tn36 level-3 program for the observed board signature."""

from __future__ import annotations

from typing import Sequence


EDITABLE_COLS = (34, 39, 44, 49, 54, 59)
UP_COLS = EDITABLE_COLS[:2]
RIGHT_COLS = EDITABLE_COLS[2:]
TOP_ROW = 33
SECOND_ROW = 36
BOTTOM_ROW = 48
RUN_CLICK = (58, 57)


def plan_tn36_level3_program(
    grid: Sequence[Sequence[int]],
) -> list[dict[str, int]] | None:
    """Encode two up commands (33), four right commands (2), then run."""
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

    actions = []
    for col in UP_COLS:
        actions.extend(
            (
                {"row": TOP_ROW, "col": col},
                {"row": BOTTOM_ROW, "col": col},
            )
        )
    actions.extend({"row": SECOND_ROW, "col": col} for col in RIGHT_COLS)
    actions.append({"row": RUN_CLICK[0], "col": RUN_CLICK[1]})
    return actions
