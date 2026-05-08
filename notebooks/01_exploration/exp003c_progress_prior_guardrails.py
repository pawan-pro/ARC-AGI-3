# EXP-003C — progress prior guardrails
# Kaggle notebook-source scaffold.
# Start from EXP-003B and change only prior-selection guardrails.

import os
import sys
import subprocess
import json
import random
import zlib
import math
from pathlib import Path
from collections import defaultdict


def ensure_arc_packages() -> None:
    """Install ARC competition packages from Kaggle's local wheel directory when needed.

    This keeps the notebook robust when the pulled source is run as one cell and the
    original pip-install cell has not been executed separately.
    """
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
            "Attach the ARC Prize 2026 / ARC-AGI-3 competition dataset to the notebook, "
            "or run this inside the Kaggle competition notebook environment."
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

EXP_ID = "EXP-003C"
MAX_MOVES = 1000
SEED = 42
USE_PER_GAME_SEED = False

# Controlled change vs EXP-003B:
# EXP-003B used PRIOR_PROB=0.10 and MIN_PRIOR_OBS=8.
# EXP-003C starts with a safer 0.05 prior and stronger evidence requirement.
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12

# New EXP-003C guardrails.
GAME_OVER_PENALTY = 30.0
NOOP_RATE_PENALTY = 0.75
GAME_OVER_RATE_PENALTY = 8.0
MIN_PRIOR_SCORE = 0.02
MAX_CONSECUTIVE_SAME_PRIOR = 2
ACTION6_EXTRA_REPEAT_PENALTY = 0.25

WORK = Path("/kaggle/working")
ART = WORK / "exp003c_artifacts"
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
    """Progress-first utility.

    Main EXP-003C change: GAME_OVER penalty is stronger than EXP-003B.
    Frame change remains a weak signal only.
    """
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


def choose_prior_action(valid_actions, rng, action_stats, last_prior_action, same_prior_count):
    """Choose a cautious prior action or return None to fall back to EXP-001 behavior."""
    candidates = []

    for action in valid_actions:
        stats = action_stats.get(action.name)
        if not stats or stats.get("count", 0) < MIN_PRIOR_OBS:
            continue

        # Cap repeated same-action prior choices.
        if action.name == last_prior_action and same_prior_count >= MAX_CONSECUTIVE_SAME_PRIOR:
            continue

        count = max(1, stats["count"])
        avg_utility = stats["utility"] / count
        noop_rate = stats["noops"] / count
        game_over_rate = stats["game_over"] / count

        score = avg_utility - NOOP_RATE_PENALTY * noop_rate - GAME_OVER_RATE_PENALTY * game_over_rate

        # EXP-003B shifted heavily toward ACTION6. Do not ban ACTION6, but make repeated ACTION6
        # prior selection slightly harder unless utility remains clearly positive.
        if action.name == "ACTION6" and action.name == last_prior_action:
            score -= ACTION6_EXTRA_REPEAT_PENALTY

        if score >= MIN_PRIOR_SCORE:
            candidates.append((score, action))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    top = candidates[:3]

    # Soft top-3 choice: avoids a brittle greedy loop but still favors stronger actions.
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


def play_one_environment(env, game_id: str):
    rng = rng_for(game_id)
    response = env._last_response
    action_counts = defaultdict(int)
    policy_counts = defaultdict(int)
    effect_summary = defaultdict(init_stats)
    action_stats = defaultdict(init_stats)
    effect_tail = []
    base_actions = [action for action in GameAction if action is not GameAction.RESET]

    last_action = None
    last_policy = None
    last_prior_action = None
    same_prior_count = 0

    for move_idx in range(1, MAX_MOVES + 1):
        if response is None or response.state == GameState.WIN:
            break

        if response.state in (GameState.GAME_OVER, GameState.NOT_PLAYED):
            response = env.step(GameAction.RESET, {})
            last_action = "RESET"
            last_policy = "reset"
            last_prior_action = None
            same_prior_count = 0
            action_counts["RESET"] += 1
            policy_counts["reset"] += 1
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
                "prior_prob": PRIOR_PROB,
                "min_prior_obs": MIN_PRIOR_OBS,
                "max_consecutive_same_prior": MAX_CONSECUTIVE_SAME_PRIOR,
            },
        )

        after_frame = get_frame(response)
        diff = diff_summary(before_frame, after_frame)
        after_levels = int(response.levels_completed)
        after_state = response.state.name
        level_delta = after_levels - before_levels
        state_changed = after_state != before_state

        record = {
            "step": move_idx,
            "action": action.name,
            "policy": policy,
            "data": data,
            "frame_changed": diff.get("frame_changed"),
            "diff_pixels": diff.get("diff_pixels"),
            "diff_cx": diff.get("diff_cx"),
            "diff_cy": diff.get("diff_cy"),
            "levels_before": before_levels,
            "levels_after": after_levels,
            "level_delta": level_delta,
            "state_before": before_state,
            "state_after": after_state,
            "state_changed": state_changed,
        }
        record["utility"] = utility_from_effect(record)

        effect_tail.append(record)
        if len(effect_tail) > 100:
            effect_tail = effect_tail[-100:]

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

        last_action = action.name
        last_policy = policy
        action_counts[action.name] += 1
        policy_counts[policy] += 1

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
        "action_counts": dict(action_counts),
        "policy_counts": dict(policy_counts),
        "effect_summary": dict(effect_summary),
        "action_prior": dict(action_stats),
        "effect_tail": effect_tail,
    }


