#!/usr/bin/env python3
"""Focused tests for EXP-DUCK-032 ft09 operator calibration."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ft09_operator_calibration import (
    infer_calibrated_level5_objective,
    learn_mark_roles,
    leave_one_level_out,
    reconstruct_solved_examples,
)


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_level5_prospective/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)


class OperatorCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = [
            json.loads(line)
            for line in EVENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cls.examples = reconstruct_solved_examples(cls.events)
        cls.roles = learn_mark_roles(cls.examples)
        cls.objective = infer_calibrated_level5_objective(
            cls.events[69]["board"], cls.roles
        )

    def test_reconstructs_all_four_solved_targets(self) -> None:
        self.assertEqual([1, 2, 3, 4], [row.level for row in self.examples])
        self.assertEqual([8, 13, 23, 18], [len(row.target) for row in self.examples])

    def test_learns_stable_mark_roles(self) -> None:
        self.assertEqual({0: "same", 2: "different"}, self.roles)

    def test_every_leave_one_level_out_prediction_is_exact(self) -> None:
        folds = leave_one_level_out(self.examples)
        self.assertEqual(4, len(folds))
        self.assertTrue(all(row["exact_target_match"] for row in folds))
        self.assertTrue(all(row["target_signatures"] == 1 for row in folds))

    def test_level5_separates_clues_from_obstacles(self) -> None:
        self.assertEqual(27, len(self.objective.normal_cells))
        self.assertEqual(8, len(self.objective.clue_cells))
        self.assertEqual(3, len(self.objective.obstacle_cells))
        self.assertEqual(1, len(self.objective.uncovered_cells))

    def test_level5_has_one_actionable_nine_click_target(self) -> None:
        board = self.events[69]["board"]
        self.assertEqual(2, len(self.objective.unknown_role_models))
        self.assertEqual(9, len(self.objective.clicks(board)))
        self.assertEqual(
            [
                (6, 32),
                (22, 16),
                (22, 32),
                (22, 48),
                (38, 16),
                (38, 32),
                (38, 48),
                (54, 16),
                (54, 32),
            ],
            list(self.objective.clicks(board)),
        )


if __name__ == "__main__":
    unittest.main()
