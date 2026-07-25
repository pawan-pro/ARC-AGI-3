"""Signature-gated deterministic movement routes for tu93 levels 1 and 2."""

from __future__ import annotations

import zlib
from typing import Any, Iterable


LEVEL_START_CRC32 = {
    1: 0xF888B0BD,
    2: 0x984223A4,
}

LEVEL_ROUTES = {
    1: (
        "ACTION4",  # right
        "ACTION2",  # down
        "ACTION2",
        "ACTION4",
        "ACTION1",  # up
        "ACTION4",
        "ACTION2",
        "ACTION2",
        "ACTION3",  # left
        "ACTION3",
        "ACTION2",
        "ACTION4",
        "ACTION4",
        "ACTION2",
        "ACTION4",
        "ACTION1",
        "ACTION4",
        "ACTION2",
    ),
    2: (
        "ACTION1",
        "ACTION4",
        "ACTION4",
        "ACTION2",
        "ACTION4",
        "ACTION4",
        "ACTION1",
        "ACTION4",
        "ACTION4",
        "ACTION1",
    ),
}


def board_crc32(board: Iterable[Iterable[Any]]) -> int | None:
    rows = [list(row) for row in board]
    if len(rows) != 64 or any(len(row) != 64 for row in rows):
        return None
    try:
        payload = bytes(int(value) for row in rows for value in row)
    except (TypeError, ValueError, OverflowError):
        return None
    return zlib.crc32(payload) & 0xFFFFFFFF


def plan_tu93_route(
    board: Iterable[Iterable[Any]], level: int
) -> tuple[str, ...] | None:
    expected = LEVEL_START_CRC32.get(int(level))
    route = LEVEL_ROUTES.get(int(level))
    if expected is None or route is None or board_crc32(board) != expected:
        return None
    return route
