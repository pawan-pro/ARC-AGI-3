#!/usr/bin/env python3
"""Build the two isolated EXP-DUCK-036 bottom-right pair notebooks."""

from __future__ import annotations

from build_ft09_feedback_order_notebooks import (
    MIDDLE,
    TOP,
    build,
)


BOTTOM_RIGHT = "ft09-level5-magenta-bottom_right"
ARMS = (
    ("top-bottom-right", (TOP, BOTTOM_RIGHT)),
    ("middle-bottom-right", (MIDDLE, BOTTOM_RIGHT)),
)


def main() -> int:
    for arm, order in ARMS:
        output, metadata = build(
            arm,
            order,
            experiment_id="EXP-DUCK-036",
            feedback_active_rules=order,
            date_slug="20260731",
            purpose=(
                "two-action test of whether the corner marks any active "
                "control pair"
            ),
        )
        print(output)
        print(metadata)
    print("validated: two private bottom-right pair arms; neither launched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
