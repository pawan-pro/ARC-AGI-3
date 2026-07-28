#!/usr/bin/env python3
"""Infer a unique actionable ft09 level-5 target from its initial pixels."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import itertools
import math


Cell = tuple[int, int]


@dataclass(frozen=True)
class Level5Objective:
    background: int
    state_colors: tuple[int, int]
    spacing: int
    normal_cells: tuple[Cell, ...]
    clue_cells: tuple[Cell, ...]
    mark_colors: tuple[int, ...]
    semantic_models: tuple[tuple[tuple[int, bool], ...], ...]
    target: tuple[tuple[Cell, int], ...]

    def target_dict(self) -> dict[Cell, int]:
        return dict(self.target)

    def clicks(self, board: list[list[int]]) -> tuple[Cell, ...]:
        return tuple(
            cell
            for cell, target_color in self.target
            if int(board[cell[0]][cell[1]]) != target_color
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "background": self.background,
            "state_colors": list(self.state_colors),
            "spacing": self.spacing,
            "normal_cells": [list(cell) for cell in self.normal_cells],
            "clue_cells": [list(cell) for cell in self.clue_cells],
            "mark_colors": list(self.mark_colors),
            "semantic_models": [
                {
                    str(mark): "flip" if flips else "same"
                    for mark, flips in model
                }
                for model in self.semantic_models
            ],
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
    return centers, math.gcd(*differences)


def infer_level5_objective(board: list[list[int]]) -> Level5Objective:
    background = Counter(value for row in board for value in row).most_common(1)[0][0]
    normal_cells, spacing = _solid_centers(board, background)
    rows = tuple(range(min(r for r, _ in normal_cells), max(r for r, _ in normal_cells) + 1, spacing))
    cols = tuple(range(min(c for _, c in normal_cells), max(c for _, c in normal_cells) + 1, spacing))
    micro_step = spacing // 4

    varied: list[tuple[Cell, tuple[int, ...]]] = []
    center_colors = {int(board[row][col]) for row, col in normal_cells}
    for cell in itertools.product(rows, cols):
        row, col = cell
        samples = tuple(
            int(board[row + dr * micro_step][col + dc * micro_step])
            for dr in (-1, 0, 1)
            for dc in (-1, 0, 1)
        )
        if int(board[row][col]) != background and len(set(samples)) > 1:
            varied.append((cell, samples))
            center_colors.add(int(board[row][col]))

    state_colors = tuple(sorted(center_colors - {background}))
    if len(state_colors) != 2:
        raise ValueError(f"expected a binary state palette, found {state_colors}")
    state_set = set(state_colors)
    clue_cells = tuple(
        cell
        for cell, samples in varied
        if any(value not in state_set | {background} for value in samples)
    )
    marks = tuple(
        sorted(
            {
                value
                for cell, samples in varied
                if cell in set(clue_cells)
                for value in samples
            }
            - state_set
            - {background}
        )
    )
    normal_set = set(normal_cells)
    semantic_models: list[tuple[tuple[int, bool], ...]] = []
    targets: dict[tuple[tuple[Cell, int], ...], list[tuple[tuple[int, bool], ...]]] = {}
    for flags in itertools.product((False, True), repeat=len(marks)):
        semantics = tuple(zip(marks, flags))
        flip_by_mark = dict(semantics)
        votes: dict[Cell, list[int]] = {cell: [] for cell in normal_cells}
        for row, col in clue_cells:
            center = int(board[row][col])
            other = next(iter(state_set - {center}))
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (dr, dc) == (0, 0):
                        continue
                    target_cell = (row + dr * spacing, col + dc * spacing)
                    if target_cell not in normal_set:
                        continue
                    mark = int(
                        board[row + dr * micro_step][col + dc * micro_step]
                    )
                    if mark in state_set:
                        target_color = mark
                    elif mark in flip_by_mark:
                        target_color = other if flip_by_mark[mark] else center
                    else:
                        continue
                    votes[target_cell].append(target_color)
        if not all(values and len(set(values)) == 1 for values in votes.values()):
            continue
        target = tuple((cell, votes[cell][0]) for cell in normal_cells)
        semantic_models.append(semantics)
        targets.setdefault(target, []).append(semantics)

    if len(targets) != 1:
        raise ValueError(
            f"actionable objective is ambiguous: {len(targets)} target signatures"
        )
    target, equivalent_models = next(iter(targets.items()))
    return Level5Objective(
        background=background,
        state_colors=(state_colors[0], state_colors[1]),
        spacing=spacing,
        normal_cells=normal_cells,
        clue_cells=clue_cells,
        mark_colors=marks,
        semantic_models=tuple(equivalent_models),
        target=target,
    )
