# EXP-004 — Long-Horizon Discovery
# Standalone Kaggle-safe research/data-generation scaffold.
# Goal: discover which buttons/actions and recent action windows lead to level progress.
# Do not submit directly unless intentionally using as a high-budget public probe.

import os
import sys
import subprocess
import json
import random
import zlib
import math
from pathlib import Path
from collections import Counter, defaultdict, deque


def ensure_arc_packages() -> None:
    """Install ARC competition packages from Kaggle's local wheel directory when needed."""
    try:
        import arc_agi  # noqa: F401
        import arcengine  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    wheel_dir = Path("/kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels")
    if not wheel_dir.exists():
        raise ModuleNotFoundError(
            "arc_agi is not installed and the Kaggle wheel directory was not found. "
            "Attach the ARC Prize 2026 / ARC-AGI-3 competition dataset to the notebook."
        )

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-q",
        "--no-index",
        "--find-links",
        str(wheel_dir),
        "arc-agi",
        "python-dotenv",
        "pyarrow",
    ]
    print("Installing ARC packages from local wheels:", " ".join(cmd))
    subprocess.check_call(cmd)


ensure_arc_packages()

import numpy as np
import pandas as pd
import dotenv
import arc_agi
from arcengine import GameAction, GameState


# -----------------------------
# Experiment config
# -----------------------------
EXP_ID = "EXP-004"
MAX_MOVES = 10_000
SEED = 42
USE_PER_GAME_SEED = False

# Keep EXP-003C-style sparse progress prior. No ACTION6 throttle.
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
GAME_OVER_PENALTY = 30.0
NOOP_RATE_PENALTY = 0.75
GAME_OVER_RATE_PENALTY = 8.0
MIN_PRIOR_SCORE = 0.02
MAX_CONSECUTIVE_SAME_PRIOR = 2
ACTION6_EXTRA_REPEAT_PENALTY = 0.25

WINDOW_SIZES = [10, 25, 50, 100]
EVENT_TAIL_KEEP = 250

WORK = Path("/kaggle/working")
ART = WORK / "exp004_artifacts"
ART.mkdir(exist_ok=True)

if os.getenv("KAGGLE_IS_COMPETITION_RERUN"):
    get_ipython().system(
        "curl --fail --retry 999 --retry-all-errors --retry-delay 5 --retry-max-time 600 http://gateway:8001/api/games"
    )
    mode = "online"
    envdir = ""
else:
    mode = "offline"
    envdir = "/kaggle/input/competitions/arc-prize-2026-arc-agi-3/environment_files/"

(WORK / ".env").write_text(
    f"""SCHEME=http
HOST=gateway
PORT=8001
ARC_API_KEY=test-key-123
ARC_BASE_URL=http://gateway:8001/
OPERATION_MODE={mode}
ENVIRONMENTS_DIR={envdir}
RECORDINGS_DIR=/kaggle/working/server_recording
"""
)
dotenv.load_dotenv(WORK / ".env", override=True)


# -----------------------------
# Helpers
# -----------------------------
def rng_for(game_id: str) -> random.Random:
    if not USE_PER_GAME_SEED:
        return random.Random(SEED)
    return random.Random(SEED + (zlib.adler32(game_id.encode()) & 0xFFFFFFFF))


def get_frame(obs):
    if obs is None or not getattr(obs, "frame", None):
        return None
    return np.asarray(obs.frame[-1])


def diff_summary(before, after):
    if before is None or after is None or before.shape != after.shape:
        return {"frame_changed": None, "diff_pixels": None, "diff_cx": None, "diff_cy": None}
    diff = before != after
    ys, xs = np.where(diff)
    if len(xs) == 0:
        return {"frame_changed": False, "diff_pixels": 0, "diff_cx": None, "diff_cy": None}
    return {
        "frame_changed": True,
        "diff_pixels": int(len(xs)),
        "diff_cx": float(xs.mean()),
        "diff_cy": float(ys.mean()),
    }


