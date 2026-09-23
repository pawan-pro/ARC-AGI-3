#!/usr/bin/env python3
"""Focused tests for the EXP-DUCK-035 feedback-order gate."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE.parent))

from duck_harness_repro.bounded_reasoning_loop import (
    MechanicsMemory,
    ReasoningContext,
    freeze_board,
)
from duck_harness_repro.two_action_feedback_gate import (
    FeedbackHypothesis,
    TwoActionFeedbackController,
)


ROOT = Path(__file__).resolve().parents[2]
MEMORY = PACKAGE / "exp_duck_034_mechanics_memory.json"
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_bounded_gray_reasoner/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)
TOP = "ft09-level5-magenta-top"
MIDDLE = "ft09-level5-magenta-middle"


class TwoActionFeedbackGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = [
            json.loads(line)
            for line in EVENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cls.memory = MechanicsMemory.load(MEMORY)
        cls.context = ReasoningContext("ft09", "ft09-0d8bbf25", 5)
        cls.feedback = FeedbackHypothesis(
            point=(63, 63),
            inactive_value=12,
            active_value=11,
            active_rules=frozenset({TOP, MIDDLE}),
        )

    def controller(self, order: tuple[str, str]) -> TwoActionFeedbackController:
        return TwoActionFeedbackController(
            memory=self.memory,
            context=self.context,
            initial_board=self.events[69]["board"],
            action_order=order,
            feedback=self.feedback,
        )

    def test_top_middle_replays_live_result_exactly(self) -> None:
        controller = self.controller((TOP, MIDDLE))
        first = controller.next_action(self.events[69]["board"])
        self.assertIsNotNone(first)
        self.assertTrue(controller.observe(self.events[70]["board"]))
        second = controller.next_action(self.events[70]["board"])
        self.assertIsNotNone(second)
        self.assertTrue(controller.observe(self.events[71]["board"]))
        self.assertEqual("two_action_plan_complete", controller.stop_reason)
        self.assertTrue(
            all(row["prediction_check"] == "match" for row in controller.records)
        )

    def test_middle_top_has_the_same_combination_state_prediction(self) -> None:
        controller = self.controller((MIDDLE, TOP))
        board = freeze_board(self.events[69]["board"])
        first = controller.next_action(board)
        self.assertIsNotNone(first)
        assert first is not None
        self.assertEqual((30, 24), (first.row, first.col))
        board = first.predicted_board
        self.assertEqual(12, board[63][63])
        self.assertTrue(controller.observe(board))
        second = controller.next_action(board)
        self.assertIsNotNone(second)
        assert second is not None
        self.assertEqual((14, 24), (second.row, second.col))
        self.assertEqual(11, second.predicted_board[63][63])

    def test_any_extra_pixel_aborts_before_a_third_action(self) -> None:
        controller = self.controller((TOP, MIDDLE))
        first = controller.next_action(self.events[69]["board"])
        assert first is not None
        wrong = [list(row) for row in first.predicted_board]
        wrong[0][0] = (wrong[0][0] + 1) % 16
        self.assertFalse(controller.observe(wrong))
        self.assertEqual("prediction_mismatch", controller.stop_reason)
        self.assertIsNone(controller.next_action(wrong))

    def test_terminal_events_abort_even_when_pixels_would_match(self) -> None:
        controller = self.controller((TOP, MIDDLE))
        first = controller.next_action(self.events[69]["board"])
        assert first is not None
        self.assertFalse(
            controller.observe(first.predicted_board, game_over=True)
        )
        self.assertEqual("game_over", controller.stop_reason)


if __name__ == "__main__":
    unittest.main()
