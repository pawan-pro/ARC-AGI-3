"""Signature-gated plan for the observed tn36 level-2 matrix puzzle."""

from __future__ import annotations

from collections import deque
from typing import Sequence


TARGET_ROWS = (33, 36, 39, 42, 45, 48)
TARGET_COLS = (8, 13, 18, 23)
EDITABLE_COLS = (39, 44, 49, 54)
MARKER_COLORS = {1, 5}
SUBMIT_COLOR = 9
SUBMIT_BBOX = (54, 42, 62, 50)
SUBMIT_AREA = 69


def _component(
    grid: Sequence[Sequence[int]], row: int, col: int
) -> list[tuple[int, int]]:
    color = int(grid[row][col])
    height = len(grid)
    width = len(grid[0])
    queue = deque([(row, col)])
    seen = {(row, col)}
    while queue:
        current_row, current_col = queue.popleft()
        for next_row, next_col in (
            (current_row - 1, current_col),
            (current_row + 1, current_col),
            (current_row, current_col - 1),
            (current_row, current_col + 1),
        ):
            if not (0 <= next_row < height and 0 <= next_col < width):
                continue
            if (next_row, next_col) in seen:
                continue
            if int(grid[next_row][next_col]) != color:
                continue
            seen.add((next_row, next_col))
            queue.append((next_row, next_col))
    return sorted(seen)


def _marker_footprint(row: int, col: int) -> tuple[tuple[int, int], ...]:
    if row in {33, 39, 45}:
        return ((row, col - 1), (row, col), (row, col + 1))
    return ((row - 1, col), (row, col), (row + 1, col))


def _valid_marker(grid: Sequence[Sequence[int]], row: int, col: int) -> bool:
    color = int(grid[row][col])
    return color in MARKER_COLORS and all(
        int(grid[marker_row][marker_col]) == color
        for marker_row, marker_col in _marker_footprint(row, col)
    )


def _submit_center(grid: Sequence[Sequence[int]]) -> tuple[int, int] | None:
    row, col = 58, 46
    if int(grid[row][col]) != SUBMIT_COLOR:
        return None
    pixels = _component(grid, row, col)
    bbox = (
        min(pixel_row for pixel_row, _ in pixels),
        min(pixel_col for _, pixel_col in pixels),
        max(pixel_row for pixel_row, _ in pixels),
        max(pixel_col for _, pixel_col in pixels),
    )
    if len(pixels) != SUBMIT_AREA or bbox != SUBMIT_BBOX:
        return None
    return row, col


def plan_tn36_level2(
    grid: Sequence[Sequence[int]],
) -> list[dict[str, int]] | None:
    """Click right-side mismatches, then the submit object."""
    if len(grid) != 64 or any(len(row) != 64 for row in grid):
        return None
    if int(grid[32][1]) != 2 or int(grid[32][33]) != 0:
        return None

    for row in TARGET_ROWS:
        for col in (*TARGET_COLS, *EDITABLE_COLS):
            if not _valid_marker(grid, row, col):
                return None

    submit = _submit_center(grid)
    if submit is None:
        return None

    actions = []
    for row in TARGET_ROWS:
        for target_col, editable_col in zip(TARGET_COLS, EDITABLE_COLS):
            if int(grid[row][target_col]) != int(grid[row][editable_col]):
                actions.append({"row": row, "col": editable_col})
    actions.append({"row": submit[0], "col": submit[1]})
    return actions
