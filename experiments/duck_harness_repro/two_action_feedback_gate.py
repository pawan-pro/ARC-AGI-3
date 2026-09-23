"""Two-action order gate for a regional XOR plus state-feedback hypothesis."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Sequence

from .bounded_reasoning_loop import (
    Board,
    MechanicsMemory,
    ReasoningContext,
    RuleMatch,
    board_mismatches,
    board_sha256,
    freeze_board,
)


Point = tuple[int, int]


@dataclass(frozen=True)
class FeedbackHypothesis:
    point: Point
    inactive_value: int
    active_value: int
    active_rules: frozenset[str]

    def value_for(self, active_rules: frozenset[str]) -> int:
        return (
            self.active_value
            if self.active_rules.issubset(active_rules)
            else self.inactive_value
        )


@dataclass(frozen=True)
class FeedbackPlannedAction:
    index: int
    rule_id: str
    row: int
    col: int
    active_rules_after: tuple[str, ...]
    predicted_board: tuple[tuple[int, ...], ...]


def _predict_regional_xor(board: Board, match: RuleMatch) -> list[list[int]]:
    predicted = [list(row) for row in freeze_board(board)]
    center_row, center_col = match.action_center
    for transition in match.rule.relative_transitions:
        row = center_row + transition.drow
        col = center_col + transition.dcol
        observed = predicted[row][col]
        if observed == transition.before:
            predicted[row][col] = transition.after
        elif observed == transition.after:
            predicted[row][col] = transition.before
        else:
            raise ValueError(
                f"{match.rule.rule_id} expected "
                f"{transition.before}/{transition.after} at {(row, col)}, "
                f"found {observed}."
            )
    return predicted


class TwoActionFeedbackController:
    """Execute exactly two configured controls under one complete-board model."""

    def __init__(
        self,
        *,
        memory: MechanicsMemory,
        context: ReasoningContext,
        initial_board: Board,
        action_order: Sequence[str],
        feedback: FeedbackHypothesis,
    ) -> None:
        if len(action_order) != 2 or len(set(action_order)) != 2:
            raise ValueError("The order gate requires two different actions.")
        matches = memory.retrieve(context, initial_board)
        self.matches = {match.rule.rule_id: match for match in matches}
        missing = [rule_id for rule_id in action_order if rule_id not in self.matches]
        if missing:
            raise ValueError(f"Missing exact-board rules: {missing}")
        if not feedback.active_rules.issubset(self.matches):
            raise ValueError("Feedback hypothesis names an unavailable rule.")
        self.context = context
        self.action_order = tuple(action_order)
        self.feedback = feedback
        self.initial_sha256 = board_sha256(initial_board)
        self._last_board = freeze_board(initial_board)
        self._active_rules: set[str] = set()
        self._pending: tuple[
            FeedbackPlannedAction,
            tuple[tuple[int, ...], ...],
        ] | None = None
        self.records: list[dict[str, object]] = []
        self.stop_reason: str | None = None

    @property
    def stopped(self) -> bool:
        return self.stop_reason is not None

    def next_action(self, current_board: Board) -> FeedbackPlannedAction | None:
        if self.stopped:
            return None
        if self._pending is not None:
            raise RuntimeError("The previous action has not been observed.")
        current = freeze_board(current_board)
        if board_mismatches(self._last_board, current):
            self.stop_reason = "board_changed_before_action"
            return None
        if len(self.records) >= 2:
            self.stop_reason = "two_action_plan_complete"
            return None
        rule_id = self.action_order[len(self.records)]
        match = self.matches[rule_id]
        predicted = _predict_regional_xor(current, match)
        active_after = set(self._active_rules)
        if rule_id in active_after:
            active_after.remove(rule_id)
        else:
            active_after.add(rule_id)
        feedback_value = self.feedback.value_for(frozenset(active_after))
        row, col = self.feedback.point
        current_feedback = current[row][col]
        if current_feedback not in {
            self.feedback.inactive_value,
            self.feedback.active_value,
        }:
            raise ValueError(
                f"Unexpected feedback value {current_feedback} at {self.feedback.point}."
            )
        predicted[row][col] = feedback_value
        planned = FeedbackPlannedAction(
            index=len(self.records) + 1,
            rule_id=rule_id,
            row=match.action_center[0],
            col=match.action_center[1],
            active_rules_after=tuple(sorted(active_after)),
            predicted_board=freeze_board(predicted),
        )
        self._pending = (planned, current)
        return planned

    def observe(
        self,
        observed_board: Board,
        *,
        level_completed: bool = False,
        game_over: bool = False,
        run_complete: bool = False,
    ) -> bool:
        if self._pending is None:
            raise RuntimeError("No action is awaiting observation.")
        planned, before = self._pending
        self._pending = None
        observed = freeze_board(observed_board)
        record: dict[str, object] = {
            "step": planned.index,
            "rule_id": planned.rule_id,
            "action": {"kind": "mouse", "row": planned.row, "col": planned.col},
            "active_rules_after": list(planned.active_rules_after),
            "before_sha256": board_sha256(before),
            "observed_sha256": board_sha256(observed),
            "feedback_point": list(self.feedback.point),
            "feedback_observed": observed[self.feedback.point[0]][
                self.feedback.point[1]
            ],
            "level_completed": level_completed,
            "game_over": game_over,
            "run_complete": run_complete,
        }
        if level_completed or game_over or run_complete:
            if level_completed:
                self.stop_reason = "unexpected_level_transition"
            elif game_over:
                self.stop_reason = "game_over"
            else:
                self.stop_reason = "run_complete"
            record["prediction_check"] = "terminal_anomaly"
            self.records.append(record)
            self._last_board = observed
            return False

        mismatches = board_mismatches(planned.predicted_board, observed)
        record["prediction_check"] = "match" if not mismatches else "mismatch"
        record["mismatch_count"] = len(mismatches)
        record["mismatch_sample"] = [list(item) for item in mismatches[:12]]
        self.records.append(record)
        self._last_board = observed
        if mismatches:
            self.stop_reason = "prediction_mismatch"
            return False
        self._active_rules = set(planned.active_rules_after)
        if len(self.records) == 2:
            self.stop_reason = "two_action_plan_complete"
        return True

    def trace_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "controller": "two_action_feedback_gate",
            "runtime_llm": False,
            "context": asdict(self.context),
            "initial_sha256": self.initial_sha256,
            "action_budget": 2,
            "action_order": list(self.action_order),
            "feedback_hypothesis": {
                "point": list(self.feedback.point),
                "inactive_value": self.feedback.inactive_value,
                "active_value": self.feedback.active_value,
                "active_rules": sorted(self.feedback.active_rules),
            },
            "executed_actions": len(self.records),
            "stop_reason": self.stop_reason,
            "records": self.records,
        }

    def save_trace(self, path: Path) -> None:
        path.write_text(
            json.dumps(self.trace_dict(), indent=2) + "\n",
            encoding="utf-8",
        )
