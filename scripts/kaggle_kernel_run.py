#!/usr/bin/env python3
"""Push, monitor, download, and summarize the Duck Kaggle notebook run.

This is intentionally a thin wrapper around the Kaggle CLI so runs are easy to
start from a terminal and the resulting artifacts land in predictable folders.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "notebooks/04_submission_builds/duck_public_repro_terminal_run"
VARIANTS = {
    "baseline": {
        "metadata": PACKAGE_DIR / "kernel-metadata.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_public_repro_terminal_run/latest",
    },
    "stall": {
        "metadata": PACKAGE_DIR / "kernel-metadata-stall-policy.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_controlled_stall_policy/latest",
    },
    "ft09-helper": {
        "metadata": PACKAGE_DIR / "kernel-metadata-ft09-helper.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_ft09_helper/latest",
    },
    "ft09-mask-cycle": {
        "metadata": PACKAGE_DIR / "kernel-metadata-ft09-mask-cycle.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_ft09_mask_cycle/latest",
    },
    "ft09-level4-isolated": {
        "metadata": PACKAGE_DIR / "kernel-metadata-ft09-level4-isolated.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_ft09_level4_isolated/latest",
    },
    "ft09-level4-exhaustive": {
        "metadata": PACKAGE_DIR / "kernel-metadata-ft09-level4-exhaustive.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_ft09_level4_exhaustive/latest",
    },
    "ft09-level4-overlap": {
        "metadata": PACKAGE_DIR / "kernel-metadata-ft09-level4-overlap.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_ft09_level4_overlap/latest",
    },
    "full-eval-overlap": {
        "metadata": PACKAGE_DIR / "kernel-metadata-full-eval-overlap.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_full_eval_ft09_overlap/latest",
    },
    "reki-fallback": {
        "metadata": PACKAGE_DIR / "kernel-metadata-reki-fallback.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_reki_fallback/latest",
    },
    "batch-feedback": {
        "metadata": PACKAGE_DIR / "kernel-metadata-batch-feedback.json",
        "artifact_dir": REPO_ROOT / "artifacts/kaggle/duck_batch_feedback/latest",
    },
}


def variant_config(args: argparse.Namespace) -> dict:
    return VARIANTS[str(getattr(args, "variant", "baseline"))]


def load_metadata(args: argparse.Namespace) -> dict:
    return json.loads(variant_config(args)["metadata"].read_text(encoding="utf-8"))


def kernel_id(args: argparse.Namespace) -> str:
    return str(load_metadata(args)["id"])


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, check=check)


def capture(cmd: list[str], *, check: bool = True) -> str:
    print("+", " ".join(cmd), flush=True)
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )
    print(result.stdout, end="")
    return result.stdout


def cmd_info(args: argparse.Namespace) -> None:
    metadata = load_metadata(args)
    print("Kaggle package:")
    print(f"  variant:     {args.variant}")
    print(f"  package_dir: {PACKAGE_DIR}")
    print(f"  kernel_id:   {metadata['id']}")
    print(f"  title:       {metadata['title']}")
    print(f"  code_file:   {metadata['code_file']}")
    print(f"  gpu:         {metadata.get('enable_gpu')}")
    print(f"  internet:    {metadata.get('enable_internet')}")
    print("Inputs:")
    for ref in metadata.get("competition_sources", []):
        print(f"  competition: {ref}")
    for ref in metadata.get("dataset_sources", []):
        print(f"  dataset:     {ref}")


def cmd_push(args: argparse.Namespace) -> None:
    config = variant_config(args)
    active_metadata = PACKAGE_DIR / "kernel-metadata.json"
    requested_metadata = config["metadata"]
    original_text = active_metadata.read_text(encoding="utf-8")
    requested_text = requested_metadata.read_text(encoding="utf-8")
    try:
        if requested_metadata != active_metadata:
            active_metadata.write_text(requested_text, encoding="utf-8")
        run(["kaggle", "kernels", "push", "-p", str(PACKAGE_DIR)])
    finally:
        active_metadata.write_text(original_text, encoding="utf-8")


def cmd_status(args: argparse.Namespace) -> None:
    run(["kaggle", "kernels", "status", kernel_id(args)])


def cmd_logs(args: argparse.Namespace) -> None:
    cmd = ["kaggle", "kernels", "logs", kernel_id(args)]
    if args.follow:
        cmd.extend(["--follow", "--interval", str(args.interval)])
    run(cmd)


def cmd_watch(args: argparse.Namespace) -> None:
    terminal_states = {
        "complete",
        "error",
        "cancel",
        "cancelled",
        "canceled",
        "cancel_acknowledged",
        "failed",
    }
    while True:
        output = capture(["kaggle", "kernels", "status", kernel_id(args)], check=False)
        lower = output.lower()
        if any(state in lower for state in terminal_states):
            break
        time.sleep(args.interval)


def cmd_output(args: argparse.Namespace) -> None:
    artifact_dir = variant_config(args)["artifact_dir"]
    artifact_dir.mkdir(parents=True, exist_ok=True)
    run(["kaggle", "kernels", "output", kernel_id(args), "-p", str(artifact_dir), "--force"])
    print(f"Downloaded latest output to {artifact_dir}")


def cmd_summarize(args: argparse.Namespace) -> None:
    artifact_dir = variant_config(args)["artifact_dir"]
    benchmark_path = Path(args.benchmark) if args.benchmark else artifact_dir / "benchmark.json"
    if not benchmark_path.exists():
        raise SystemExit(f"Missing benchmark.json: {benchmark_path}")

    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    runs = benchmark.get("game_runs", [])
    rows = []
    for game_run in runs:
        game_id = str(game_run.get("game_id") or "")
        history = game_run.get("history") or []
        actions = sum(game_run.get("actions_per_level") or [])
        note = game_run.get("solver_note") or ""
        note_tokens = None
        if "tokens=" in note:
            try:
                note_tokens = int(note.rsplit("=", 1)[-1])
            except ValueError:
                note_tokens = None
        tokens = note_tokens or sum(step.get("generated_tokens") or 0 for step in history)
        action_counts = Counter((step.get("action") or {}).get("id") for step in history)
        zero_token_actions = sum(1 for step in history if (step.get("generated_tokens") or 0) == 0)
        fallback_events = []
        events_path = artifact_dir / "artifacts" / f"{game_id}_p0_events.jsonl"
        if events_path.exists():
            for line in events_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                event = json.loads(line)
                if event.get("fallback_policy") == "reki_saliency_deadsig":
                    fallback_events.append(event)
        rows.append(
            {
                "game_id": game_id,
                "score": float(game_run.get("final_score") or 0),
                "levels": int(game_run.get("levels_completed") or 0),
                "total_levels": int(game_run.get("number_of_levels") or 0),
                "actions": actions,
                "tokens": tokens,
                "zero_token_actions": zero_token_actions,
                "fallback_actions": len(fallback_events),
                "fallback_effective": sum(
                    bool((event.get("reki_fallback_observation") or {}).get("effective"))
                    for event in fallback_events
                ),
                "fallback_progress": sum(
                    bool((event.get("reki_fallback_observation") or {}).get("level_progress"))
                    for event in fallback_events
                ),
                "top_actions": action_counts.most_common(3),
            }
        )

    print(f"label: {benchmark.get('label')}")
    print(f"games: {len(rows)}")
    print(f"score_sum: {sum(row['score'] for row in rows):.4f}")
    print(f"levels: {sum(row['levels'] for row in rows)} / {sum(row['total_levels'] for row in rows)}")
    print(f"actions: {sum(row['actions'] for row in rows)}")
    print(f"tokens: {sum(row['tokens'] for row in rows)}")
    print(f"zero_token_actions: {sum(row['zero_token_actions'] for row in rows)}")
    print(
        "reki_fallback: "
        f"actions={sum(row['fallback_actions'] for row in rows)} "
        f"effective={sum(row['fallback_effective'] for row in rows)} "
        f"level_progress={sum(row['fallback_progress'] for row in rows)}"
    )

    print("\nTop progress games:")
    for row in sorted(rows, key=lambda item: (item["score"], item["levels"]), reverse=True)[:12]:
        print(
            f"{row['game_id']:13} score={row['score']:6.2f} "
            f"levels={row['levels']}/{row['total_levels']} "
            f"actions={row['actions']:4} tokens={row['tokens']:6} "
            f"zero={row['zero_token_actions']:4} fallback={row['fallback_actions']:3}/"
            f"{row['fallback_effective']:3}/{row['fallback_progress']:2} top={row['top_actions']}"
        )

    print("\nZero-level high-spend games:")
    zero_rows = [row for row in rows if row["levels"] == 0]
    for row in sorted(zero_rows, key=lambda item: (item["tokens"], item["actions"]), reverse=True)[:12]:
        print(
            f"{row['game_id']:13} score={row['score']:6.2f} "
            f"levels={row['levels']}/{row['total_levels']} "
            f"actions={row['actions']:4} tokens={row['tokens']:6} "
            f"zero={row['zero_token_actions']:4} fallback={row['fallback_actions']:3}/"
            f"{row['fallback_effective']:3}/{row['fallback_progress']:2} top={row['top_actions']}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--variant",
        choices=sorted(VARIANTS),
        default="baseline",
        help="Kaggle kernel package variant to operate on.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("info", help="Show package metadata").set_defaults(func=cmd_info)
    subparsers.add_parser("push", help="Push package to Kaggle and start a run").set_defaults(func=cmd_push)
    subparsers.add_parser("status", help="Show latest Kaggle kernel status").set_defaults(func=cmd_status)

    logs_parser = subparsers.add_parser("logs", help="Print latest Kaggle kernel logs")
    logs_parser.add_argument("--follow", action="store_true", help="Follow logs")
    logs_parser.add_argument("--interval", type=int, default=30, help="Follow polling interval in seconds")
    logs_parser.set_defaults(func=cmd_logs)

    watch_parser = subparsers.add_parser("watch", help="Poll status until a terminal state")
    watch_parser.add_argument("--interval", type=int, default=120, help="Polling interval in seconds")
    watch_parser.set_defaults(func=cmd_watch)

    subparsers.add_parser("output", help="Download latest Kaggle kernel output").set_defaults(func=cmd_output)

    summarize_parser = subparsers.add_parser("summarize", help="Summarize benchmark.json")
    summarize_parser.add_argument("--benchmark", help="Optional path to benchmark.json")
    summarize_parser.set_defaults(func=cmd_summarize)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
