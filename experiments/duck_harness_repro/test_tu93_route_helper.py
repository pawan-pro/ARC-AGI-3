import json
import unittest
from pathlib import Path

from tu93_route_helper import LEVEL_ROUTES, board_crc32, plan_tu93_route


REPO_ROOT = Path(__file__).resolve().parents[2]


def events(run_name):
    path = (
        REPO_ROOT
        / "artifacts"
        / "kaggle"
        / run_name
        / "latest"
        / "artifacts"
        / "tu93-0768757b_p0_events.jsonl"
    )
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def level_start(run_name, level):
    stored = events(run_name)
    if level == 1:
        return next(event["board"] for event in stored if event.get("type") == "initial")
    return next(
        event["board"]
        for event in stored
        if event.get("type") == "action"
        and event.get("action_display") == "RESET"
        and event.get("level") == level
    )


class Tu93RouteHelperTests(unittest.TestCase):
    def test_matches_repeated_level_starts(self):
        for run_name in (
            "duck_public_repro_terminal_run",
            "duck_full_eval_ft09_overlap",
            "duck_full_eval_tn36_postlude",
        ):
            for level in (1, 2):
                with self.subTest(run_name=run_name, level=level):
                    self.assertEqual(
                        plan_tu93_route(level_start(run_name, level), level),
                        LEVEL_ROUTES[level],
                    )

    def test_rejects_changed_board_or_unknown_level(self):
        board = level_start("duck_full_eval_tn36_postlude", 1)
        board[0][0] = (board[0][0] + 1) % 16
        self.assertIsNone(plan_tu93_route(board, 1))
        self.assertIsNone(plan_tu93_route([[0]], 1))
        self.assertIsNone(plan_tu93_route(level_start("duck_full_eval_tn36_postlude", 1), 3))

    def test_expected_route_lengths(self):
        self.assertEqual([len(LEVEL_ROUTES[level]) for level in (1, 2)], [18, 10])
        self.assertEqual(board_crc32([[0]]), None)


if __name__ == "__main__":
    unittest.main()
