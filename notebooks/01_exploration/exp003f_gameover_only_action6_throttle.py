# EXP-003F — GAME_OVER-only ACTION6 throttle
# Standalone Kaggle-safe scaffold.
# Based on EXP-003E diagnostics, but disables no-op-based ACTION6 throttling.
# Do not submit before artifact analysis.

import os
import sys
import subprocess
import json
import random
import zlib
import math
from pathlib import Path
from collections import defaultdict, deque


def ensure_arc_packages() -> None:
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
        sys.executable, "-m", "pip", "install", "-q", "--no-index",
        "--find-links", str(wheel_dir), "arc-agi", "python-dotenv", "pyarrow"
    ]
    print("Installing ARC packages from local wheels:", " ".join(cmd))
    subprocess.check_call(cmd)


ensure_arc_packages()

import numpy as np
import pandas as pd
import dotenv
import arc_agi
from arcengine import GameAction, GameState


EXP_ID = "EXP-003F"
MAX_MOVES = 1000
SEED = 42
USE_PER_GAME_SEED = False

# Keep EXP-003C/E prior guardrails.
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
GAME_OVER_PENALTY = 30.0
NOOP_RATE_PENALTY = 0.75
GAME_OVER_RATE_PENALTY = 8.0
MIN_PRIOR_SCORE = 0.02
MAX_CONSECUTIVE_SAME_PRIOR = 2
ACTION6_EXTRA_REPEAT_PENALTY = 0.25

# EXP-003F controlled change:
# no no-op-based ACTION6 throttle; only GAME_OVER rate can trigger throttle.
ACTION6_MIN_OBS_FOR_THROTTLE = 30
ACTION6_BAD_GAME_OVER_RATE = 0.04
ACTION6_RECENT_WINDOW = 40
ACTION6_RECENT_LEVEL_DELTA_PROTECT = 1
ACTION6_THROTTLE_KEEP_PROB = 0.50

WORK = Path("/kaggle/working")
ART = WORK / "exp003f_artifacts"
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


def should_throttle_action6(action_stats, recent_action6_effects):
    """GAME_OVER-only ACTION6 throttle.

    No-op rate is intentionally ignored in EXP-003F because EXP-003D/E showed
    no-op throttling can suppress useful ACTION6 exploration.
    """
    stats = action_stats.get("ACTION6")
    if not stats or stats.get("count", 0) < ACTION6_MIN_OBS_FOR_THROTTLE:
        return False, "not_enough_obs"

    current_positive = stats.get("level_delta", 0) > 0
    recent_positive = sum(1 for rec in recent_action6_effects if rec.get("level_delta", 0) > 0)
    if current_positive or recent_positive >= ACTION6_RECENT_LEVEL_DELTA_PROTECT:
        return False, "level_delta_protect"

    count = max(1, stats["count"])
    game_over_rate = stats["game_over"] / count

    if game_over_rate >= ACTION6_BAD_GAME_OVER_RATE:
        return True, "bad_game_over_rate"
    return False, "below_game_over_threshold"


def choose_fallback_action(valid_actions, rng, action_stats, recent_action6_effects, throttle_events):
    action = rng.choice(valid_actions)
    if action.name != "ACTION6":
        return action, "none"

    throttle, reason = should_throttle_action6(action_stats, recent_action6_effects)
    if not throttle:
        return action, reason

    if rng.random() < ACTION6_THROTTLE_KEEP_PROB:
        throttle_events["action6_throttled_but_kept"] += 1
        return action, f"kept_after_{reason}"

    alternatives = [candidate for candidate in valid_actions if candidate.name != "ACTION6"]
    if not alternatives:
        return action, "no_alternative"

    replacement = rng.choice(alternatives)
    throttle_events["action6_throttled_replaced"] += 1
    throttle_events[f"action6_throttle_reason__{reason}"] += 1
    throttle_events[f"action6_replaced_with__{replacement.name}"] += 1
    return replacement, reason