def random_visible_pixel(frame, rng: random.Random):
    color = rng.choice(np.unique(frame).tolist())
    ys, xs = np.where(frame == color)
    idx = rng.randint(0, len(xs) - 1)
    return {"x": int(xs[idx]), "y": int(ys[idx])}


def init_stats():
    return {
        "count": 0,
        "frame_changed": 0,
        "noops": 0,
        "level_delta": 0,
        "game_over": 0,
        "state_changed": 0,
        "diff_pixels": 0,
        "utility": 0.0,
    }


def utility_from_effect(effect):
    utility = 0.0
    level_delta = effect.get("level_delta")
    if level_delta and level_delta > 0:
        utility += 50.0 * level_delta
    if effect.get("state_after") == "WIN":
        utility += 50.0
    if effect.get("state_after") == "GAME_OVER":
        utility -= GAME_OVER_PENALTY
    elif effect.get("state_changed"):
        utility += 1.0
    if effect.get("frame_changed") is True:
        utility += min(0.5, math.log1p(effect.get("diff_pixels") or 0) / 20.0)
    elif effect.get("frame_changed") is False:
        utility -= 0.35
    return float(utility)


def sequence_string(records, key="action"):
    return ">".join(str(item.get(key)) for item in records)


def counter_json(counter: Counter):
    return json.dumps(dict(counter), sort_keys=True)


def recent_rates(records):
    if not records:
        return {"noop_rate": None, "game_over_rate": None, "progress_rate": None}
    n = len(records)
    noops = sum(1 for item in records if item.get("frame_changed") is False)
    game_over = sum(1 for item in records if item.get("state_after") == "GAME_OVER")
    progress = sum(1 for item in records if (item.get("level_delta") or 0) > 0)
    return {
        "noop_rate": noops / n,
        "game_over_rate": game_over / n,
        "progress_rate": progress / n,
    }


def choose_prior_action(valid_actions, rng, action_stats, last_prior_action, same_prior_count):
    """Sparse EXP-003C-style online progress prior."""
    candidates = []
    for action in valid_actions:
        stats = action_stats.get(action.name)
        if not stats or stats.get("count", 0) < MIN_PRIOR_OBS:
            continue
        if action.name == last_prior_action and same_prior_count >= MAX_CONSECUTIVE_SAME_PRIOR:
            continue

        count = max(1, stats["count"])
        avg_utility = stats["utility"] / count
        noop_rate = stats["noops"] / count
        game_over_rate = stats["game_over"] / count
        score = avg_utility - NOOP_RATE_PENALTY * noop_rate - GAME_OVER_RATE_PENALTY * game_over_rate
        if action.name == "ACTION6" and action.name == last_prior_action:
            score -= ACTION6_EXTRA_REPEAT_PENALTY
        if score >= MIN_PRIOR_SCORE:
            candidates.append((score, action))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    top = candidates[:3]
    floor = top[-1][0]
    weights = [max(0.01, score - floor + 0.05) for score, _ in top]
    total = sum(weights)
    draw = rng.random() * total
    acc = 0.0
    for weight, (_, action) in zip(weights, top):
        acc += weight
        if draw <= acc:
            return action
    return top[0][1]