arcade = arc_agi.Arcade()
environments = list(arcade.available_environments)
rows = []
details = []
effect_summary_rows = []
prior_by_game = {}

print(
    EXP_ID,
    "envs=",
    len(environments),
    "MAX_MOVES=",
    MAX_MOVES,
    "SEED=",
    SEED,
    "PRIOR_PROB=",
    PRIOR_PROB,
    "MIN_PRIOR_OBS=",
    MIN_PRIOR_OBS,
)

for idx, info in enumerate(environments, 1):
    result = play_one_environment(arcade.make(info.game_id), info.game_id)
    details.append(result)
    flat = {key: value for key, value in result.items() if key not in ("action_counts", "policy_counts", "effect_summary", "action_prior", "effect_tail")}
    rows.append(flat)
    prior_by_game[result["game_id"]] = result["action_prior"]

    for action, stats in result["effect_summary"].items():
        output = {"game_id": result["game_id"], "action": action}
        output.update(stats)
        effect_summary_rows.append(output)

    print(f"[{idx:03d}/{len(environments):03d}] {flat}")

pd.DataFrame(rows).to_csv(ART / "exp003c_run_results.csv", index=False)
pd.DataFrame(effect_summary_rows).to_csv(ART / "exp003c_effect_summary_by_game.csv", index=False)
(ART / "exp003c_run_details.json").write_text(json.dumps(details, indent=2))
(ART / "exp003c_action_prior_by_game.json").write_text(json.dumps(prior_by_game, indent=2, sort_keys=True))

action_totals = defaultdict(int)
policy_totals = defaultdict(int)
for detail in details:
    for key, value in detail["action_counts"].items():
        action_totals[key] += int(value)
    for key, value in detail["policy_counts"].items():
        policy_totals[key] += int(value)

(ART / "exp003c_action_counts.json").write_text(json.dumps(dict(action_totals), indent=2, sort_keys=True))
(ART / "exp003c_policy_counts.json").write_text(json.dumps(dict(policy_totals), indent=2, sort_keys=True))

summary = {
    "exp_id": EXP_ID,
    "max_moves": MAX_MOVES,
    "seed": SEED,
    "use_per_game_seed": USE_PER_GAME_SEED,
    "prior_prob": PRIOR_PROB,
    "min_prior_obs": MIN_PRIOR_OBS,
    "game_over_penalty": GAME_OVER_PENALTY,
    "max_consecutive_same_prior": MAX_CONSECUTIVE_SAME_PRIOR,
    "change": "EXP-003B refinement with lower prior probability and repeated-prior guardrails",
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
    ).to_csv(ART / "exp003c_scorecard_by_environment.csv", index=False)
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
    ).to_csv(ART / "exp003c_scorecard_by_tag.csv", index=False)
    print(
        "Score:",
        f"{scorecard.score:.4f}",
        "Levels:",
        f"{scorecard.total_levels_completed}/{scorecard.total_levels}",
        "Actions:",
        scorecard.total_actions,
    )

(ART / "exp003c_scorecard_summary.json").write_text(json.dumps(summary, indent=2))

submission_path = WORK / "submission.parquet"
if not submission_path.exists():
    pd.DataFrame(
        [["1_0", "1", True, 1]],
        columns=["row_id", "game_id", "end_of_game", "score"],
    ).to_parquet(submission_path, index=False)

manifest = sorted(str(path) for path in ART.glob("*"))
pd.DataFrame({"artifact": manifest}).to_csv(ART / "artifact_manifest.csv", index=False)

print("submission:", submission_path, submission_path.exists())
print("artifacts:", ART)
print(json.dumps(summary, indent=2))
summary
