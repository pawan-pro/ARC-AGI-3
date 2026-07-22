from tn36_level3_program_helper import (
    BOTTOM_ROW,
    RIGHT_COLS,
    RUN_CLICK,
    SECOND_ROW,
    TOP_ROW,
    UP_COLS,
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


def test_plan_encodes_two_up_then_four_right_commands() -> None:
    expected = []
    for col in UP_COLS:
        expected.extend(
            ({"row": TOP_ROW, "col": col}, {"row": BOTTOM_ROW, "col": col})
        )
    expected.extend({"row": SECOND_ROW, "col": col} for col in RIGHT_COLS)
    expected.append({"row": RUN_CLICK[0], "col": RUN_CLICK[1]})
    assert plan_tn36_level3_program(make_grid()) == expected
    assert len(expected) == 9


def test_signature_mismatch_is_rejected() -> None:
    grid = make_grid()
    grid[20][37] = 5
    assert plan_tn36_level3_program(grid) is None
