import json
import unittest
from pathlib import Path

from tn36_level1_helper import plan_tn36_level1


REPO_ROOT = Path(__file__).resolve().parents[2]


def initial_board(run_name):
    path = (
        REPO_ROOT
        / "artifacts"
        / "kaggle"
        / run_name
        / "latest"
        / "artifacts"
        / "tn36-ef4dde99_p0_events.jsonl"
    )
    events = [json.loads(line) for line in path.read_text().splitlines() if line]
    return next(event["board"] for event in events if event.get("type") == "initial")


class Tn36Level1HelperTests(unittest.TestCase):
    def test_matches_both_stored_level_starts(self):
        expected = [
            {"row": 42, "col": 26},
            {"row": 42, "col": 36},
            {"row": 42, "col": 41},
            {"row": 45, "col": 26},
            {"row": 45, "col": 36},
            {"row": 45, "col": 41},
            {"row": 55, "col": 36},
        ]
        for run_name in (
            "duck_public_repro_terminal_run",
            "duck_full_eval_ft09_overlap",
        ):
            self.assertEqual(plan_tn36_level1(initial_board(run_name)), expected)

    def test_rejects_changed_signature(self):
        board = initial_board("duck_full_eval_ft09_overlap")
        board[42][26] = 2
        self.assertIsNone(plan_tn36_level1(board))


if __name__ == "__main__":
    unittest.main()