def play_one_environment(env, game_id: str):
    rng = rng_for(game_id)
    response = env._last_response
    action_counts = defaultdict(int)
    policy_counts = defaultdict(int)
    policy_action_counts = defaultdict(int)
    effect_summary = defaultdict(init_stats)
    action_stats = defaultdict(init_stats)
    effect_tail = []
    recent_action6_effects = deque(maxlen=ACTION6_RECENT_WINDOW)
    throttle_events = defaultdict(int)
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

        throttle_reason = "not_applicable"
        if action is None:
            action, throttle_reason = choose_fallback_action(
                valid_actions, rng, action_stats, recent_action6_effects, throttle_events
            )
            policy = "exp001_random_visible_pixel_fallback_action6_gameover_throttle"
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
                "action6_throttle_reason": throttle_reason,
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
            "action6_throttle_reason": throttle_reason,
        }
        record["utility"] = utility_from_effect(record)

        effect_tail.append(record)
        if len(effect_tail) > 100:
            effect_tail = effect_tail[-100:]
        if action.name == "ACTION6":
            recent_action6_effects.append(record)

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
        policy_action_counts[f"{policy}|{action.name}"] += 1

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
        "policy_action_counts": dict(policy_action_counts),
        "effect_summary": dict(effect_summary),
        "action_prior": dict(action_stats),
        "effect_tail": effect_tail,
        "action6_throttle": dict(throttle_events),
    }


arcade = arc_agi.Arcade()
environments = list(arcade.available_environments)
rows, details, effect_summary_rows, policy_action_rows, action_diag_rows, action6_throttle_rows = [], [], [], [], [], []
prior_by_game = {}

print(
    EXP_ID,
    "envs=", len(environments),
    "MAX_MOVES=", MAX_MOVES,
    "SEED=", SEED,
    "PRIOR_PROB=", PRIOR_PROB,
    "MIN_PRIOR_OBS=", MIN_PRIOR_OBS,
    "ACTION6_BAD_GAME_OVER_RATE=", ACTION6_BAD_GAME_OVER_RATE,
    "ACTION6_THROTTLE_KEEP_PROB=", ACTION6_THROTTLE_KEEP_PROB,
)

for idx, info in enumerate(environments, 1):
    result = play_one_environment(arcade.make(info.game_id), info.game_id)
    details.append(result)
    flat = {
        key: value
        for key, value in result.items()
        if key not in ("action_counts", "policy_counts", "policy_action_counts", "effect_summary", "action_prior", "effect_tail", "action6_throttle")
    }
    rows.append(flat)
    prior_by_game[result["game_id"]] = result["action_prior"]

    for key, count in result["policy_action_counts"].items():
        policy, action = key.split("|", 1)
        policy_action_rows.append({"game_id": result["game_id"], "policy": policy, "action": action, "count": int(count)})

    throttle_row = {"game_id": result["game_id"]}
    throttle_row.update(result["action6_throttle"])
    action6_throttle_rows.append(throttle_row)

    for action, stats in result["effect_summary"].items():
        out = {"game_id": result["game_id"], "action": action}
        out.update(stats)
        effect_summary_rows.append(out)
        count = max(1, stats.get("count", 0))
        action_diag_rows.append({
            "game_id": result["game_id"],
            "action": action,
            "count": int(stats.get("count", 0)),
            "noop_rate": float(stats.get("noops", 0) / count),
            "game_over_rate": float(stats.get("game_over", 0) / count),
            "level_delta": int(stats.get("level_delta", 0)),
            "utility_per_action": float(stats.get("utility", 0.0) / count),
            "utility": float(stats.get("utility", 0.0)),
        })

    print(f"[{idx:03d}/{len(environments):03d}] {flat}")

pd.DataFrame(rows).to_csv(ART / "exp003f_run_results.csv", index=False)
pd.DataFrame(effect_summary_rows).to_csv(ART / "exp003f_effect_summary_by_game.csv", index=False)
pd.DataFrame(policy_action_rows).to_csv(ART / "exp003f_policy_action_by_game.csv", index=False)
pd.DataFrame(action_diag_rows).to_csv(ART / "exp003f_action_diagnostics_by_game.csv", index=False)
pd.DataFrame(action6_throttle_rows).fillna(0).to_csv(ART / "exp003f_action6_throttle_by_game.csv", index=False)
(ART / "exp003f_run_details.json").write_text(json.dumps(details, indent=2))
(ART / "exp003f_action_prior_by_game.json").write_text(json.dumps(prior_by_game, indent=2, sort_keys=True))