def summarize_progress_event(
    *,
    game_id,
    record,
    recent_history,
    action_counts,
    policy_counts,
    policy_action_counts,
    resets_seen,
    last_progress_step,
):
    """Create a flat row and rich JSON window for a level_delta event."""
    windows = {}
    row = {
        "game_id": game_id,
        "step": int(record["step"]),
        "level_before": int(record["levels_before"]),
        "level_after": int(record["levels_after"]),
        "level_delta": int(record["level_delta"]),
        "progress_action": record["action"],
        "progress_policy": record["policy"],
        "action_data": json.dumps(record.get("data", {}), sort_keys=True),
        "state_before": record["state_before"],
        "state_after": record["state_after"],
        "frame_changed": record.get("frame_changed"),
        "diff_pixels": record.get("diff_pixels"),
        "diff_cx": record.get("diff_cx"),
        "diff_cy": record.get("diff_cy"),
        "utility": record.get("utility"),
        "resets_before_progress": int(resets_seen),
        "actions_since_previous_progress": None if last_progress_step is None else int(record["step"] - last_progress_step),
        "action_counts_before_progress": json.dumps(dict(action_counts), sort_keys=True),
        "policy_counts_before_progress": json.dumps(dict(policy_counts), sort_keys=True),
        "policy_action_counts_before_progress": json.dumps(dict(policy_action_counts), sort_keys=True),
    }

    for size in WINDOW_SIZES:
        window = list(recent_history)[-size:]
        actions = [item.get("action") for item in window]
        policies = [item.get("policy") for item in window]
        action_counter = Counter(actions)
        policy_counter = Counter(policies)
        rates = recent_rates(window)
        windows[str(size)] = {
            "size": size,
            "actions": actions,
            "policies": policies,
            "records": window,
            "action_counts": dict(action_counter),
            "policy_counts": dict(policy_counter),
            "noop_rate": rates["noop_rate"],
            "game_over_rate": rates["game_over_rate"],
            "progress_rate": rates["progress_rate"],
        }
        row[f"last_{size}_actions"] = ">".join(actions)
        row[f"last_{size}_policies"] = ">".join(policies)
        row[f"last_{size}_action_counts"] = json.dumps(dict(action_counter), sort_keys=True)
        row[f"last_{size}_policy_counts"] = json.dumps(dict(policy_counter), sort_keys=True)
        row[f"recent_{size}_noop_rate"] = rates["noop_rate"]
        row[f"recent_{size}_game_over_rate"] = rates["game_over_rate"]
        row[f"recent_{size}_progress_rate"] = rates["progress_rate"]

    rich = {
        "game_id": game_id,
        "event": row,
        "windows": windows,
    }
    return row, rich


