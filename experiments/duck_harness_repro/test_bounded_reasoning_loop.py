#!/usr/bin/env python3
"""Focused tests for the bounded mechanics-reasoning loop."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bounded_reasoning_loop import (
    ActionEffectRule,
    BoundedReasoningController,
    MechanicsMemory,
    ReasoningContext,
    RelativeTransition,
    board_sha256,
    build_exp033_memory,
    freeze_board,
    gray_code_clicks,
    observe_board,
    patch_values,
    propose_hypotheses,
)


ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "experiments/duck_harness_repro/exp_duck_033_validation.json"
ARM_ROOT = ROOT / "artifacts/kaggle/duck_ft09_level5_probe_top/latest"
EVENTS = ARM_ROOT / "artifacts/ft09-0d8bbf25_p0_events.jsonl"


class BoundedReasoningLoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
        cls.events = [
            json.loads(line)
            for line in EVENTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cls.untouched = cls.events[69]["board"]
        cls.top_after = cls.events[70]["board"]
        cls.memory = build_exp033_memory(cls.validation, cls.untouched)
        cls.context = ReasoningContext(
            game_family="ft09",
            game_id="ft09-0d8bbf25",
            level=5,
        )

    def test_observation_compacts_small_regions_without_game_names(self) -> None:
        observation = observe_board(self.untouched)
        centers = {candidate.center for candidate in observation.candidate_regions}
        self.assertEqual((64, 64), observation.shape)
        self.assertIn((14, 24), centers)
        self.assertIn((30, 24), centers)
        self.assertIn((46, 40), centers)
        self.assertNotIn("ft09", json.dumps(observation.compact_dict()))

    def test_validated_probe_evidence_builds_three_narrow_rules(self) -> None:
        self.assertEqual(3, len(self.memory.rules))
        self.assertEqual(
            [128, 164, 164],
            sorted(len(rule.relative_transitions) for rule in self.memory.rules),
        )
        self.assertTrue(
            all(rule.status == "observed_forward_only" for rule in self.memory.rules)
        )
        self.assertTrue(
            all(rule.transfer_scope == "exact_board" for rule in self.memory.rules)
        )

    def test_memory_retrieval_requires_the_exact_current_board(self) -> None:
        matches = self.memory.retrieve(self.context, self.untouched)
        self.assertEqual(3, len(matches))
        changed = copy.deepcopy(self.untouched)
        changed[0][0] = (changed[0][0] + 1) % 16
        self.assertEqual((), self.memory.retrieve(self.context, changed))

    def test_hypotheses_keep_set_and_reversible_xor_separate(self) -> None:
        hypotheses = propose_hypotheses(
            self.memory.retrieve(self.context, self.untouched)
        )
        self.assertEqual(
            {"monotone-set", "binary-xor"},
            {hypothesis.hypothesis_id for hypothesis in hypotheses},
        )

    def test_gray_code_is_the_recorded_seven_action_route(self) -> None:
        rule_ids = (
            "ft09-level5-magenta-top",
            "ft09-level5-magenta-middle",
            "ft09-level5-magenta-bottom_right",
        )
        self.assertEqual(
            (
                rule_ids[0],
                rule_ids[1],
                rule_ids[0],
                rule_ids[2],
                rule_ids[0],
                rule_ids[1],
                rule_ids[0],
            ),
            gray_code_clicks(rule_ids, max_actions=7),
        )
        with self.assertRaisesRegex(ValueError, "needs 7 actions"):
            gray_code_clicks(rule_ids, max_actions=6)

    def test_first_prediction_matches_live_top_probe_pixel_for_pixel(self) -> None:
        controller = BoundedReasoningController.from_memory(
            memory=self.memory,
            context=self.context,
            initial_board=self.untouched,
            selected_hypothesis="binary-xor",
            max_actions=7,
        )
        planned = controller.next_action(self.untouched)
        self.assertIsNotNone(planned)
        assert planned is not None
        self.assertEqual((14, 24), (planned.row, planned.col))
        self.assertEqual(freeze_board(self.top_after), planned.predicted_board)
        self.assertTrue(controller.observe(self.top_after))
        self.assertEqual(1, controller.hypotheses["binary-xor"].verified_steps)
        self.assertEqual(1, controller.hypotheses["monotone-set"].verified_steps)

    def test_simulated_xor_traversal_is_bounded_and_falsifiable(self) -> None:
        controller = BoundedReasoningController.from_memory(
            memory=self.memory,
            context=self.context,
            initial_board=self.untouched,
            selected_hypothesis="binary-xor",
            max_actions=7,
        )
        board = freeze_board(self.untouched)
        while not controller.stopped:
            planned = controller.next_action(board)
            if planned is None:
                break
            board = planned.predicted_board
            self.assertTrue(controller.observe(board))
        trace = controller.trace_dict()
        self.assertEqual(7, trace["executed_actions"])
        self.assertEqual("state_space_exhausted", trace["stop_reason"])
        self.assertEqual(
            7, controller.hypotheses["binary-xor"].verified_steps
        )
        self.assertEqual(
            "rejected", controller.hypotheses["monotone-set"].status
        )

    def test_prediction_mismatch_aborts_before_another_action(self) -> None:
        controller = BoundedReasoningController.from_memory(
            memory=self.memory,
            context=self.context,
            initial_board=self.untouched,
            selected_hypothesis="binary-xor",
            max_actions=7,
        )
        planned = controller.next_action(self.untouched)
        self.assertIsNotNone(planned)
        self.assertFalse(controller.observe(self.untouched))
        self.assertEqual("prediction_mismatch", controller.stop_reason)
        self.assertIsNone(controller.next_action(self.untouched))

    def test_level_completion_is_a_terminal_success_not_a_board_mismatch(self) -> None:
        controller = BoundedReasoningController.from_memory(
            memory=self.memory,
            context=self.context,
            initial_board=self.untouched,
            selected_hypothesis="binary-xor",
            max_actions=7,
        )
        planned = controller.next_action(self.untouched)
        self.assertIsNotNone(planned)
        self.assertTrue(controller.observe([[1]], level_completed=True))
        self.assertEqual("level_completed", controller.stop_reason)
        self.assertEqual(
            "terminal_level_transition",
            controller.records[0]["prediction_check"],
        )

    def test_promoted_anchor_rule_can_be_retrieved_at_a_later_level(self) -> None:
        board = [[0] * 9 for _ in range(9)]
        board[2][2] = 7
        patch = patch_values(board, (2, 2), 1)
        rule = ActionEffectRule(
            rule_id="synthetic-transfer",
            mechanic="sparse-regional-color-transition",
            action_kind="mouse",
            observed_center=(2, 2),
            anchor_color=7,
            anchor_area=1,
            anchor_patch_radius=1,
            anchor_patch=patch,
            relative_transitions=(RelativeTransition(0, 0, 7, 8),),
            status="validated_bidirectional",
            evidence_experiment="synthetic-test",
            observations=2,
            forward_verified_pixels=1,
            reverse_verified_pixels=1,
            game_family="synthetic",
            game_id="synthetic-a",
            level=1,
            board_shape=(9, 9),
            initial_board_sha256=board_sha256(board),
            transfer_scope="anchor_signature",
        )
        later = [[0] * 9 for _ in range(9)]
        later[6][6] = 7
        matches = MechanicsMemory([rule]).retrieve(
            ReasoningContext("synthetic", "synthetic-b", 2),
            later,
        )
        self.assertEqual(1, len(matches))
        self.assertEqual((6, 6), matches[0].action_center)
        self.assertEqual("anchor_signature", matches[0].match_mode)

    def test_runtime_memory_records_bidirectional_evidence_without_auto_transfer(
        self,
    ) -> None:
        controller = BoundedReasoningController.from_memory(
            memory=self.memory,
            context=self.context,
            initial_board=self.untouched,
            selected_hypothesis="binary-xor",
            max_actions=7,
        )
        board = freeze_board(self.untouched)
        while not controller.stopped:
            planned = controller.next_action(board)
            if planned is None:
                break
            board = planned.predicted_board
            controller.observe(board)
        snapshot = controller.memory_snapshot()
        by_id = {rule.rule_id: rule for rule in snapshot.rules}
        self.assertEqual(
            "validated_bidirectional_current_board",
            by_id["ft09-level5-magenta-top"].status,
        )
        self.assertEqual(
            "validated_bidirectional_current_board",
            by_id["ft09-level5-magenta-middle"].status,
        )
        self.assertEqual(
            "observed_forward_only",
            by_id["ft09-level5-magenta-bottom_right"].status,
        )
        self.assertTrue(
            all(rule.transfer_scope == "exact_board" for rule in snapshot.rules)
        )
        promoted = snapshot.promote_for_anchor_transfer(
            "ft09-level5-magenta-top"
        )
        promoted_top = next(
            rule
            for rule in promoted.rules
            if rule.rule_id == "ft09-level5-magenta-top"
        )
        self.assertEqual("validated_bidirectional", promoted_top.status)
        self.assertEqual("anchor_signature", promoted_top.transfer_scope)
        with self.assertRaisesRegex(ValueError, "not bidirectionally validated"):
            snapshot.promote_for_anchor_transfer(
                "ft09-level5-magenta-bottom_right"
            )


if __name__ == "__main__":
    unittest.main()
