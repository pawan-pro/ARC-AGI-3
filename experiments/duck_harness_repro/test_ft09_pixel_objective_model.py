#!/usr/bin/env python3
"""Tests for the EXP-DUCK-030 role-neutral ft09 learner."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ft09_pixel_objective_model import choose_next_click, infer_objective


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_level4_overlap/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)


class PixelObjectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = [
            json.loads(line)
            for line in EVENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cls.boundary = next(
            index
            for index, event in enumerate(cls.events)
            if int(event.get("level") or 0) == 4
            and bool(event.get("level_completed"))
        )
        cls.model = infer_objective(
            cls.events[: cls.boundary], cls.events[cls.boundary]["board"]
        )

    def test_discovers_geometry(self) -> None:
        self.assertEqual(18, len(self.model.normal_cells))
        self.assertEqual(3, len(self.model.clue_cells))
        self.assertEqual(8, self.model.spacing)

    def test_only_one_clue_interpretation_survives(self) -> None:
        self.assertEqual(sorted([0, 1]), sorted(dict(self.model.hypothesis_counts).values()))

    def test_closed_loop_policy_matches_successful_replay(self) -> None:
        board = self.events[self.boundary]["board"]
        for event in self.events[self.boundary + 1 :]:
            predicted = choose_next_click(board, self.model)
            display = str(event["action_display"])
            self.assertIn(f"row={predicted[0]}, col={predicted[1]}", display)
            board = event["board"]
        self.assertTrue(self.events[-1]["level_completed"])
        self.assertEqual(5, self.events[-1]["level"])

    def test_model_does_not_need_heldout_actions(self) -> None:
        shortened = self.events[: self.boundary]
        alternate = infer_objective(shortened, self.events[self.boundary]["board"])
        self.assertEqual(self.model.target, alternate.target)


if __name__ == "__main__":
    unittest.main()
