"""Three-action confirmation gate for the ft09 level-five objective."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Sequence

from .bounded_reasoning_loop import (
    Board,
    MechanicsMemory,
    ReasoningContext,
    board_mismatches,
    board_sha256,
    freeze_board,
)
from .two_action_feedback_gate import _predict_regional_xor


Point = tuple[int, int]


@dataclass(frozen=True)
class ThresholdFeedbackHypothesis:
    point: Point
    inactive_value: int
    active_value: int
    activation_threshold: int

    def value_for(self, active_count: int) -> int:
        return (
            self.active_value
            if active_count >= self.activation_threshold
            else self.inactive_value
        )


@dataclass(frozen=True)
class ObjectivePlannedAction:
    index: int
    rule_id: str
    row: int
    col: int
    active_rules_after: tuple[str, ...]
    predicted_board: tuple[tuple[int, ...], ...]


class ThreeActionObjectiveController:
    """Confirm one pre-registered three-control objective and then stop."""

    def __init__(
        self,
        *,
        memory: MechanicsMemory,
        context: ReasoningContext,
        initial_board: Board,
        action_order: Sequence[str],
        feedback: ThresholdFeedbackHypothesis,
    ) -> None:
        if len(action_order) != 3 or len(set(action_order)) != 3:
            raise ValueError("The objective gate requires three different actions.")
        matches = memory.retrieve(context, initial_board)
        self.matches = {match.rule.rule_id: match for match in matches}
        missing = [rule_id for rule_id in action_order if rule_id not in self.matches]
        if missing:
            raise ValueError(f"Missing exact-board rules: {missing}")
        self.context = context
        self.action_order = tuple(action_order)
        self.feedback = feedback
        self.initial_sha256 = board_sha256(initial_board)
        self._last_board = freeze_board(initial_board)
        self._active_rules: set[str] = set()
        self._pending: tuple[
            ObjectivePlannedAction,
            tuple[tuple[int, ...], ...],
        ] | None = None
        self.records: list[dict[str, object]] = []
        self.stop_reason: str | None = None
        self.objective_supported: bool | None = None

    @property
    def stopped(self) -> bool:
        return self.stop_reason is not None

    def next_action(self, current_board: Board) -> ObjectivePlannedAction | None:
        if self.stopped:
            return None
        if self._pending is not None:
            raise RuntimeError("The previous action has not been observed.")
        current = freeze_board(current_board)
        if board_mismatches(self._last_board, current):
            self.stop_reason = "board_changed_before_action"
            return None
        if len(self.records) >= 3:
            raise RuntimeError("The three-action budget was exceeded.")

        rule_id = self.action_order[len(self.records)]
        match = self.matches[rule_id]
        predicted = _predict_regional_xor(current, match)
        active_after = set(self._active_rules)
        if rule_id in active_after:
            active_after.remove(rule_id)
        else:
            active_after.add(rule_id)
        row, col = self.feedback.point
        current_feedback = current[row][col]
        if current_feedback not in {
            self.feedback.inactive_value,
            self.feedback.active_value,
        }:
            raise ValueError(
                f"Unexpected feedback value {current_feedback} at "
                f"{self.feedback.point}."
            )
        predicted[row][col] = self.feedback.value_for(len(active_after))
        planned = ObjectivePlannedAction(
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
            "predicted_sha256": board_sha256(planned.predicted_board),
            "observed_sha256": board_sha256(observed),
            "feedback_point": list(self.feedback.point),
            "feedback_predicted": planned.predicted_board[
                self.feedback.point[0]
            ][self.feedback.point[1]],
            "feedback_observed": observed[self.feedback.point[0]][
                self.feedback.point[1]
            ],
            "level_completed": level_completed,
            "game_over": game_over,
            "run_complete": run_complete,
        }

        if game_over or run_complete:
            self.stop_reason = "game_over" if game_over else "run_complete"
            record["prediction_check"] = "terminal_anomaly"
            self.records.append(record)
            self._last_board = observed
            return False

        if level_completed:
            if planned.index == 3:
                self.stop_reason = "objective_completed"
                self.objective_supported = True
                record["prediction_check"] = "expected_level_transition"
                self.records.append(record)
                self._last_board = observed
                return True
            self.stop_reason = "unexpected_level_transition"
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
        if planned.index == 3:
            self.stop_reason = "objective_falsified_no_transition"
            self.objective_supported = False
        return True

    def trace_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "controller": "three_action_objective_gate",
            "runtime_llm": False,
            "context": asdict(self.context),
            "initial_sha256": self.initial_sha256,
            "action_budget": 3,
            "action_order": list(self.action_order),
            "feedback_hypothesis": {
                "point": list(self.feedback.point),
                "inactive_value": self.feedback.inactive_value,
                "active_value": self.feedback.active_value,
                "activation_threshold": self.feedback.activation_threshold,
            },
            "executed_actions": len(self.records),
            "stop_reason": self.stop_reason,
            "objective_supported": self.objective_supported,
            "records": self.records,
        }

    def save_trace(self, path: Path) -> None:
        path.write_text(
            json.dumps(self.trace_dict(), indent=2) + "\n",
            encoding="utf-8",
        )