# -----------------------------
# Main play loop
# -----------------------------
def play_one_environment(env, game_id: str):
    rng = rng_for(game_id)
    response = env._last_response

    action_counts = defaultdict(int)
    policy_counts = defaultdict(int)
    policy_action_counts = defaultdict(int)
    effect_summary = defaultdict(init_stats)
    action_stats = defaultdict(init_stats)

    effect_tail = []
    recent_history = deque(maxlen=max(WINDOW_SIZES))
    progress_rows = []
    progress_windows = []

    base_actions = [action for action in GameAction if action is not GameAction.RESET]
    last_action = None
    last_policy = None
    last_prior_action = None
    same_prior_count = 0
    resets_seen = 0
    last_progress_step = None

    for move_idx in range(1, MAX_MOVES + 1):
        if response is None or response.state == GameState.WIN:
            break

        if response.state in (GameState.GAME_OVER, GameState.NOT_PLAYED):
            response = env.step(GameAction.RESET, {})
            last_action = "RESET"
            last_policy = "reset"
            last_prior_action = None
            same_prior_count = 0
            resets_seen += 1
            action_counts["RESET"] += 1
            policy_counts["reset"] += 1
            policy_action_counts["reset|RESET"] += 1
            continue

        frame = get_frame(response)
        before_frame = frame.copy() if frame is not None else None
        before_levels = int(response.levels_completed)
        before_state = response.state.name

        valid_actions = list(getattr(env, "action_space", [])) or base_actions
        valid_actions = [action for action in valid_actions if action is not GameAction.RESET]
        if not valid_actions:
            valid_actions = base_actions

        use_prior = rng.random() < PRIOR_PROB
        action = choose_prior_action(valid_actions, rng, action_stats, last_prior_action, same_prior_count) if use_prior else None

        if action is None:
            action = rng.choice(valid_actions)
            policy = "exp001_random_visible_pixel_fallback"
        else:
            policy = "progress_prior_guardrailed"

        data = random_visible_pixel(frame, rng) if action.is_complex() and frame is not None else {}
        response = env.step(
            action,
            data,
            reasoning={
                "exp_id": EXP_ID,
                "policy": policy,
                "purpose": "long_horizon_progress_window_discovery",
                "prior_prob": PRIOR_PROB,
                "min_prior_obs": MIN_PRIOR_OBS,
            },
        )

        after_frame = get_frame(response)
        diff = diff_summary(before_frame, after_frame)
        after_levels = int(response.levels_completed)
        after_state = response.state.name
        level_delta = after_levels - before_levels
        state_changed = after_state != before_state

        record = {
            "step": int(move_idx),
            "action": action.name,
            "policy": policy,
            "data": data,
            "frame_changed": diff.get("frame_changed"),
            "diff_pixels": diff.get("diff_pixels"),
            "diff_cx": diff.get("diff_cx"),
            "diff_cy": diff.get("diff_cy"),
            "levels_before": int(before_levels),
            "levels_after": int(after_levels),
            "level_delta": int(level_delta),
            "state_before": before_state,
            "state_after": after_state,
            "state_changed": bool(state_changed),
        }
        record["utility"] = utility_from_effect(record)

        # Update counts before progress-window export so the progress action is included.
        action_counts[action.name] += 1
        policy_counts[policy] += 1
        policy_action_counts[f"{policy}|{action.name}"] += 1

        for table in (effect_summary, action_stats):
            stats = table[action.name]
            stats["count"] += 1
            if record["frame_changed"] is True:
                stats["frame_changed"] += 1
            if record["frame_changed"] is False:
                stats["noops"] += 1
            if level_delta > 0:
                stats["level_delta"] += int(level_delta)
            if after_state == "GAME_OVER":
                stats["game_over"] += 1
            if state_changed:
                stats["state_changed"] += 1
            stats["diff_pixels"] += int(record.get("diff_pixels") or 0)
            stats["utility"] += float(record["utility"])

        recent_history.append(record)
        effect_tail.append(record)
        if len(effect_tail) > EVENT_TAIL_KEEP:
            effect_tail = effect_tail[-EVENT_TAIL_KEEP:]

        if level_delta > 0:
            progress_row, progress_window = summarize_progress_event(
                game_id=game_id,
                record=record,
                recent_history=recent_history,
                action_counts=action_counts,
                policy_counts=policy_counts,
                policy_action_counts=policy_action_counts,
                resets_seen=resets_seen,
                last_progress_step=last_progress_step,
            )
            progress_rows.append(progress_row)
            progress_windows.append(progress_window)
            last_progress_step = move_idx
            print(
                "PROGRESS_EVENT",
                json.dumps(
                    {
                        "game_id": game_id,
                        "step": move_idx,
                        "level_before": before_levels,
                        "level_after": after_levels,
                        "action": action.name,
                        "last_10": progress_row.get("last_10_actions"),
                    },
                    sort_keys=True,
                ),
            )

        last_action = action.name
        last_policy = policy
        if policy == "progress_prior_guardrailed":
            if action.name == last_prior_action:
                same_prior_count += 1
            else:
                last_prior_action = action.name
                same_prior_count = 1
        else:
            same_prior_count = 0

    return {
        "game_id": game_id,
        "moves": int(move_idx),
        "state": response.state.name if response else "unknown",
        "levels_completed": int(response.levels_completed) if response else 0,
        "last_action": last_action,
        "last_policy": last_policy,
        "resets_seen": int(resets_seen),
        "progress_events": int(len(progress_rows)),
        "action_counts": dict(action_counts),
        "policy_counts": dict(policy_counts),
        "policy_action_counts": dict(policy_action_counts),
        "effect_summary": dict(effect_summary),
        "action_prior": dict(action_stats),
        "effect_tail": effect_tail,
        "progress_rows": progress_rows,
        "progress_windows": progress_windows,
    }


# -----------------------------
# Run environments
# -----------------------------
arcade = arc_agi.Arcade()
environments = list(arcade.available_environments)

rows = []
details = []
effect_summary_rows = []
policy_action_rows = []
action_diag_rows = []
progress_event_rows = []
progress_windows_all = []
prior_by_game = {}

print(
    EXP_ID,
    "envs=", len(environments),
    "MAX_MOVES=", MAX_MOVES,
    "SEED=", SEED,
    "PRIOR_PROB=", PRIOR_PROB,
    "MIN_PRIOR_OBS=", MIN_PRIOR_OBS,
)

