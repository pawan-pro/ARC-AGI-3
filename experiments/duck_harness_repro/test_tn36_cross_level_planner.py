from pathlib import Path

from tn36_cross_level_planner import (
    CandidateResult,
    ObjectiveHypothesis,
    editable_clicks,
    rank_commands_for_objective,
    search_program,
    tn36_control_memory,
)


def objective(dx: int, dy: int) -> ObjectiveHypothesis:
    return ObjectiveHypothesis(
        statement="Reach the target.",
        success_test="Advance a level.",
        target_dx=dx,
        target_dy=dy,
        evidence=("visible displacement",),
    )


def test_command_ranking_uses_target_direction() -> None:
    controls = tn36_control_memory()
    assert rank_commands_for_objective(objective(4, -2), controls)[:2] == (2, 33)
    assert rank_commands_for_objective(objective(0, -4), controls)[0] == 33


def test_search_finds_injected_solution_without_storing_it() -> None:
    hidden_solution = (2, 33, 2)

    def evaluate(program: tuple[int, ...]) -> CandidateResult:
        return CandidateResult(
            program=program,
            solved=program == hidden_solution,
            observed_level=2 if program == hidden_solution else 1,
        )

    result = search_program(
        objective=objective(2, -1),
        controls=tn36_control_memory(),
        length=3,
        evaluate=evaluate,
    )
    assert result.winning_program == hidden_solution
    assert result.tested_candidates > 1


def test_visible_program_encoding_is_separate_from_search() -> None:
    actions = editable_clicks(
        (2, 33),
        columns=(10, 20),
        bit_rows={2: (4,), 33: (1, 6)},
        run_click=(9, 9),
    )
    assert actions == [
        {"row": 4, "col": 10},
        {"row": 1, "col": 20},
        {"row": 6, "col": 20},
        {"row": 9, "col": 9},
    ]


def test_planner_source_does_not_store_known_six_command_answer() -> None:
    source = Path(__file__).with_name("tn36_cross_level_planner.py").read_text(
        encoding="utf-8"
    )
    assert "2, 33, 2, 2, 2, 33" not in source
