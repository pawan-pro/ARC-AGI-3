from tn36_level3_true_name_helper import (
    BIT_ONE_ROW,
    BIT_TWO_ROW,
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


def test_plan_writes_four_code_three_commands() -> None:
    expected = [
        {"row": row, "col": col}
        for col in EDITABLE_COLS
        for row in (BIT_ONE_ROW, BIT_TWO_ROW)
    ]
    expected.append({"row": RUN_CLICK[0], "col": RUN_CLICK[1]})
    assert plan_tn36_level3_program(make_grid()) == expected
    assert len(expected) == 9


def test_signature_mismatch_is_rejected() -> None:
    grid = make_grid()
    grid[20][37] = 5
    assert plan_tn36_level3_program(grid) is None
