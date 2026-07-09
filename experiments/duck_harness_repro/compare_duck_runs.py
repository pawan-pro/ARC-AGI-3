"""Compare Duck benchmark JSON files for a small set of games.

Usage:
    python experiments/duck_harness_repro/compare_duck_runs.py \
        artifacts/kaggle/duck_public_repro_terminal_run/latest/benchmark.json \
        artifacts/kaggle/duck_controlled_stall_policy/latest/benchmark.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_GAMES = (
    "ft09-0d8bbf25",
    "tn36-ef4dde99",
    "sc25-635fd71a",
    "tr87-cd924810",
)


def load_runs(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text())
    return {run["game_id"]: run for run in data["game_runs"]}


def metrics(run: dict[str, Any]) -> dict[str, Any]:
    history = run.get("history", [])
    return {
        "levels": int(run.get("levels_completed", 0)),
        "total_levels": int(run.get("number_of_levels", 0)),
        "score": float(run.get("final_score", 0.0)),
        "actions": len(history),
        "tokens": sum(int(step.get("generated_tokens", 0)) for step in history),
        "zero_token_actions": sum(1 for step in history if int(step.get("generated_tokens", 0)) == 0),
        "actions_per_level": run.get("actions_per_level", []),
        "solver_note": run.get("solver_note", ""),
    }


def fmt_int(value: int) -> str:
    return f"{value:,}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--games", nargs="*", default=list(DEFAULT_GAMES))
    args = parser.parse_args()

    baseline = load_runs(args.baseline)
    candidate = load_runs(args.candidate)

    print("| game | baseline | candidate | action delta | token delta | level delta | note |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for game_id in args.games:
        if game_id not in baseline or game_id not in candidate:
            print(f"| `{game_id}` | missing | missing |  |  |  | not present in both files |")
            continue
        b = metrics(baseline[game_id])
        c = metrics(candidate[game_id])
        action_delta = c["actions"] - b["actions"]
        token_delta = c["tokens"] - b["tokens"]
        level_delta = c["levels"] - b["levels"]
        baseline_cell = (
            f"{b['levels']}/{b['total_levels']}, "
            f"{fmt_int(b['actions'])} actions, {fmt_int(b['tokens'])} tokens"
        )
        candidate_cell = (
            f"{c['levels']}/{c['total_levels']}, "
            f"{fmt_int(c['actions'])} actions, {fmt_int(c['tokens'])} tokens"
        )
        print(
            f"| `{game_id}` | {baseline_cell} | {candidate_cell} | "
            f"{action_delta:+,} | {token_delta:+,} | {level_delta:+,} | "
            f"{c['solver_note']} |"
        )


if __name__ == "__main__":
    main()
