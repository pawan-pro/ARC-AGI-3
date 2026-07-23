from tn36_level3_wall_route_helper import (
    BIT_ROWS,
    COMMANDS,
    EDITABLE_COLS,
    RUN_CLICK,
    plan_tn36_level3_program,
)


def make_grid() -> list[list[int]]:
    grid = [[1 for _ in range(64)] for _ in range(64)]
    for (row, col), color in {
        (32, 1): 2,
        (32, 33): 0,
        (20, 37): 11,
        (12, 53): 4,
        (58, 57): 9,
    }.items():
        grid[row][col] = color
    return grid


def test_plan_encodes_engine_verified_wall_route() -> None:
    expected = [
        {"row": row, "col": col}
        for col, command in zip(EDITABLE_COLS, COMMANDS)
        for row in BIT_ROWS[command]
    ]
    expected.append({"row": RUN_CLICK[0], "col": RUN_CLICK[1]})
    assert COMMANDS == (2, 33, 2, 2, 2, 33)
    assert plan_tn36_level3_program(make_grid()) == expected
    assert len(expected) == 9


def test_signature_mismatch_is_rejected() -> None:
    grid = make_grid()
    grid[12][53] = 5
    assert plan_tn36_level3_program(grid) is None
