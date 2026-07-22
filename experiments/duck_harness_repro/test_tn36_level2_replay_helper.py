from tn36_level2_replay_helper import (
    PROVEN_LEVEL2_CLICKS,
    plan_tn36_level2_replay,
)


def make_grid() -> list[list[int]]:
    grid = [[1 for _ in range(64)] for _ in range(64)]
    grid[32][1] = 2
    grid[32][33] = 0
    for col in (8, 13, 18, 23):
        grid[33][col] = 5
    return grid


def test_proven_trace_is_returned_exactly() -> None:
    plan = plan_tn36_level2_replay(make_grid())
    assert plan == [
        {"row": row, "col": col}
        for row, col in PROVEN_LEVEL2_CLICKS
    ]
    assert len(plan) == 26


def test_signature_mismatch_is_rejected() -> None:
    grid = make_grid()
    grid[33][8] = 1
    assert plan_tn36_level2_replay(grid) is None


def test_non_64_square_board_is_rejected() -> None:
    assert plan_tn36_level2_replay([[0]]) is None
