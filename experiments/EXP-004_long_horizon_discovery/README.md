# EXP-004 — Long-horizon discovery

## Purpose

EXP-004 is a research/data-generation experiment. It runs a much longer local horizon so we can discover which actions, action windows, and button patterns lead to actual `level_delta > 0` events.

This is not a normal leaderboard submission candidate.

K-12 version: let the robot play for a long time, and every time it finally makes progress, write down exactly what it did right before the progress. Then use those notes to build a smarter, shorter policy later.

## Motivation

EXP-003F_5000 showed that longer stochastic exploration can find more levels:

```text
EXP-003F_1000 score: 0.481950521305291 | levels: 7 / 183 | actions: 25,000
EXP-003F_5000 score: 0.5105754965839018 | levels: 9 / 183 | actions: 125,000
```

The improvement came from longer exploration, not from the ACTION6 throttle, because throttle counts were empty. EXP-004 therefore focuses on discovery, not another throttle.

## Experiment setup

Notebook/source:

```text
notebooks/01_exploration/exp004_long_horizon_discovery.py
```

Default settings:

```text
EXP_ID = EXP-004
MAX_MOVES = 10000
SEED = 42
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
Base behavior = EXP-003C-style fallback + sparse progress prior
No ACTION6 throttle
Do not submit directly
```

## Key instrumentation

For every `level_delta > 0`, EXP-004 records:

```text
game_id
step
level_before
level_after
level_delta
action
policy
action data / click coordinate
state_before
state_after
frame_changed
diff_pixels
resets before progress
actions since previous progress
action counts before progress
policy counts before progress
recent no-op rate
recent GAME_OVER rate
last 10 actions
last 25 actions
last 50 actions
last 100 actions
```

## Required artifacts

```text
artifact_manifest.csv
exp004_scorecard_summary.json
exp004_scorecard_by_environment.csv
exp004_scorecard_by_tag.csv
exp004_run_results.csv
exp004_run_details.json
exp004_action_counts.json
exp004_policy_counts.json
exp004_policy_action_counts.json
exp004_effect_summary_by_game.csv
exp004_action_diagnostics_by_game.csv
exp004_action_prior_by_game.json
exp004_progress_events.csv
exp004_progress_windows.json
exp004_progress_action_window_counts.csv
```

## What to analyze after run

1. Which games produce progress after 5k/10k actions.
2. Which actions are at the progress step.
3. Which actions appear most often in the last 10/25/50/100 actions before progress.
4. Whether progress is single-action or sequence/precondition based.
5. Whether ACTION6 is causal or just frequent.
6. Whether resets help or hurt discovery.
7. Which progress patterns can be compressed into a 25k-action policy.

## Validation / submission gate

Do not submit EXP-004 directly unless deliberately using it as a public high-budget probe.

The intended follow-up is:

```text
EXP-004B_progress_replay_prior
```

Possible policy idea:

```text
Use long-run progress windows to bias actions for a short budget, then fall back to stochastic exploration.
```

## Success criterion

Success is not only a higher long-horizon score. Success is a clean, analyzable progress-window dataset that can produce a shorter, more efficient policy.
