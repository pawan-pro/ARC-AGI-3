#!/usr/bin/env python3
"""Learn ft09 clue operators from solved levels and predict a new target."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import itertools
import math
import re


Cell = tuple[int, int]
Role = str
SAME = "same"
DIFFERENT = "different"


@dataclass(frozen=True)
class LevelExample:
    level: int
    board: list[list[int]]
    background: int
    spacing: int
    normal_cells: tuple[Cell, ...]
    clue_cells: tuple[Cell, ...]
    palette: tuple[int, ...]
    target: tuple[tuple[Cell, int], ...] = ()

    def target_dict(self) -> dict[Cell, int]:
        return dict(self.target)


@dataclass(frozen=True)
class CalibratedObjective:
    background: int
    state_colors: tuple[int, ...]
    spacing: int
    normal_cells: tuple[Cell, ...]
    clue_cells: tuple[Cell, ...]
    obstacle_cells: tuple[Cell, ...]
    learned_roles: tuple[tuple[int, Role], ...]
    unknown_role_models: tuple[tuple[tuple[int, Role], ...], ...]
    uncovered_cells: tuple[Cell, ...]
    target: tuple[tuple[Cell, int], ...]

    def target_dict(self) -> dict[Cell, int]:
        return dict(self.target)

    def clicks(self, board: list[list[int]]) -> tuple[Cell, ...]:
        return tuple(
            cell
            for cell, color in self.target
            if int(board[cell[0]][cell[1]]) != color
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "background": self.background,
            "state_colors": list(self.state_colors),
            "spacing": self.spacing,
            "normal_cells": [list(cell) for cell in self.normal_cells],
            "clue_cells": [list(cell) for cell in self.clue_cells],
            "obstacle_cells": [list(cell) for cell in self.obstacle_cells],
            "learned_roles": dict(self.learned_roles),
            "unknown_role_models": [
                dict(model) for model in self.unknown_role_models
            ],
            "uncovered_cells": [list(cell) for cell in self.uncovered_cells],
            "target": [
                {"cell": list(cell), "color": color}
                for cell, color in self.target
            ],
        }


def _components(board: list[list[int]], color: int) -> list[list[Cell]]:
    height, width = len(board), len(board[0])
    seen: set[Cell] = set()
    result: list[list[Cell]] = []
    for row in range(height):
        for col in range(width):
            if board[row][col] != color or (row, col) in seen:
                continue
            stack = [(row, col)]
            seen.add((row, col))
            component: list[Cell] = []
            while stack:
                current = stack.pop()
                component.append(current)
                cr, cc = current
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    neighbor = (cr + dr, cc + dc)
                    nr, nc = neighbor
                    if (
                        0 <= nr < height
                        and 0 <= nc < width
                        and neighbor not in seen
                        and board[nr][nc] == color
                    ):
                        seen.add(neighbor)
                        stack.append(neighbor)
            result.append(component)
    return result


def _solid_centers(
    board: list[list[int]], background: int
) -> tuple[tuple[Cell, ...], int]:
    blocks: list[tuple[int, int, int]] = []
    colors = sorted({value for row in board for value in row} - {background})
    for color in colors:
        for component in _components(board, color):
            rows = [cell[0] for cell in component]
            cols = [cell[1] for cell in component]
            height = max(rows) - min(rows) + 1
            width = max(cols) - min(cols) + 1
            if height == width and height >= 4 and len(component) == height * width:
                blocks.append((min(rows), min(cols), height))
    size_counts = Counter(size for _, _, size in blocks)
    block_size, count = size_counts.most_common(1)[0]
    if count < 8:
        raise ValueError("no repeated editable-cell geometry found")
    centers = tuple(
        sorted(
            (
                row + (block_size - 2) // 2,
                col + (block_size - 2) // 2,
            )
            for row, col, size in blocks
            if size == block_size
        )
    )
    row_values = sorted({row for row, _ in centers})
    col_values = sorted({col for _, col in centers})
    differences = [
        second - first
        for values in (row_values, col_values)
        for first, second in zip(values, values[1:])
    ]
    spacing = math.gcd(*differences)
    return centers, spacing


def _sample(
    board: list[list[int]], cell: Cell, spacing: int
) -> tuple[int, ...]:
    row, col = cell
    micro_step = spacing // 4
    return tuple(
        int(board[row + dr * micro_step][col + dc * micro_step])
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
    )


def _parse_action(action_display: str) -> Cell | None:
    match = re.search(r"row=(\d+), col=(\d+)", action_display)
    return tuple(map(int, match.groups())) if match else None


def _action_hits(cell: Cell, action: Cell, radius: int = 3) -> bool:
    return (
        abs(cell[0] - action[0]) <= radius
        and abs(cell[1] - action[1]) <= radius
    )


def _active_level1_example(events: list[dict]) -> LevelExample:
    board = events[0]["board"]
    background = Counter(value for row in board for value in row).most_common(1)[0][0]
    normal_cells, _ = _solid_centers(board, background)
    normal_set = set(normal_cells)
    candidates: list[Cell] = []
    for row in range(2, len(board) - 3):
        for col in range(2, len(board[0]) - 3):
            cell = (row, col)
            if cell in normal_set or int(board[row][col]) == background:
                continue
            samples = tuple(
                int(board[row + dr * 2][col + dc * 2])
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
            )
            if background in samples or len(set(samples)) <= 1:
                continue
            neighbors = tuple(
                (row + dr * 8, col + dc * 8)
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0)
            )
            if all(neighbor in normal_set for neighbor in neighbors):
                colors = {int(board[r][c]) for r, c in neighbors}
                if len(colors) == 1:
                    candidates.append(cell)
    if len(candidates) != 1:
        raise ValueError(f"expected one active tutorial clue, found {candidates}")
    clue = candidates[0]
    normal = tuple(
        (clue[0] + dr * 8, clue[1] + dc * 8)
        for dr in (-1, 0, 1)
        for dc in (-1, 0, 1)
        if (dr, dc) != (0, 0)
    )
    target = _reconstruct_target(events, 0, 9, normal)
    palette = tuple(
        sorted(
            {int(board[r][c]) for r, c in normal}
            | {int(board[clue[0]][clue[1]])}
            | set(target.values())
        )
    )
    return LevelExample(
        level=1,
        board=board,
        background=background,
        spacing=8,
        normal_cells=normal,
        clue_cells=(clue,),
        palette=palette,
        target=tuple((cell, target[cell]) for cell in normal),
    )


def _parse_level(
    events: list[dict], start: int, end: int
) -> LevelExample:
    board = events[start]["board"]
    level = int(events[start]["level"])
    background = Counter(value for row in board for value in row).most_common(1)[0][0]
    normal_cells, spacing = _solid_centers(board, background)
    if spacing != 8:
        raise ValueError(f"unexpected level-{level} spacing {spacing}")
    rows = range(
        min(row for row, _ in normal_cells),
        max(row for row, _ in normal_cells) + 1,
        spacing,
    )
    cols = range(
        min(col for _, col in normal_cells),
        max(col for _, col in normal_cells) + 1,
        spacing,
    )
    normal_set = set(normal_cells)
    varied = tuple(
        cell
        for cell in itertools.product(rows, cols)
        if cell not in normal_set
        and int(board[cell[0]][cell[1]]) != background
        and len(set(_sample(board, cell, spacing))) > 1
        and any(
            (
                cell[0] + dr * spacing,
                cell[1] + dc * spacing,
            )
            in normal_set
            for dr, dc in itertools.product((-1, 0, 1), repeat=2)
            if (dr, dc) != (0, 0)
        )
    )
    palette = tuple(
        sorted(
            {int(board[row][col]) for row, col in normal_cells}
            | {int(board[row][col]) for row, col in varied}
        )
    )
    target = _reconstruct_target(events, start, end, normal_cells)
    return LevelExample(
        level=level,
        board=board,
        background=background,
        spacing=spacing,
        normal_cells=normal_cells,
        clue_cells=varied,
        palette=palette,
        target=tuple((cell, target[cell]) for cell in normal_cells),
    )


def _reconstruct_target(
    events: list[dict], start: int, end: int, normal_cells: tuple[Cell, ...]
) -> dict[Cell, int]:
    board = events[start]["board"]
    transitions: dict[int, int] = {}
    for before, after in zip(events[start:end], events[start + 1 : end]):
        action = _parse_action(str(after.get("action_display") or ""))
        if action is None:
            continue
        cell = next(
            (candidate for candidate in normal_cells if _action_hits(candidate, action)),
            None,
        )
        if cell is None:
            continue
        previous = int(before["board"][cell[0]][cell[1]])
        observed = int(after["board"][cell[0]][cell[1]])
        if previous != observed:
            transitions[previous] = observed
    click_counts: Counter[Cell] = Counter()
    for event in events[start + 1 : end + 1]:
        action = _parse_action(str(event.get("action_display") or ""))
        if action is None:
            continue
        cell = next(
            (candidate for candidate in normal_cells if _action_hits(candidate, action)),
            None,
        )
        if cell is not None:
            click_counts[cell] += 1
    target: dict[Cell, int] = {}
    for cell in normal_cells:
        color = int(board[cell[0]][cell[1]])
        for _ in range(click_counts[cell]):
            if color not in transitions:
                raise ValueError(
                    f"missing observed transition from color {color} on level "
                    f"{events[start]['level']}"
                )
            color = transitions[color]
        target[cell] = color
    return target


def reconstruct_solved_examples(events: list[dict]) -> tuple[LevelExample, ...]:
    return (
        _active_level1_example(events),
        _parse_level(events, 9, 16),
        _parse_level(events, 16, 48),
        _parse_level(events, 48, 69),
    )


def learn_mark_roles(examples: tuple[LevelExample, ...]) -> dict[int, Role]:
    evidence: dict[int, set[Role]] = {}
    for example in examples:
        target = example.target_dict()
        normal_set = set(example.normal_cells)
        for row, col in example.clue_cells:
            center = int(example.board[row][col])
            samples = _sample(example.board, (row, col), example.spacing)
            for index, (dr, dc) in enumerate(itertools.product((-1, 0, 1), repeat=2)):
                if (dr, dc) == (0, 0):
                    continue
                cell = (row + dr * example.spacing, col + dc * example.spacing)
                if cell not in normal_set:
                    continue
                mark = int(samples[index])
                role = SAME if target[cell] == center else DIFFERENT
                evidence.setdefault(mark, set()).add(role)
    contradictory = {
        mark: roles for mark, roles in evidence.items() if len(roles) != 1
    }
    if contradictory:
        raise ValueError(f"contradictory mark roles: {contradictory}")
    return {mark: next(iter(roles)) for mark, roles in evidence.items()}


def _solve_targets(
    example: LevelExample,
    roles: dict[int, Role],
    allow_uncovered: bool,
    palette: tuple[int, ...] | None = None,
) -> tuple[tuple[tuple[Cell, int], ...], ...]:
    normal_set = set(example.normal_cells)
    candidate_palette = palette or example.palette
    choices = [
        tuple(
            color
            for color in candidate_palette
            if color != example.board[row][col]
        )
        for row, col in example.clue_cells
    ]
    targets: set[tuple[tuple[Cell, int], ...]] = set()
    for selected in itertools.product(*choices):
        other_by_clue = dict(zip(example.clue_cells, selected))
        votes: dict[Cell, list[int]] = {cell: [] for cell in example.normal_cells}
        for row, col in example.clue_cells:
            center = int(example.board[row][col])
            samples = _sample(example.board, (row, col), example.spacing)
            for index, (dr, dc) in enumerate(itertools.product((-1, 0, 1), repeat=2)):
                if (dr, dc) == (0, 0):
                    continue
                cell = (row + dr * example.spacing, col + dc * example.spacing)
                if cell not in normal_set:
                    continue
                mark = int(samples[index])
                role = roles.get(mark)
                if role == SAME:
                    votes[cell].append(center)
                elif role == DIFFERENT:
                    votes[cell].append(other_by_clue[(row, col)])
        if any(len(set(values)) > 1 for values in votes.values()):
            continue
        if not allow_uncovered and any(not values for values in votes.values()):
            continue
        target = tuple(
            (
                cell,
                values[0]
                if values
                else int(example.board[cell[0]][cell[1]]),
            )
            for cell, values in votes.items()
        )
        targets.add(target)
    return tuple(sorted(targets))


def leave_one_level_out(
    examples: tuple[LevelExample, ...]
) -> tuple[dict[str, object], ...]:
    folds: list[dict[str, object]] = []
    for heldout in examples:
        training = tuple(example for example in examples if example.level != heldout.level)
        roles = learn_mark_roles(training)
        predictions = _solve_targets(heldout, roles, allow_uncovered=False)
        used_global_palette = False
        if not predictions:
            global_palette = tuple(
                sorted(
                    set(heldout.palette).union(
                        *[set(example.palette) for example in training]
                    )
                )
            )
            predictions = _solve_targets(
                heldout,
                roles,
                allow_uncovered=False,
                palette=global_palette,
            )
            used_global_palette = True
        exact = len(predictions) == 1 and predictions[0] == heldout.target
        folds.append(
            {
                "heldout_level": heldout.level,
                "training_levels": [
                    example.level for example in training
                ],
                "learned_roles": roles,
                "target_signatures": len(predictions),
                "target_cells": len(heldout.target),
                "used_calibrated_global_palette": used_global_palette,
                "exact_target_match": exact,
            }
        )
    return tuple(folds)


def infer_calibrated_level5_objective(
    board: list[list[int]],
    learned_roles: dict[int, Role] | None = None,
) -> CalibratedObjective:
    roles = dict(learned_roles or {0: SAME, 2: DIFFERENT})
    background = Counter(value for row in board for value in row).most_common(1)[0][0]
    normal_cells, spacing = _solid_centers(board, background)
    rows = range(
        min(row for row, _ in normal_cells),
        max(row for row, _ in normal_cells) + 1,
        spacing,
    )
    cols = range(
        min(col for _, col in normal_cells),
        max(col for _, col in normal_cells) + 1,
        spacing,
    )
    normal_set = set(normal_cells)
    varied = tuple(
        cell
        for cell in itertools.product(rows, cols)
        if cell not in normal_set
        and int(board[cell[0]][cell[1]]) != background
        and len(set(_sample(board, cell, spacing))) > 1
        and any(
            (
                cell[0] + dr * spacing,
                cell[1] + dc * spacing,
            )
            in normal_set
            for dr, dc in itertools.product((-1, 0, 1), repeat=2)
            if (dr, dc) != (0, 0)
        )
    )
    clue_cells = tuple(
        cell
        for cell in varied
        if set(_sample(board, cell, spacing)) & set(roles)
    )
    obstacle_cells = tuple(cell for cell in varied if cell not in set(clue_cells))
    state_colors = tuple(
        sorted(
            {int(board[row][col]) for row, col in normal_cells}
            | {int(board[row][col]) for row, col in clue_cells}
        )
    )
    if len(state_colors) != 2:
        raise ValueError(f"expected binary level-5 states, found {state_colors}")
    unknown_marks = tuple(
        sorted(
            {
                value
                for cell in clue_cells
                for value in _sample(board, cell, spacing)
            }
            - set(state_colors)
            - {background}
            - set(roles)
        )
    )
    example = LevelExample(
        level=5,
        board=board,
        background=background,
        spacing=spacing,
        normal_cells=normal_cells,
        clue_cells=clue_cells,
        palette=state_colors,
    )
    target_models: dict[
        tuple[tuple[Cell, int], ...], list[tuple[tuple[int, Role], ...]]
    ] = {}
    for assigned in itertools.product((SAME, DIFFERENT), repeat=len(unknown_marks)):
        unknown_model = tuple(zip(unknown_marks, assigned))
        candidate_roles = roles | dict(unknown_model)
        for target in _solve_targets(example, candidate_roles, allow_uncovered=True):
            target_models.setdefault(target, []).append(unknown_model)
    if len(target_models) != 1:
        raise ValueError(
            f"calibrated objective is ambiguous: {len(target_models)} targets"
        )
    target, unknown_models = next(iter(target_models.items()))
    covered: set[Cell] = set()
    for row, col in clue_cells:
        for dr, dc in itertools.product((-1, 0, 1), repeat=2):
            cell = (row + dr * spacing, col + dc * spacing)
            if cell in normal_set:
                covered.add(cell)
    return CalibratedObjective(
        background=background,
        state_colors=state_colors,
        spacing=spacing,
        normal_cells=normal_cells,
        clue_cells=clue_cells,
        obstacle_cells=obstacle_cells,
        learned_roles=tuple(sorted(roles.items())),
        unknown_role_models=tuple(unknown_models),
        uncovered_cells=tuple(sorted(normal_set - covered)),
        target=target,
    )
