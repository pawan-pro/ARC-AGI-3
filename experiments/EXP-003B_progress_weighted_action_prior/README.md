# EXP-003B — Progress-Weighted Action Prior

## Purpose

EXP-003A proved that we can collect action/effect logs without changing EXP-001 behavior or score. EXP-003B is the first cautious policy experiment using those logs.

The goal is not object-click memory. EXP-003 failed because it treated frame change as usefulness and over-clicked objects that changed pixels but did not make progress.

EXP-003B instead tests a small progress-weighted action prior:

- keep most EXP-001 randomness,
- use a tiny per-game action bias only after observing local effects,
- rank usefulness by progress signals, not by frame change alone.

## Baseline to beat

Current validated public baseline:

- EXP-001 public score: 0.11
- EXP-001 local score: 0.21238458620043624
- EXP-001 local levels: 7 / 183

Safe logging scaffold:

- EXP-003A local score: 0.21238458620043624
- EXP-003A local levels: 7 / 183

## Hypothesis

A very small action prior may preserve EXP-001's stochastic exploration while improving action efficiency in games where the log reveals one action family is clearly useful.

## Design

Use EXP-001 random policy as default.

At each step:

- 90% EXP-001 random action
- 10% progress-prior action

The prior is updated online from this run only.

Action utility scoring priority:

1. level_delta > 0: strong positive
2. state changes to WIN or level progress: strong positive
3. state changes to GAME_OVER: strong negative
4. repeated no-op: negative
5. frame change without progress: weak positive only

## Important constraint

Do not use public game-id hard-coding. Do not use per-game seed schedule. Do not use object/component targeting. This is an action-level prior only.

## Notebook

notebooks/01_exploration/exp003b_progress_weighted_action_prior.ipynb

## Validation gate before submission

Submit only if local validation is at least competitive with EXP-001:

- Local score >= 0.21238458620043624
- Local levels >= 7 / 183
- submission.parquet created
- no runtime failure

If it underperforms, do not submit. Use it as an ablation showing that even soft online action priors need better timing/state abstraction.

## Expected artifacts

- exp003b_scorecard_summary.json
- exp003b_scorecard_by_environment.csv
- exp003b_scorecard_by_tag.csv
- exp003b_run_results.csv
- exp003b_run_details.json
- exp003b_action_counts.json
- exp003b_policy_counts.json
- exp003b_action_prior_by_game.json
- exp003b_effect_summary_by_game.csv
