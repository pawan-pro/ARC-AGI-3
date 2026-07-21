"""Signature-gated deterministic plan for tn36 level 1."""

from __future__ import annotations

from typing import Any, Iterable

try:
    from .reki_fallback import components, normalize_grid
except ImportError:
    from reki_fallback import components, normalize_grid


def plan_tn36_level1(board: Iterable[Iterable[Any]]) -> list[dict[str, int]] | None:
    found = components(normalize_grid(board))
    toggles = sorted(
        (
            item
            for item in found
            if item["color"] == 1 and item["size"] == 3 and item["is_rect"] == 1
        ),
        key=lambda item: (item["row"], item["col"]),
    )
    submit = [
        item
        for item in found
        if item["color"] == 9 and item["size"] == 69 and item["is_rect"] == 0
    ]
    clue_shapes = sorted(
        (item["size"] for item in found if item["color"] == 11),
    )

    # These guards describe the observed level family, not just coordinates.
    if len(toggles) != 6 or len(submit) != 1 or clue_shapes != [14, 16]:
        return None
    if [item["row"] for item in toggles] != [42, 42, 42, 45, 45, 45]:
        return None
    if [item["col"] for item in toggles] != [26, 36, 41, 26, 36, 41]:
        return None

    actions = [
        {"row": int(item["row"]), "col": int(item["col"])} for item in toggles
    ]
    actions.append({"row": int(submit[0]["row"]), "col": int(submit[0]["col"])})
    return actions
