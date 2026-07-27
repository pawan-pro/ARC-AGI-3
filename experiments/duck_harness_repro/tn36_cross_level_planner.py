"""Cross-level control memory and falsifiable program search for tn36.

The module deliberately contains no winning level program. It records reusable
control semantics, ranks movement commands from an explicit objective, and asks
an injected simulator to test complete program hypotheses.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True)
class ControlFact:
    command: int
    meaning: str
    delta_x: int
    delta_y: int
    learned_from: str
    confidence: float


@dataclass(frozen=True)
class ObjectiveHypothesis:
    statement: str
    success_test: str
    target_dx: int
    target_dy: int
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class CandidateResult:
    program: tuple[int, ...]
    solved: bool
    observed_level: int
    note: str = ""


@dataclass(frozen=True)
class SearchResult:
    objective: ObjectiveHypothesis
    command_order: tuple[int, ...]
    tested_candidates: int
    winning_program: tuple[int, ...] | None
    observations: tuple[CandidateResult, ...]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["winning_program"] = (
            list(self.winning_program) if self.winning_program else None
        )
        return payload


def tn36_control_memory() -> tuple[ControlFact, ...]:
    """Return movement facts retained after inspecting earlier levels.

    The command meanings come from the public game implementation and are
    confirmed by successful earlier-level runs. They are mechanics, not level
    answers.
    """

    return (
        ControlFact(1, "move left one cell", -1, 0, "levels 1-2", 1.0),
        ControlFact(2, "move right one cell", 1, 0, "levels 1-2", 1.0),
        ControlFact(3, "move down one cell", 0, 1, "levels 1-2", 1.0),
        ControlFact(33, "move up one cell", 0, -1, "levels 1-2", 1.0),
    )


def rank_commands_for_objective(
    objective: ObjectiveHypothesis,
    controls: Sequence[ControlFact],
) -> tuple[int, ...]:
    """Try commands that reduce target distance before commands that increase it."""

    def rank(fact: ControlFact) -> tuple[int, int]:
        before = abs(objective.target_dx) + abs(objective.target_dy)
        after = abs(objective.target_dx - fact.delta_x) + abs(
            objective.target_dy - fact.delta_y
        )
        return (after - before, fact.command)

    return tuple(fact.command for fact in sorted(controls, key=rank))


def candidate_programs(
    length: int,
    command_order: Sequence[int],
) -> Iterable[tuple[int, ...]]:
    """Generate hypotheses without embedding a puzzle-specific route."""

    if length <= 0:
        raise ValueError("Program length must be positive.")
    if not command_order:
        raise ValueError("At least one command is required.")
    return product(tuple(command_order), repeat=length)


def search_program(
    *,
    objective: ObjectiveHypothesis,
    controls: Sequence[ControlFact],
    length: int,
    evaluate: Callable[[tuple[int, ...]], CandidateResult],
    observation_limit: int = 12,
) -> SearchResult:
    """Search program hypotheses and stop only on the stated success test."""

    command_order = rank_commands_for_objective(objective, controls)
    observations: list[CandidateResult] = []
    tested = 0
    winner: tuple[int, ...] | None = None
    for program in candidate_programs(length, command_order):
        tested += 1
        result = evaluate(program)
        if len(observations) < observation_limit or result.solved:
            observations.append(result)
        if result.solved:
            winner = program
            break
    return SearchResult(
        objective=objective,
        command_order=command_order,
        tested_candidates=tested,
        winning_program=winner,
        observations=tuple(observations),
    )


def editable_clicks(
    program: Sequence[int],
    *,
    columns: Sequence[int],
    bit_rows: dict[int, Sequence[int]],
    run_click: tuple[int, int],
) -> list[dict[str, int]]:
    """Translate a discovered program into clicks on the visible editor."""

    if len(program) != len(columns):
        raise ValueError("Program and editor column counts differ.")
    actions: list[dict[str, int]] = []
    for column, command in zip(columns, program):
        if command not in bit_rows:
            raise ValueError(f"No visible encoding for command {command}.")
        actions.extend(
            {"row": int(row), "col": int(column)}
            for row in bit_rows[command]
        )
    actions.append({"row": int(run_click[0]), "col": int(run_click[1])})
    return actions
