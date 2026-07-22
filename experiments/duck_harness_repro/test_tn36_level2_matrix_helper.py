from tn36_level2_matrix_helper import (
    EDITABLE_COLS,
    TARGET_COLS,
    TARGET_ROWS,
    plan_tn36_level2,
)


def make_grid() -> list[list[int]]:
    grid = [[5 for _ in range(64)] for _ in range(64)]
    grid[32][1] = 2
    grid[32][33] = 0

    for row in TARGET_ROWS:
        for col in TARGET_COLS:
            color = 5 if row == 33 else 1
            if row in {33, 39, 45}:
                for marker_col in (col - 1, col, col + 1):
                    grid[row][marker_col] = color
            else:
                for marker_row in (row - 1, row, row + 1):
                    grid[marker_row][col] = color
        for col in EDITABLE_COLS:
            if row in {33, 39, 45}:
                for marker_col in (col - 1, col, col + 1):
                    grid[row][marker_col] = 1
            else:
                for marker_row in (row - 1, row, row + 1):
                    grid[marker_row][col] = 1

    for row in range(54, 63):
        for col in range(42, 51):
            grid[row][col] = 9
    for row, col in (
        (54, 42), (54, 43), (54, 49), (54, 50),
        (55, 42), (55, 50), (61, 42), (61, 50),
        (62, 42), (62, 43), (62, 49), (62, 50),
    ):
        grid[row][col] = 5
    return grid


def test_plan_copies_four_mismatches_then_submits() -> None:
    assert plan_tn36_level2(make_grid()) == [
        {"row": 33, "col": 39},
        {"row": 33, "col": 44},
        {"row": 33, "col": 49},
        {"row": 33, "col": 54},
        {"row": 58, "col": 46},
    ]


def test_matching_matrix_submits_without_extra_toggles() -> None:
    grid = make_grid()
    for col in EDITABLE_COLS:
        for marker_col in (col - 1, col, col + 1):
            grid[33][marker_col] = 5
    assert plan_tn36_level2(grid) == [{"row": 58, "col": 46}]


def test_signature_mismatch_is_rejected() -> None:
    grid = make_grid()
    grid[58][46] = 5
    assert plan_tn36_level2(grid) is None
