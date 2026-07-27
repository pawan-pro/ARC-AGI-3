#!/usr/bin/env python3
"""Infer an ft09 objective from pixels without stored colors or coordinates."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import itertools
import math
import re


Cell = tuple[int, int]


@dataclass(frozen=True)
class ObjectiveModel:
    background: int
    palette: tuple[int, ...]
    spacing: int
    normal_cells: tuple[Cell, ...]
    clue_cells: tuple[Cell, ...]
    mask_marks: tuple[int, int]
    center_mark: int
    other_assignments: tuple[int, ...]
    target: tuple[tuple[Cell, int], ...]
    hypothesis_counts: tuple[tuple[int, int], ...]

    def target_dict(self) -> dict[Cell, int]:
        return dict(self.target)

    def to_dict(self) -> dict[str, object]:
        return {
            "background": self.background,
            "palette": list(self.palette),
            "spacing": self.spacing,
            "normal_cells": [list(cell) for cell in self.normal_cells],
            "clue_cells": [list(cell) for cell in self.clue_cells],
            "mask_marks": list(self.mask_marks),
            "center_mark": self.center_mark,
            "other_assignments": list(self.other_assignments),
            "target": [
                {"cell": list(cell), "color": color}
                for cell, color in self.target
            ],
            "hypothesis_counts": [
                {"center_mark": mark, "solutions": count}
                for mark, count in self.hypothesis_counts
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


def _learn_palette(training_events: list[dict]) -> tuple[int, ...]:
    observed: Counter[int] = Counter()
    pattern = re.compile(r"row=(\d+), col=(\d+)")
    for before_event, after_event in zip(training_events, training_events[1:]):
        if before_event.get("level") != after_event.get("level"):
            continue
        match = pattern.search(str(after_event.get("action_display") or ""))
        if not match:
            continue
        row, col = map(int, match.groups())
        before = int(before_event["board"][row][col])
        after = int(after_event["board"][row][col])
        if before != after:
            observed[before] += 1
            observed[after] += 1
    palette = tuple(sorted(observed))
    if len(palette) != 3:
        raise ValueError(f"expected three learned state colors, found {palette}")
    return palette


def _solid_block_centers(
    board: list[list[int]], background: int
) -> tuple[tuple[Cell, ...], int]:
    candidates: list[tuple[int, int, int]] = []
    for color in sorted({value for row in board for value in row} - {background}):
        for component in _components(board, color):
            rows = [cell[0] for cell in component]
            cols = [cell[1] for cell in component]
            height = max(rows) - min(rows) + 1
            width = max(cols) - min(cols) + 1
            if height == width and len(component) == height * width and height >= 4:
                candidates.append((min(rows), min(cols), height))
    size_counts = Counter(size for _, _, size in candidates)
    block_size, count = size_counts.most_common(1)[0]
    if count < 6:
        raise ValueError("no repeated editable-cell geometry found")
    centers = tuple(
        sorted(
            (
                row + (block_size - 2) // 2,
                col + (block_size - 2) // 2,
            )
            for row, col, size in candidates
            if size == block_size
        )
    )
    row_values = sorted({row for row, _ in centers})
    col_values = sorted({col for _, col in centers})
    differences = [
        b - a
        for values in (row_values, col_values)
        for a, b in zip(values, values[1:])
    ]
    spacing = math.gcd(*differences)
    return centers, spacing


def _lattice(values: list[int], spacing: int) -> tuple[int, ...]:
    return tuple(range(min(values), max(values) + 1, spacing))


def infer_objective(
    training_events: list[dict], heldout_board: list[list[int]]
) -> ObjectiveModel:
    background = Counter(value for row in heldout_board for value in row).most_common(1)[0][0]
    palette = _learn_palette(training_events)
    solid_centers, spacing = _solid_block_centers(heldout_board, background)
    rows = _lattice(sorted({row for row, _ in solid_centers}), spacing)
    cols = _lattice(sorted({col for _, col in solid_centers}), spacing)

    micro_step = spacing // 4
    clue_cells: list[Cell] = []
    normal_cells: list[Cell] = []
    for cell in itertools.product(rows, cols):
        row, col = cell
        center = int(heldout_board[row][col])
        if center == background:
            continue
        samples = {
            int(heldout_board[row + dr * micro_step][col + dc * micro_step])
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
        }
        if len(samples) > 1:
            clue_cells.append(cell)
        else:
            normal_cells.append(cell)

    mask_marks = tuple(
        sorted(
            {
                int(heldout_board[row + dr * micro_step][col + dc * micro_step])
                for row, col in clue_cells
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
            }
            - set(palette)
        )
    )
    if len(mask_marks) != 2:
        raise ValueError(f"expected two mask marks, found {mask_marks}")

    normal_set = set(normal_cells)
    solutions_by_mark: dict[int, list[tuple[tuple[int, ...], dict[Cell, int]]]] = {}
    for center_mark in mask_marks:
        solutions: list[tuple[tuple[int, ...], dict[Cell, int]]] = []
        choices = [
            tuple(color for color in palette if color != heldout_board[row][col])
            for row, col in clue_cells
        ]
        for assignment in itertools.product(*choices):
            votes: dict[Cell, list[int]] = {cell: [] for cell in normal_cells}
            for (row, col), other_color in zip(clue_cells, assignment):
                center_color = int(heldout_board[row][col])
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if (dr, dc) == (0, 0):
                            continue
                        target_cell = (row + dr * spacing, col + dc * spacing)
                        if target_cell not in normal_set:
                            continue
                        mark = int(
                            heldout_board[row + dr * micro_step][
                                col + dc * micro_step
                            ]
                        )
                        votes[target_cell].append(
                            center_color if mark == center_mark else other_color
                        )
            if all(values and len(set(values)) == 1 for values in votes.values()):
                solutions.append(
                    (assignment, {cell: values[0] for cell, values in votes.items()})
                )
        solutions_by_mark[center_mark] = solutions

    unique = [
        (mark, solutions[0])
        for mark, solutions in solutions_by_mark.items()
        if len(solutions) == 1
    ]
    if len(unique) != 1:
        counts = {mark: len(values) for mark, values in solutions_by_mark.items()}
        raise ValueError(f"objective is not uniquely identified: {counts}")
    center_mark, (assignment, target) = unique[0]
    return ObjectiveModel(
        background=background,
        palette=palette,
        spacing=spacing,
        normal_cells=tuple(normal_cells),
        clue_cells=tuple(clue_cells),
        mask_marks=mask_marks,
        center_mark=center_mark,
        other_assignments=assignment,
        target=tuple((cell, target[cell]) for cell in normal_cells),
        hypothesis_counts=tuple(
            (mark, len(solutions_by_mark[mark])) for mark in mask_marks
        ),
    )


def choose_next_click(board: list[list[int]], model: ObjectiveModel) -> Cell | None:
    """Choose from the current observation; no future replay action is consulted."""
    for cell, target_color in model.target:
        row, col = cell
        if int(board[row][col]) != target_color:
            return cell
    return None
