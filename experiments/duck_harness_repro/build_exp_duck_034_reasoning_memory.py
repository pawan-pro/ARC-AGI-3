#!/usr/bin/env python3
"""Build the EXP-DUCK-034 rule memory from validated EXP-DUCK-033 evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bounded_reasoning_loop import build_exp033_memory


ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / "experiments/duck_harness_repro/exp_duck_033_validation.json"
EVENTS = (
    ROOT
    / "artifacts/kaggle/duck_ft09_level5_probe_top/latest/artifacts"
    / "ft09-0d8bbf25_p0_events.jsonl"
)
OUTPUT = ROOT / "experiments/duck_harness_repro/exp_duck_034_mechanics_memory.json"


def main() -> int:
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in EVENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    untouched = events[69]["board"]
    memory = build_exp033_memory(validation, untouched)
    memory.save(OUTPUT)
    print(OUTPUT)
    print(
        "validated memory: "
        f"{len(memory.rules)} forward-only rules; no bidirectional claim"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
