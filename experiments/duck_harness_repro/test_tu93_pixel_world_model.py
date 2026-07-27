import json
from pathlib import Path

from tu93_pixel_world_model import learn_visual_model, parse_world, plan_world


ROOT = Path(__file__).resolve().parents[2]
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_tu93_level3_route/latest/artifacts"
    / "tu93-0768757b_p0_events.jsonl"
)


def load_actions() -> list[dict]:
    return [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line).get("type") == "action"
    ]


def test_learns_controls_and_roles_from_levels_1_and_2() -> None:
    actions = load_actions()
    model = learn_visual_model(actions[:28])
    assert model.action_deltas == {
        "DOWN": (6, 0),
        "LEFT": (0, -6),
        "RIGHT": (0, 6),
        "UP": (-6, 0),
    }
    assert (
        model.agent_color,
        model.target_color,
        model.token_color,
        model.marker_color,
    ) == (9, 14, 8, 15)


def test_parses_three_visual_lock_dependencies() -> None:
    actions = load_actions()
    model = learn_visual_model(actions[:28])
    world = parse_world(actions[27]["board"], model)
    assert world.locks == {
        (25, 25): (25, 31),
        (25, 31): (31, 31),
        (37, 13): (37, 19),
    }


def test_heldout_plan_matches_replay_but_naive_model_does_not() -> None:
    actions = load_actions()
    model = learn_visual_model(actions[:28])
    expected = tuple(event["action_display"] for event in actions[28:])
    assert plan_world(actions[27]["board"], model).actions == expected
    assert (
        plan_world(
            actions[27]["board"],
            model,
            use_marker_locks=False,
        ).actions
        != expected
    )


def test_learner_contains_no_source_import_or_answer_route() -> None:
    source = Path(__file__).with_name("tu93_pixel_world_model.py").read_text(
        encoding="utf-8"
    )
    assert "tu93.py" not in source
    assert (
        "'UP', 'UP', 'RIGHT', 'UP', 'LEFT', 'LEFT'"
        not in source
    )
