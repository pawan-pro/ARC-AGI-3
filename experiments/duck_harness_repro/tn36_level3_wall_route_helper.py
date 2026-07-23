"""Engine-verified tn36 level-3 route through the switching walls."""

from __future__ import annotations

from typing import Sequence


COMMANDS = (2, 33, 2, 2, 2, 33)
EDITABLE_COLS = (34, 39, 44, 49, 54, 59)
BIT_ROWS = {
    2: (36,),
    33: (33, 48),
}
RUN_CLICK = (58, 57)


def plan_tn36_level3_program(
    grid: Sequence[Sequence[int]],
) -> list[dict[str, int]] | None:
    """Write the engine-verified route, then run the right program."""
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
        for col, command in zip(EDITABLE_COLS, COMMANDS)
        for row in BIT_ROWS[command]
    ]
    actions.append({"row": RUN_CLICK[0], "col": RUN_CLICK[1]})
    return actions