action_totals, policy_totals, policy_action_totals, throttle_totals = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
for detail in details:
    for key, value in detail["action_counts"].items():
        action_totals[key] += int(value)
    for key, value in detail["policy_counts"].items():
        policy_totals[key] += int(value)
    for key, value in detail["policy_action_counts"].items():
        policy_action_totals[key] += int(value)
    for key, value in detail["action6_throttle"].items():
        throttle_totals[key] += int(value)

(ART / "exp003f_action_counts.json").write_text(json.dumps(dict(action_totals), indent=2, sort_keys=True))
(ART / "exp003f_policy_counts.json").write_text(json.dumps(dict(policy_totals), indent=2, sort_keys=True))
(ART / "exp003f_policy_action_counts.json").write_text(json.dumps(dict(policy_action_totals), indent=2, sort_keys=True))
(ART / "exp003f_action6_throttle_counts.json").write_text(json.dumps(dict(throttle_totals), indent=2, sort_keys=True))

summary = {
    "exp_id": EXP_ID,
    "max_moves": MAX_MOVES,
    "seed": SEED,
    "use_per_game_seed": USE_PER_GAME_SEED,
    "prior_prob": PRIOR_PROB,
    "min_prior_obs": MIN_PRIOR_OBS,
    "game_over_penalty": GAME_OVER_PENALTY,
    "max_consecutive_same_prior": MAX_CONSECUTIVE_SAME_PRIOR,
    "action6_min_obs_for_throttle": ACTION6_MIN_OBS_FOR_THROTTLE,
    "action6_bad_game_over_rate": ACTION6_BAD_GAME_OVER_RATE,
    "action6_throttle_keep_prob": ACTION6_THROTTLE_KEEP_PROB,
    "change": "EXP-003F GAME_OVER-only ACTION6 throttle; no no-op throttle",
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
    pd.DataFrame([
        {
            "game": env.id,
            "score": float(env.score),
            "levels_completed": int(env.levels_completed),
            "actions": int(env.actions),
            "completed": bool(env.completed),
        }
        for env in scorecard.environments
    ]).to_csv(ART / "exp003f_scorecard_by_environment.csv", index=False)
    pd.DataFrame([
        {
            "tag": tag.id,
            "score": float(tag.score),
            "levels_completed": int(tag.levels_completed),
            "number_of_environments": int(tag.number_of_environments),
        }
        for tag in (scorecard.tags_scores or [])
    ]).to_csv(ART / "exp003f_scorecard_by_tag.csv", index=False)
    print("Score:", f"{scorecard.score:.4f}", "Levels:", f"{scorecard.total_levels_completed}/{scorecard.total_levels}", "Actions:", scorecard.total_actions)

(ART / "exp003f_scorecard_summary.json").write_text(json.dumps(summary, indent=2))

submission_path = WORK / "submission.parquet"
if not submission_path.exists():
    pd.DataFrame([["1_0", "1", True, 1]], columns=["row_id", "game_id", "end_of_game", "score"]).to_parquet(submission_path, index=False)

manifest = sorted(str(path) for path in ART.glob("*"))
pd.DataFrame({"artifact": manifest}).to_csv(ART / "artifact_manifest.csv", index=False)

print("submission:", submission_path, submission_path.exists())
print("artifacts:", ART)
print("action_counts:", json.dumps(dict(action_totals), indent=2, sort_keys=True))
print("policy_counts:", json.dumps(dict(policy_totals), indent=2, sort_keys=True))
print("policy_action_counts:", json.dumps(dict(policy_action_totals), indent=2, sort_keys=True))
print("action6_throttle_counts:", json.dumps(dict(throttle_totals), indent=2, sort_keys=True))
print(json.dumps(summary, indent=2))
summary
