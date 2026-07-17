#!/usr/bin/env python3
"""Derive an overlap-consistent ft09 level-4 clue mapping.

White positions inherit a clue's center color. Gray must mean a different
palette color. Overlapping clue neighborhoods constrain those gray meanings;
the script accepts a target only when the assignment is unique and conflict
free.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

try:
    from .ft09_level4_truth_table import (
        BLUE,
        CYCLE,
        GRAY,
        NORMAL_CELLS,
        NORMAL_SET,
        SPECIAL_CELLS,
        WHITE,
        center_string,
        color,
        cycle_distance,
        mask_values,
        reconstruct,
    )
except ImportError:
    from ft09_level4_truth_table import (
        BLUE,
        CYCLE,
        GRAY,
        NORMAL_CELLS,
        NORMAL_SET,
        SPECIAL_CELLS,
        WHITE,
        center_string,
        color,
        cycle_distance,
        mask_values,
        reconstruct,
    )


def load_level4_board(events_path: Path) -> list[list[int]]:
    for line in events_path.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if (
            event.get("type") == "action"
            and int(event.get("level") or 0) == 4
            and bool(event.get("level_completed"))
        ):
            return event["board"]
    raise ValueError(f"no ft09 level-4 start board found in {events_path}")


def direct_mapping(board: list[list[int]]) -> dict[str, object]:
    centers = {special: int(board[special[0]][special[1]]) for special in SPECIAL_CELLS}
    gray_choices = {
        special: [candidate for candidate in CYCLE if candidate != center]
        for special, center in centers.items()
    }

    def build_constraints(
        gray_assignment: dict[tuple[int, int], int],
    ) -> dict[tuple[int, int], list[dict[str, object]]]:
        constraints: dict[tuple[int, int], list[dict[str, object]]] = {
            cell: [] for cell in NORMAL_CELLS
        }
        for special in SPECIAL_CELLS:
            center_color = centers[special]
            for offset, mark in mask_values(board, special).items():
                if offset == (0, 0):
                    continue
                dr, dc = offset
                target_cell = (special[0] + dr * 8, special[1] + dc * 8)
                if target_cell not in NORMAL_SET:
                    continue
                if mark == WHITE:
                    target_color = center_color
                    rule = "white->center"
                elif mark == GRAY:
                    target_color = gray_assignment[special]
                    rule = "gray->overlap-consistent non-center"
                else:
                    raise ValueError(
                        f"unexpected mask color {mark} at {special} offset {offset}"
                    )
                constraints[target_cell].append(
                    {
                        "special": list(special),
                        "offset": list(offset),
                        "mark": color(mark),
                        "target": color(target_color),
                        "rule": rule,
                    }
                )
        return constraints

    solutions = []
    for selected in itertools.product(*(gray_choices[special] for special in SPECIAL_CELLS)):
        assignment = dict(zip(SPECIAL_CELLS, selected))
        candidate_constraints = build_constraints(assignment)
        if all(
            len({str(vote["target"]) for vote in votes}) <= 1
            for votes in candidate_constraints.values()
        ):
            solutions.append((assignment, candidate_constraints))

    if len(solutions) != 1:
        return {
            "rule": "white->center; gray->non-center constrained by overlaps",
            "solution_count": len(solutions),
            "gray_assignments": [
                {str(list(cell)): color(value) for cell, value in assignment.items()}
                for assignment, _ in solutions
            ],
            "conflicts": [],
            "uncovered": [],
            "direct_target": None,
            "planned_actions": 0,
            "clicks": [],
            "macro_target": [],
            "constraints": [],
        }

    gray_assignment, constraints = solutions[0]

    conflicts = []
    uncovered = []
    target: dict[tuple[int, int], int] = {}
    for cell in NORMAL_CELLS:
        votes = constraints[cell]
        if not votes:
            uncovered.append(list(cell))
            continue
        colors = {str(vote["target"]) for vote in votes}
        if len(colors) != 1:
            conflicts.append({"cell": list(cell), "votes": votes})
            continue
        target[cell] = next(
            value for value in CYCLE if color(value) == next(iter(colors))
        )

    current = {cell: int(board[cell[0]][cell[1]]) for cell in NORMAL_CELLS}
    clicks = []
    if not conflicts and not uncovered:
        for cell in NORMAL_CELLS:
            clicks.extend([list(cell)] * cycle_distance(current[cell], target[cell]))

    macro_rows = []
    for row in (16, 24, 32, 40, 48):
        macro_row = []
        for col in (14, 22, 30, 38, 46):
            cell = (row, col)
            if cell in SPECIAL_CELLS:
                macro_row.append(f"clue:{color(board[row][col])}")
            elif cell in NORMAL_SET:
                macro_row.append(color(target[cell]) if cell in target else "?")
            else:
                macro_row.append(".")
        macro_rows.append(macro_row)

    return {
        "rule": "white->center; gray->unique non-center color forced by overlaps",
        "solution_count": len(solutions),
        "gray_assignment": {
            str(list(cell)): color(value) for cell, value in gray_assignment.items()
        },
        "conflicts": conflicts,
        "uncovered": uncovered,
        "direct_target": center_string(target) if len(target) == len(NORMAL_CELLS) else None,
        "planned_actions": len(clicks),
        "clicks": clicks,
        "macro_target": macro_rows,
        "constraints": [
            {"cell": list(cell), "votes": votes}
            for cell, votes in constraints.items()
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--events",
        type=Path,
        default=Path(
            "artifacts/kaggle/duck_ft09_level4_exhaustive/latest/artifacts/"
            "ft09-0d8bbf25_p0_events.jsonl"
        ),
    )
    args = parser.parse_args()

    board = load_level4_board(args.events)
    result = direct_mapping(board)
    trace = reconstruct(args.events)
    direct_target = result["direct_target"]
    result["attempted_candidate_mismatches"] = [
        {
            "candidate_index": row["candidate_index"],
            "candidate": row["candidate"],
            "mismatched_centers": sum(
                actual != expected
                for actual, expected in zip(str(row["target"]), str(direct_target))
            ),
            "mismatched_cells": [
                list(cell)
                for cell, actual, expected in zip(
                    NORMAL_CELLS, str(row["target"]), str(direct_target)
                )
                if actual != expected
            ],
        }
        for row in trace["rows"]
    ]
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