for idx, info in enumerate(environments, 1):
    result = play_one_environment(arcade.make(info.game_id), info.game_id)
    details.append(result)

    flat = {
        key: value
        for key, value in result.items()
        if key not in (
            "action_counts",
            "policy_counts",
            "policy_action_counts",
            "effect_summary",
            "action_prior",
            "effect_tail",
            "progress_rows",
            "progress_windows",
        )
    }
    rows.append(flat)
    prior_by_game[result["game_id"]] = result["action_prior"]
    progress_event_rows.extend(result["progress_rows"])
    progress_windows_all.extend(result["progress_windows"])

    for key, count in result["policy_action_counts"].items():
        policy, action = key.split("|", 1)
        policy_action_rows.append({"game_id": result["game_id"], "policy": policy, "action": action, "count": int(count)})

    for action, stats in result["effect_summary"].items():
        out = {"game_id": result["game_id"], "action": action}
        out.update(stats)
        effect_summary_rows.append(out)
        count = max(1, stats.get("count", 0))
        action_diag_rows.append(
            {
                "game_id": result["game_id"],
                "action": action,
                "count": int(stats.get("count", 0)),
                "noop_rate": float(stats.get("noops", 0) / count),
                "game_over_rate": float(stats.get("game_over", 0) / count),
                "level_delta": int(stats.get("level_delta", 0)),
                "utility_per_action": float(stats.get("utility", 0.0) / count),
                "utility": float(stats.get("utility", 0.0)),
            }
        )

    print(f"[{idx:03d}/{len(environments):03d}] {flat}")

# -----------------------------
# Persist artifacts
# -----------------------------
pd.DataFrame(rows).to_csv(ART / "exp004_run_results.csv", index=False)
pd.DataFrame(effect_summary_rows).to_csv(ART / "exp004_effect_summary_by_game.csv", index=False)
pd.DataFrame(policy_action_rows).to_csv(ART / "exp004_policy_action_by_game.csv", index=False)
pd.DataFrame(action_diag_rows).to_csv(ART / "exp004_action_diagnostics_by_game.csv", index=False)
pd.DataFrame(progress_event_rows).to_csv(ART / "exp004_progress_events.csv", index=False)

(ART / "exp004_run_details.json").write_text(json.dumps(details, indent=2))
(ART / "exp004_action_prior_by_game.json").write_text(json.dumps(prior_by_game, indent=2, sort_keys=True))
(ART / "exp004_progress_windows.json").write_text(json.dumps(progress_windows_all, indent=2, sort_keys=True))

action_totals = defaultdict(int)
policy_totals = defaultdict(int)
policy_action_totals = defaultdict(int)
for detail in details:
    for key, value in detail["action_counts"].items():
        action_totals[key] += int(value)
    for key, value in detail["policy_counts"].items():
        policy_totals[key] += int(value)
    for key, value in detail["policy_action_counts"].items():
        policy_action_totals[key] += int(value)

(ART / "exp004_action_counts.json").write_text(json.dumps(dict(action_totals), indent=2, sort_keys=True))
(ART / "exp004_policy_counts.json").write_text(json.dumps(dict(policy_totals), indent=2, sort_keys=True))
(ART / "exp004_policy_action_counts.json").write_text(json.dumps(dict(policy_action_totals), indent=2, sort_keys=True))

