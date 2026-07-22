from tn36_level2_program_helper import (
    BOTTOM_ROW,
    EDITABLE_COLS,
    RUN_CLICK,
    TOP_ROW,
    plan_tn36_level2_program,
)


def make_grid() -> list[list[int]]:
    grid = [[1 for _ in range(64)] for _ in range(64)]
    grid[32][1] = 2
    grid[32][33] = 0
    for col in (8, 13, 18, 23):
        grid[33][col] = 5
    return grid


def test_plan_writes_33_to_all_four_commands_then_runs() -> None:
    expected = [
        {"row": row, "col": col}
        for row in (TOP_ROW, BOTTOM_ROW)
        for col in EDITABLE_COLS
    ]
    expected.append({"row": RUN_CLICK[0], "col": RUN_CLICK[1]})
    assert plan_tn36_level2_program(make_grid()) == expected
    assert len(expected) == 9


def test_signature_mismatch_is_rejected() -> None:
    grid = make_grid()
    grid[33][8] = 1
    assert plan_tn36_level2_program(grid) is None


def test_non_64_square_board_is_rejected() -> None:
    assert plan_tn36_level2_program([[0]]) is None
