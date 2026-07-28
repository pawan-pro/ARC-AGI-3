#!/usr/bin/env python3
"""Focused tests for the prospective ft09 level-5 objective learner."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ft09_level5_objective_model import infer_level5_objective


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_level4_overlap/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)


class Level5ObjectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = [
            json.loads(line)
            for line in EVENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cls.board = cls.events[-1]["board"]
        cls.objective = infer_level5_objective(cls.board)

    def test_level5_has_no_known_action_trace(self) -> None:
        self.assertEqual(5, self.events[-1]["level"])
        self.assertTrue(self.events[-1]["level_completed"])

    def test_geometry_is_discovered(self) -> None:
        self.assertEqual(27, len(self.objective.normal_cells))
        self.assertEqual(11, len(self.objective.clue_cells))
        self.assertEqual(8, self.objective.spacing)

    def test_semantic_ambiguity_has_one_target(self) -> None:
        self.assertEqual(2, len(self.objective.semantic_models))
        self.assertEqual(27, len(self.objective.target))

    def test_plan_changes_eighteen_cells(self) -> None:
        clicks = self.objective.clicks(self.board)
        self.assertEqual(18, len(clicks))
        self.assertEqual(18, len(set(clicks)))


if __name__ == "__main__":
    unittest.main()