# Progress-window aggregate summaries.
progress_summary_rows = []
progress_window_action_rows = []
if progress_event_rows:
    progress_df = pd.DataFrame(progress_event_rows)
    progress_summary = (
        progress_df.groupby(["game_id", "progress_action", "progress_policy"], as_index=False)
        .agg(
            events=("level_delta", "count"),
            total_level_delta=("level_delta", "sum"),
            first_step=("step", "min"),
            median_step=("step", "median"),
            last_step=("step", "max"),
        )
        .sort_values(["total_level_delta", "events", "game_id"], ascending=[False, False, True])
    )
    progress_summary.to_csv(ART / "exp004_progress_action_summary.csv", index=False)

    for event in progress_windows_all:
        game_id = event["game_id"]
        step = event["event"]["step"]
        progress_action = event["event"]["progress_action"]
        for size, window in event["windows"].items():
            for action, count in window["action_counts"].items():
                progress_window_action_rows.append(
                    {
                        "game_id": game_id,
                        "step": step,
                        "progress_action": progress_action,
                        "window_size": int(size),
                        "window_action": action,
                        "window_action_count": int(count),
                    }
                )
    pd.DataFrame(progress_window_action_rows).to_csv(ART / "exp004_progress_action_window_counts.csv", index=False)
else:
    pd.DataFrame(columns=["game_id", "progress_action", "progress_policy", "events", "total_level_delta", "first_step", "median_step", "last_step"]).to_csv(ART / "exp004_progress_action_summary.csv", index=False)
    pd.DataFrame(columns=["game_id", "step", "progress_action", "window_size", "window_action", "window_action_count"]).to_csv(ART / "exp004_progress_action_window_counts.csv", index=False)

summary = {
    "exp_id": EXP_ID,
    "max_moves": MAX_MOVES,
    "seed": SEED,
    "use_per_game_seed": USE_PER_GAME_SEED,
    "prior_prob": PRIOR_PROB,
    "min_prior_obs": MIN_PRIOR_OBS,
    "game_over_penalty": GAME_OVER_PENALTY,
    "max_consecutive_same_prior": MAX_CONSECUTIVE_SAME_PRIOR,
    "progress_events": int(len(progress_event_rows)),
    "change": "Long-horizon discovery run with progress-window logging; no ACTION6 throttle",
}

if not os.getenv("KAGGLE_IS_COMPETITION_RERUN"):
    scorecard = arcade.get_scorecard()
    summary.update(
        score=float(scorecard.score),
        total_environments_completed=int(scorecard.total_environments_completed),
        total_environments=int(scorecard.total_environments),
        total_levels_completed=int(scorecard.total_levels_completed),
        total_levels=int(scorecard.total_levels),
        total_actions=int(scorecard.total_actions),
    )
    pd.DataFrame(
        [
            {
                "game": env.id,
                "score": float(env.score),
                "levels_completed": int(env.levels_completed),
                "actions": int(env.actions),
                "completed": bool(env.completed),
            }
            for env in scorecard.environments
        ]
    ).to_csv(ART / "exp004_scorecard_by_environment.csv", index=False)
    pd.DataFrame(
        [
            {
                "tag": tag.id,
                "score": float(tag.score),
                "levels_completed": int(tag.levels_completed),
                "number_of_environments": int(tag.number_of_environments),
            }
            for tag in (scorecard.tags_scores or [])
        ]
    ).to_csv(ART / "exp004_scorecard_by_tag.csv", index=False)
    print(
        "Score:",
        f"{scorecard.score:.4f}",
        "Levels:",
        f"{scorecard.total_levels_completed}/{scorecard.total_levels}",
        "Actions:",
        scorecard.total_actions,
    )

(ART / "exp004_scorecard_summary.json").write_text(json.dumps(summary, indent=2))

submission_path = WORK / "submission.parquet"
if not submission_path.exists():
    pd.DataFrame([["1_0", "1", True, 1]], columns=["row_id", "game_id", "end_of_game", "score"]).to_parquet(submission_path, index=False)

manifest = sorted(str(path) for path in ART.glob("*"))
pd.DataFrame({"artifact": manifest}).to_csv(ART / "artifact_manifest.csv", index=False)

print("submission:", submission_path, submission_path.exists())
print("artifacts:", ART)
print("progress_events:", len(progress_event_rows))
print("action_counts:", json.dumps(dict(action_totals), indent=2, sort_keys=True))
print("policy_counts:", json.dumps(dict(policy_totals), indent=2, sort_keys=True))
print("policy_action_counts:", json.dumps(dict(policy_action_totals), indent=2, sort_keys=True))
print(json.dumps(summary, indent=2))
summary
