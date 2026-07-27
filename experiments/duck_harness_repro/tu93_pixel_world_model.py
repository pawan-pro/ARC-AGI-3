"""Learn and plan tu93-style navigation from action frames only.

The learner receives successful level 1-2 observations and one held-out initial
board. It does not import a game implementation or store a level route.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from math import gcd
from typing import Iterable, Sequence


Board = Sequence[Sequence[int]]
Point = tuple[int, int]


@dataclass(frozen=True)
class LearnedVisualModel:
    agent_color: int
    target_color: int
    token_color: int
    marker_color: int
    background_color: int
    node_color: int
    step: int
    action_deltas: dict[str, Point]
    training_transitions: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class WorldState:
    agent: Point
    target: Point
    tokens: frozenset[Point]
    locks: dict[Point, Point]
    nodes: frozenset[Point]


@dataclass(frozen=True)
class PlanStep:
    index: int
    action: str
    destination: Point
    collected_token: bool
    unlocked: Point | None


@dataclass(frozen=True)
class PlanResult:
    actions: tuple[str, ...] | None
    steps: tuple[PlanStep, ...]
    explored_states: int
    use_marker_locks: bool

    def to_dict(self) -> dict:
        return {
            "actions": list(self.actions) if self.actions else None,
            "steps": [asdict(step) for step in self.steps],
            "explored_states": self.explored_states,
            "use_marker_locks": self.use_marker_locks,
        }


def components(board: Board, color: int) -> list[list[Point]]:
    remaining = {
        (row, col)
        for row, values in enumerate(board)
        for col, value in enumerate(values)
        if int(value) == color
    }
    found: list[list[Point]] = []
    while remaining:
        seed = remaining.pop()
        queue = [seed]
        component = [seed]
        while queue:
            row, col = queue.pop()
            for drow, dcol in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                neighbor = (row + drow, col + dcol)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
                    component.append(neighbor)
        found.append(component)
    return found


def center(component: Sequence[Point]) -> Point:
    rows = [point[0] for point in component]
    cols = [point[1] for point in component]
    return ((min(rows) + max(rows)) // 2, (min(cols) + max(cols)) // 2)


def small_component_centers(board: Board, color: int) -> list[Point]:
    return [
        center(component)
        for component in components(board, color)
        if 1 <= len(component) <= 16
    ]


def _event_board(event: dict) -> Board:
    board = event.get("board")
    if not board:
        raise ValueError("Training event is missing a board.")
    return board


def _same_level_pairs(events: Sequence[dict]) -> Iterable[tuple[dict, dict]]:
    for previous, current in zip(events, events[1:]):
        if (
            int(previous.get("level", -1)) == int(current.get("level", -2))
            and not float(current.get("reward", 0) or 0)
        ):
            yield previous, current


def infer_agent_color(events: Sequence[dict]) -> int:
    scores: Counter[int] = Counter()
    for previous, current in _same_level_pairs(events):
        before = _event_board(previous)
        after = _event_board(current)
        colors = set(value for row in before for value in row)
        for color in colors:
            old_centers = small_component_centers(before, int(color))
            new_centers = small_component_centers(after, int(color))
            if len(old_centers) != 1 or len(new_centers) != 1:
                continue
            drow = new_centers[0][0] - old_centers[0][0]
            dcol = new_centers[0][1] - old_centers[0][1]
            if (abs(drow), abs(dcol)) in {(0, 6), (6, 0)}:
                scores[int(color)] += 1
    if not scores:
        raise ValueError("Could not identify a consistently moving component.")
    return scores.most_common(1)[0][0]


def infer_action_deltas(
    events: Sequence[dict],
    agent_color: int,
) -> tuple[dict[str, Point], int]:
    observed: dict[str, Counter[Point]] = defaultdict(Counter)
    transitions = 0
    for previous, current in _same_level_pairs(events):
        old = small_component_centers(_event_board(previous), agent_color)
        new = small_component_centers(_event_board(current), agent_color)
        if len(old) != 1 or len(new) != 1:
            continue
        delta = (new[0][0] - old[0][0], new[0][1] - old[0][1])
        if delta == (0, 0):
            continue
        action = str(current.get("action_display") or "")
        observed[action][delta] += 1
        transitions += 1
    mapping = {
        action: counts.most_common(1)[0][0]
        for action, counts in observed.items()
    }
    if len(mapping) != 4:
        raise ValueError(f"Expected four learned movement actions, got {mapping}.")
    return dict(sorted(mapping.items())), transitions


def infer_target_color(
    events: Sequence[dict],
    agent_color: int,
    action_deltas: dict[str, Point],
) -> int:
    candidates: Counter[int] = Counter()
    for previous, current in zip(events, events[1:]):
        if not float(current.get("reward", 0) or 0):
            continue
        old = small_component_centers(_event_board(previous), agent_color)
        action = str(current.get("action_display") or "")
        if len(old) != 1 or action not in action_deltas:
            continue
        drow, dcol = action_deltas[action]
        destination = (old[0][0] + drow, old[0][1] + dcol)
        candidates[int(_event_board(previous)[destination[0]][destination[1]])] += 1
    if not candidates:
        raise ValueError("Could not infer the level-completion target color.")
    return candidates.most_common(1)[0][0]


def infer_token_and_node_colors(
    events: Sequence[dict],
    agent_color: int,
    target_color: int,
) -> tuple[int, int]:
    token_candidates: Counter[int] = Counter()
    node_candidates: Counter[int] = Counter()
    for previous, current in _same_level_pairs(events):
        before = _event_board(previous)
        after = _event_board(current)
        new_agent = small_component_centers(after, agent_color)
        if len(new_agent) != 1:
            continue
        row, col = new_agent[0]
        prior_color = int(before[row][col])
        if prior_color in {agent_color, target_color}:
            continue
        before_count = sum(value == prior_color for values in before for value in values)
        after_count = sum(value == prior_color for values in after for value in values)
        if after_count < before_count and 6 <= prior_color <= 15:
            token_candidates[prior_color] += 1
        else:
            node_candidates[prior_color] += 1
    if not token_candidates or not node_candidates:
        raise ValueError("Could not separate collectible tokens from ordinary nodes.")
    return (
        token_candidates.most_common(1)[0][0],
        node_candidates.most_common(1)[0][0],
    )


def infer_marker_color(events: Sequence[dict], token_color: int) -> int:
    candidates: Counter[int] = Counter()
    for event in events:
        board = _event_board(event)
        for token in components(board, token_color):
            if not 6 <= len(token) <= 9:
                continue
            row, col = center(token)
            for y in range(max(0, row - 1), min(len(board), row + 2)):
                for x in range(max(0, col - 1), min(len(board[0]), col + 2)):
                    color = int(board[y][x])
                    if color != token_color:
                        candidates[color] += 1
    if not candidates:
        raise ValueError("Could not infer the marker embedded in a token.")
    return candidates.most_common(1)[0][0]


def learn_visual_model(events: Sequence[dict]) -> LearnedVisualModel:
    if len(events) < 3:
        raise ValueError("At least three training action frames are required.")
    agent_color = infer_agent_color(events)
    action_deltas, transition_count = infer_action_deltas(events, agent_color)
    target_color = infer_target_color(events, agent_color, action_deltas)
    token_color, node_color = infer_token_and_node_colors(
        events,
        agent_color,
        target_color,
    )
    marker_color = infer_marker_color(events, token_color)
    magnitude = 0
    for drow, dcol in action_deltas.values():
        magnitude = gcd(magnitude, abs(drow) + abs(dcol))
    color_counts = Counter(
        int(value)
        for event in events
        for row in _event_board(event)
        for value in row
    )
    return LearnedVisualModel(
        agent_color=agent_color,
        target_color=target_color,
        token_color=token_color,
        marker_color=marker_color,
        background_color=color_counts.most_common(1)[0][0],
        node_color=node_color,
        step=magnitude,
        action_deltas=action_deltas,
        training_transitions=transition_count,
    )


def parse_world(board: Board, model: LearnedVisualModel) -> WorldState:
    agents = small_component_centers(board, model.agent_color)
    targets = small_component_centers(board, model.target_color)
    tokens = set(small_component_centers(board, model.token_color))
    if len(agents) != 1 or len(targets) != 1 or not tokens:
        raise ValueError("Held-out board does not match the learned visual roles.")
    agent, target = agents[0], targets[0]
    marker_points = [
        point
        for component in components(board, model.marker_color)
        for point in component
    ]
    locks: dict[Point, Point] = {}
    for token in tokens:
        marker = min(
            marker_points,
            key=lambda point: abs(point[0] - token[0]) + abs(point[1] - token[1]),
        )
        locks[token] = (
            token[0] + (marker[0] - token[0]) * model.step,
            token[1] + (marker[1] - token[1]) * model.step,
        )

    offset_row = agent[0] % model.step
    offset_col = agent[1] % model.step
    node_colors = {
        model.node_color,
        model.agent_color,
        model.target_color,
        model.token_color,
    }
    nodes = {
        (row, col)
        for row in range(offset_row, len(board), model.step)
        for col in range(offset_col, len(board[0]), model.step)
        if int(board[row][col]) in node_colors
    }
    return WorldState(
        agent=agent,
        target=target,
        tokens=frozenset(tokens),
        locks=locks,
        nodes=frozenset(nodes),
    )


def _connected(board: Board, start: Point, end: Point, background: int) -> bool:
    row, col = start
    end_row, end_col = end
    if row == end_row:
        return all(
            int(board[row][x]) != background
            for x in range(min(col, end_col), max(col, end_col) + 1)
        )
    return all(
        int(board[y][col]) != background
        for y in range(min(row, end_row), max(row, end_row) + 1)
    )


def plan_world(
    board: Board,
    model: LearnedVisualModel,
    *,
    use_marker_locks: bool = True,
) -> PlanResult:
    world = parse_world(board, model)
    queue = deque([(world.agent, world.tokens, tuple())])
    seen = {(world.agent, world.tokens)}
    winner: tuple[str, ...] | None = None
    action_order = sorted(
        model.action_deltas,
        key=lambda action: int("".join(ch for ch in action if ch.isdigit()) or 99),
    )
    while queue:
        position, remaining, path = queue.popleft()
        if position == world.target and not remaining:
            winner = path
            break
        locked = {world.locks[token] for token in remaining} if use_marker_locks else set()
        for action in action_order:
            drow, dcol = model.action_deltas[action]
            destination = (position[0] + drow, position[1] + dcol)
            if (
                destination not in world.nodes
                or destination in locked
                or not _connected(
                    board,
                    position,
                    destination,
                    model.background_color,
                )
            ):
                continue
            next_remaining = frozenset(remaining - {destination})
            state = (destination, next_remaining)
            if state in seen:
                continue
            seen.add(state)
            queue.append((destination, next_remaining, path + (action,)))

    steps: list[PlanStep] = []
    if winner:
        position = world.agent
        remaining = set(world.tokens)
        for index, action in enumerate(winner, start=1):
            drow, dcol = model.action_deltas[action]
            destination = (position[0] + drow, position[1] + dcol)
            collected = destination in remaining
            unlocked = world.locks.get(destination) if collected else None
            remaining.discard(destination)
            steps.append(
                PlanStep(index, action, destination, collected, unlocked)
            )
            position = destination
    return PlanResult(
        actions=winner,
        steps=tuple(steps),
        explored_states=len(seen),
        use_marker_locks=use_marker_locks,
    )
