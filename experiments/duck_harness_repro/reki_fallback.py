"""Fallback-only Reki-style salient click selection for Duck experiments.

The ledger may learn from every observed click, but it never rejects an LLM
action. Its dead signatures and exact-state failures are consulted only when a
separate stall policy explicitly asks for a fallback click.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Any, Iterable


Grid = tuple[tuple[int, ...], ...]
Signature = tuple[int, int, int, int]


def normalize_grid(board: Iterable[Iterable[Any]]) -> Grid:
    return tuple(tuple(int(cell) for cell in row) for row in board)


def dominant_color(grid: Grid) -> int:
    counts = Counter(cell for row in grid for cell in row)
    return counts.most_common(1)[0][0] if counts else 0


def comparison_grid(grid: Grid, border: int = 3) -> Grid:
    if border <= 0 or len(grid) <= border * 2:
        return grid
    trimmed = []
    for row in grid[border:-border]:
        trimmed.append(row[border:-border] if len(row) > border * 2 else row)
    return tuple(trimmed)


def changed_cells(before: Grid, after: Grid, border: int = 3) -> int:
    left = comparison_grid(before, border)
    right = comparison_grid(after, border)
    height = max(len(left), len(right))
    width = max(
        max((len(row) for row in left), default=0),
        max((len(row) for row in right), default=0),
    )
    changed = 0
    for row in range(height):
        left_row = left[row] if row < len(left) else ()
        right_row = right[row] if row < len(right) else ()
        for col in range(width):
            left_value = left_row[col] if col < len(left_row) else 0
            right_value = right_row[col] if col < len(right_row) else 0
            changed += left_value != right_value
    return changed


def components(grid: Grid) -> list[dict[str, Any]]:
    """Return non-background 4-connected components with Reki signatures."""
    if not grid:
        return []
    background = dominant_color(grid)
    height = len(grid)
    seen: set[tuple[int, int]] = set()
    result: list[dict[str, Any]] = []

    for start_row, values in enumerate(grid):
        for start_col, color in enumerate(values):
            if color == background or (start_row, start_col) in seen:
                continue
            queue = deque([(start_row, start_col)])
            seen.add((start_row, start_col))
            pixels: list[tuple[int, int]] = []
            while queue:
                row, col = queue.popleft()
                pixels.append((row, col))
                for next_row, next_col in (
                    (row - 1, col),
                    (row + 1, col),
                    (row, col - 1),
                    (row, col + 1),
                ):
                    if (next_row, next_col) in seen:
                        continue
                    if next_row < 0 or next_row >= height:
                        continue
                    if next_col < 0 or next_col >= len(grid[next_row]):
                        continue
                    if grid[next_row][next_col] != color:
                        continue
                    seen.add((next_row, next_col))
                    queue.append((next_row, next_col))

            rows = [position[0] for position in pixels]
            cols = [position[1] for position in pixels]
            center_row = sum(rows) / len(rows)
            center_col = sum(cols) / len(cols)
            click_row, click_col = min(
                pixels,
                key=lambda position: abs(position[0] - center_row)
                + abs(position[1] - center_col),
            )
            bbox_area = (max(rows) - min(rows) + 1) * (max(cols) - min(cols) + 1)
            result.append(
                {
                    "color": color,
                    "size": len(pixels),
                    "is_rect": int(len(pixels) == bbox_area),
                    "row": click_row,
                    "col": click_col,
                    "pixels": frozenset(pixels),
                }
            )

    twin_counts = Counter(
        (item["color"], item["size"], item["is_rect"]) for item in result
    )
    total_cells = sum(len(row) for row in grid)
    color_counts = Counter(cell for row in grid for cell in row)
    for item in result:
        base = (item["color"], item["size"], item["is_rect"])
        item["signature"] = (*base, twin_counts[base] - 1)
        rarity = 1.0 - color_counts[item["color"]] / max(total_cells, 1)
        size = item["size"]
        size_score = (
            1.0
            if size <= 4
            else 0.8
            if size <= 16
            else 0.5
            if size <= 64
            else 0.25
            if size <= 256
            else 0.0
        )
        item["saliency"] = 0.5 * rarity + 0.5 * size_score
    return result


def signature_at(grid: Grid, row: int, col: int) -> Signature | None:
    if row < 0 or row >= len(grid) or col < 0 or col >= len(grid[row]):
        return None
    if grid[row][col] == dominant_color(grid):
        return None
    for item in components(grid):
        if (row, col) in item["pixels"]:
            return item["signature"]
    return None


class FallbackClickLedger:
    def __init__(self, dead_threshold: int = 2, border_ignore: int = 3) -> None:
        self.dead_threshold = max(1, int(dead_threshold))
        self.border_ignore = max(0, int(border_ignore))
        self.level: int | None = None
        self.dead_signatures: set[Signature] = set()
        self.effective_signatures: set[Signature] = set()
        self.dead_counts: defaultdict[Signature, int] = defaultdict(int)
        self.failed_state_clicks: defaultdict[Grid, set[tuple[int, int]]] = defaultdict(set)
        self.fallback_attempts = 0
        self.total_fallback_attempts = 0
        self.fallback_exhausted = False
        self.observed_clicks = 0
        self.fallback_effective = 0
        self.fallback_no_effect = 0

    def ensure_level(self, level: int) -> None:
        level = int(level)
        if self.level == level:
            return
        self.level = level
        self.dead_signatures.clear()
        self.effective_signatures.clear()
        self.dead_counts.clear()
        self.failed_state_clicks.clear()
        self.fallback_attempts = 0
        self.fallback_exhausted = False

    def choose(self, board: Iterable[Iterable[Any]], level: int) -> dict[str, Any] | None:
        self.ensure_level(level)
        grid = normalize_grid(board)
        failed = self.failed_state_clicks.get(grid, set())
        ranked = sorted(
            components(grid),
            key=lambda item: (item["saliency"], -item["size"]),
            reverse=True,
        )
        for item in ranked:
            coordinate = (item["row"], item["col"])
            if item["signature"] in self.dead_signatures or coordinate in failed:
                continue
            self.fallback_attempts += 1
            self.total_fallback_attempts += 1
            return {
                "row": item["row"],
                "col": item["col"],
                "signature": item["signature"],
                "saliency": item["saliency"],
            }
        self.fallback_exhausted = True
        return None

    def observe(
        self,
        before: Iterable[Iterable[Any]],
        after: Iterable[Iterable[Any]],
        level_before: int,
        level_after: int,
        row: int,
        col: int,
        *,
        fallback: bool = False,
    ) -> dict[str, Any]:
        self.ensure_level(level_before)
        before_grid = normalize_grid(before)
        after_grid = normalize_grid(after)
        signature = signature_at(before_grid, int(row), int(col))
        changed = changed_cells(before_grid, after_grid, self.border_ignore)
        progressed = int(level_after) != int(level_before)
        effective = bool(changed or progressed)
        self.observed_clicks += 1
        if fallback:
            if effective:
                self.fallback_effective += 1
            else:
                self.fallback_no_effect += 1

        if signature is not None:
            if effective:
                self.effective_signatures.add(signature)
                self.dead_counts.pop(signature, None)
                self.dead_signatures.discard(signature)
            elif signature not in self.effective_signatures:
                self.failed_state_clicks[before_grid].add((int(row), int(col)))
                self.dead_counts[signature] += 1
                if self.dead_counts[signature] >= self.dead_threshold:
                    self.dead_signatures.add(signature)

        if progressed:
            self.ensure_level(level_after)
        return {
            "signature": signature,
            "changed_cells": changed,
            "level_progress": progressed,
            "effective": effective,
            "dead_after": signature in self.dead_signatures if signature else False,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "fallback_attempts": self.fallback_attempts,
            "total_fallback_attempts": self.total_fallback_attempts,
            "fallback_exhausted": self.fallback_exhausted,
            "observed_clicks": self.observed_clicks,
            "fallback_effective": self.fallback_effective,
            "fallback_no_effect": self.fallback_no_effect,
            "dead_signatures": len(self.dead_signatures),
            "effective_signatures": len(self.effective_signatures),
        }
