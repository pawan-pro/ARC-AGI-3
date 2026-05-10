# EXP-004 — Long-Horizon Discovery

## Purpose

EXP-004 is a research/data-generation run designed to discover which buttons/actions and short action sequences actually lead to level progress.

This is **not** a normal leaderboard submission candidate. It is meant to generate evidence for a later compressed policy.

## K-12 summary

Let the robot play for a long time. Every time it moves up a level, pause and write down what buttons it pressed right before that success. Later, teach the robot to try the useful button patterns earlier instead of wandering randomly.

## Background

Current confirmed public baseline:

```text
EXP-003B public score: 0.12
EXP-003B local score: 0.48491096178440257
EXP-003B local levels: 6 / 183
```

Recent long-horizon local evidence:

```text
EXP-003F_1000 score: 0.481950521305291 | levels: 7 / 183 | actions: 25,000
EXP-003F_5000 score: 0.5105754965839018 | levels: 9 / 183 | actions: 125,000
```

The 5000-move result improved local raw score, but it used 5x the standard action budget and the ACTION6 throttle never fired. The gain came from longer exploration, not better policy logic.

## Hypothesis

Long-horizon play can reveal reusable progress windows:

```text
which game + which level + which action + which recent action sequence -> level_delta
```

If we can identify those progress windows, we can later create a shorter, more efficient replay-prior policy.

## Notebook-source target

```text
notebooks/01_exploration/exp004_long_horizon_discovery.py
```

## Default local run settings

```text
EXP_ID = EXP-004
MAX_MOVES = 10000
SEED = 42
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
No ACTION6 throttle
No public game-id hard-coding
No per-game seed schedule
```

## Required progress-event logging

For every `level_delta > 0`, EXP-004 records:

```text
game_id
step
level_before
level_after
level_delta
progress_action
progress_policy
action_data
state_before
state_after
frame_changed
diff_pixels
resets_before_progress
actions_since_previous_progress
last_10_actions
last_25_actions
last_50_actions
last_100_actions
last_10_policies
last_25_policies
action_counts_before_progress
policy_counts_before_progress
recent_25_noop_rate
recent_25_game_over_rate
recent_50_noop_rate
recent_50_game_over_rate
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
exp004_progress_action_summary.csv
```

## Analysis questions

1. Which games produce level progress only after long horizons?
2. Which action is the immediate progress action?
3. Which actions appear most often in the last 10 / 25 / 50 / 100 actions before progress?
4. Is progress caused by one action or by repeated patterns?
5. Does ACTION6 really cause progress, or is it merely sampled often?
6. Are resets helping discovery or consuming budget?
7. Which patterns could be compressed into a 25k-action policy?

## Expected output

The most useful output is not just the score. It is a progress-window table:

```text
game_id | step | level_before -> level_after | progress_action | last_10_actions | likely_pattern | notes
```

## Candidate follow-up

If repeatable windows are found, implement:

```text
EXP-004B_progress_replay_prior
```

Possible policy direction:

```text
When the current game has similar early evidence to a discovered progress window, bias toward the pre-progress action pattern for a short bounded budget.
```

## Validation gate

Do not submit EXP-004 directly unless explicitly intended as a public high-budget probe.

A later compressed policy should improve at least one of:

```text
25k-action local score
25k-action level count
action efficiency
public Kaggle score
```
