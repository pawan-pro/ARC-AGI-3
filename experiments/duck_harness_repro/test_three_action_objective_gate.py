#!/usr/bin/env python3
"""Focused tests for the EXP-DUCK-037 objective confirmation gate."""

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
)
from duck_harness_repro.three_action_objective_gate import (
    ThreeActionObjectiveController,
    ThresholdFeedbackHypothesis,
)


ROOT = Path(__file__).resolve().parents[2]
MEMORY = PACKAGE / "exp_duck_034_mechanics_memory.json"
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_feedback_top_middle/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)
TOP = "ft09-level5-magenta-top"
MIDDLE = "ft09-level5-magenta-middle"
BOTTOM_RIGHT = "ft09-level5-magenta-bottom_right"


class ThreeActionObjectiveGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        events = [
            json.loads(line)
            for line in EVENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cls.actions = {
            event["action_num"]: event["board"]
            for event in events
            if event.get("type") == "action"
        }

    def controller(self) -> ThreeActionObjectiveController:
        return ThreeActionObjectiveController(
            memory=MechanicsMemory.load(MEMORY),
            context=ReasoningContext("ft09", "ft09-0d8bbf25", 5),
            initial_board=self.actions[69],
            action_order=(TOP, MIDDLE, BOTTOM_RIGHT),
            feedback=ThresholdFeedbackHypothesis(
                point=(63, 63),
                inactive_value=12,
                active_value=11,
                activation_threshold=2,
            ),
        )

    def advance_known_prefix(self, controller: ThreeActionObjectiveController) -> None:
        first = controller.next_action(self.actions[69])
        self.assertIsNotNone(first)
        self.assertTrue(controller.observe(self.actions[70]))
        second = controller.next_action(self.actions[70])
        self.assertIsNotNone(second)
        self.assertTrue(controller.observe(self.actions[71]))

    def test_known_first_two_actions_match_live_boards(self) -> None:
        controller = self.controller()
        self.advance_known_prefix(controller)
        self.assertIsNone(controller.stop_reason)
        self.assertEqual(["match", "match"], [r["prediction_check"] for r in controller.records])

    def test_third_action_level_completion_supports_objective(self) -> None:
        controller = self.controller()
        self.advance_known_prefix(controller)
        third = controller.next_action(self.actions[71])
        self.assertIsNotNone(third)
        assert third is not None
        self.assertTrue(controller.observe(third.predicted_board, level_completed=True))
        self.assertEqual("objective_completed", controller.stop_reason)
        self.assertTrue(controller.objective_supported)
        self.assertEqual("expected_level_transition", controller.records[-1]["prediction_check"])

    def test_exact_nonterminal_third_board_falsifies_and_stops(self) -> None:
        controller = self.controller()
        self.advance_known_prefix(controller)
        third = controller.next_action(self.actions[71])
        assert third is not None
        self.assertTrue(controller.observe(third.predicted_board))
        self.assertEqual("objective_falsified_no_transition", controller.stop_reason)
        self.assertFalse(controller.objective_supported)
        self.assertIsNone(controller.next_action(third.predicted_board))

    def test_early_level_transition_is_anomaly(self) -> None:
        controller = self.controller()
        first = controller.next_action(self.actions[69])
        assert first is not None
        self.assertFalse(controller.observe(first.predicted_board, level_completed=True))
        self.assertEqual("unexpected_level_transition", controller.stop_reason)

    def test_pixel_mismatch_aborts(self) -> None:
        controller = self.controller()
        first = controller.next_action(self.actions[69])
        assert first is not None
        wrong = [list(row) for row in first.predicted_board]
        wrong[0][0] = (wrong[0][0] + 1) % 16
        self.assertFalse(controller.observe(wrong))
        self.assertEqual("prediction_mismatch", controller.stop_reason)


if __name__ == "__main__":
    unittest.main()
