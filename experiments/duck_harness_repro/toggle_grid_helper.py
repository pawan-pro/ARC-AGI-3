"""Small helper scaffold for ft09-style 3x3 toggle-grid puzzles.

The goal is not to change the Duck solver yet. This module captures the kind of
deterministic helper we should wire in after replay review confirms the exact
game mechanics: infer a simple Boolean rule from example grids, compute the
target grid, and click only the cells that differ from the current grid.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

Grid = tuple[tuple[int, ...], ...]
Rule = Callable[[int, int, int], int]
Point = tuple[int, int]


@dataclass(frozen=True)
class TogglePlan:
    """Click plan for turning one 3x3 grid into another."""

    rule_name: str
    target: Grid
    cells_to_toggle: tuple[tuple[int, int], ...]
    click_points: tuple[Point, ...]


def normalize_grid(rows: Sequence[Sequence[int]]) -> Grid:
    """Return a rectangular 0/1 grid."""

    if not rows:
        raise ValueError("grid is empty")
    width = len(rows[0])
    if width == 0:
        raise ValueError("grid has empty rows")
    normalized = []
    for row in rows:
        if len(row) != width:
            raise ValueError("grid rows must have equal width")
        normalized.append(tuple(1 if value else 0 for value in row))
    return tuple(normalized)


def _same_shape(*grids: Grid) -> None:
    shape = (len(grids[0]), len(grids[0][0]))
    for grid in grids:
        if len(grid) != shape[0] or any(len(row) != shape[1] for row in grid):
            raise ValueError("all grids must have the same shape")


def _apply_rule(a: Grid, b: Grid, c: Grid, rule: Rule) -> Grid:
    _same_shape(a, b, c)
    return tuple(
        tuple(rule(a[r][col], b[r][col], c[r][col]) for col in range(len(a[0])))
        for r in range(len(a))
    )


RULES: dict[str, Rule] = {
    "copy_a": lambda a, b, c: a,
    "copy_b": lambda a, b, c: b,
    "copy_c": lambda a, b, c: c,
    "not_a": lambda a, b, c: 1 - a,
    "not_b": lambda a, b, c: 1 - b,
    "not_c": lambda a, b, c: 1 - c,
    "or": lambda a, b, c: int(bool(a or b or c)),
    "and": lambda a, b, c: int(bool(a and b and c)),
    "xor": lambda a, b, c: (a + b + c) % 2,
    "majority": lambda a, b, c: int((a + b + c) >= 2),
    "minority": lambda a, b, c: int((a + b + c) <= 1),
    "a_xor_b": lambda a, b, c: a ^ b,
    "a_xor_c": lambda a, b, c: a ^ c,
    "b_xor_c": lambda a, b, c: b ^ c,
    "a_or_b": lambda a, b, c: int(bool(a or b)),
    "a_or_c": lambda a, b, c: int(bool(a or c)),
    "b_or_c": lambda a, b, c: int(bool(b or c)),
    "a_and_b": lambda a, b, c: int(bool(a and b)),
    "a_and_c": lambda a, b, c: int(bool(a and c)),
    "b_and_c": lambda a, b, c: int(bool(b and c)),
}


def matching_rules(examples: Iterable[tuple[Grid, Grid, Grid, Grid]]) -> tuple[str, ...]:
    """Return rule names that satisfy every `(a, b, c, output)` example."""

    example_list = list(examples)
    if not example_list:
        raise ValueError("at least one example is required")
    matches = []
    for name, rule in RULES.items():
        if all(_apply_rule(a, b, c, rule) == expected for a, b, c, expected in example_list):
            matches.append(name)
    return tuple(matches)


def differing_cells(current: Grid, target: Grid) -> tuple[tuple[int, int], ...]:
    """Return `(row, col)` cells that need one toggle."""

    _same_shape(current, target)
    return tuple(
        (r, col)
        for r in range(len(current))
        for col in range(len(current[0]))
        if current[r][col] != target[r][col]
    )


def cells_to_click_points(
    cells: Iterable[tuple[int, int]],
    *,
    top_left: Point,
    cell_size: int,
) -> tuple[Point, ...]:
    """Convert grid cells to pixel centers for a mouse-click action list."""

    x0, y0 = top_left
    half = cell_size // 2
    return tuple((x0 + col * cell_size + half, y0 + row * cell_size + half) for row, col in cells)


def plan_toggle_solution(
    examples: Iterable[tuple[Grid, Grid, Grid, Grid]],
    puzzle_inputs: tuple[Grid, Grid, Grid],
    current_output: Grid,
    *,
    top_left: Point,
    cell_size: int,
) -> TogglePlan:
    """Infer a rule and create a minimal click plan for the current output grid."""

    rule_names = matching_rules(examples)
    if not rule_names:
        raise ValueError("no supported Boolean rule matches examples")
    rule_name = rule_names[0]
    target = _apply_rule(*puzzle_inputs, RULES[rule_name])
    cells = differing_cells(current_output, target)
    return TogglePlan(
        rule_name=rule_name,
        target=target,
        cells_to_toggle=cells,
        click_points=cells_to_click_points(cells, top_left=top_left, cell_size=cell_size),
    )


def _self_test() -> None:
    a = normalize_grid([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    b = normalize_grid([[0, 1, 0], [0, 1, 0], [0, 1, 0]])
    c = normalize_grid([[0, 0, 1], [0, 0, 1], [1, 0, 0]])
    expected = normalize_grid([[1, 1, 1], [0, 1, 1], [1, 1, 1]])
    current = normalize_grid([[0, 1, 1], [0, 1, 0], [1, 1, 1]])
    plan = plan_toggle_solution([(a, b, c, expected)], (a, b, c), current, top_left=(10, 20), cell_size=8)
    assert plan.rule_name == "or"
    assert plan.cells_to_toggle == ((0, 0), (1, 2))
    assert plan.click_points == ((14, 24), (30, 32))


if __name__ == "__main__":
    _self_test()
    print("toggle_grid_helper self-test passed")

