# EXP-003A — Affordance Log-Only Ablation

## Purpose

EXP-003 regressed because memory-biased clicks changed the policy and over-selected objects that changed pixels but did not cause progress.

EXP-003A separates logging from action selection:

- keep the EXP-001 visible-pixel random policy exactly unchanged,
- add affordance/effect logging only,
- make zero action decisions from memory.

## Baseline to reproduce

Current validated public baseline:

- EXP-001 public score: 0.11
- EXP-001 local score: 0.21238458620043624
- EXP-001 local levels: 7 / 183
- EXP-001 seed: 42

## Hypothesis

If logging alone reproduces EXP-001 local behavior, then we can safely collect object/action/effect artifacts without harming score.

If logging changes the result materially, the instrumentation is not policy-neutral and needs to be simplified.

## Notebook

notebooks/01_exploration/exp003a_affordance_log_only.ipynb

## Expected behavior

- same action policy as EXP-001,
- same seed as EXP-001,
- same action space as EXP-001,
- no memory-biased actions,
- no no-op suppression,
- no object-center policy override.

## Expected artifacts

- exp003a_scorecard_summary.json
- exp003a_scorecard_by_environment.csv
- exp003a_scorecard_by_tag.csv
- exp003a_run_results.csv
- exp003a_run_details.json
- exp003a_action_counts.json
- exp003a_effect_log_sample.json
- exp003a_effect_summary_by_game.csv

## Validation gate

Pass if local result is close to EXP-001:

- local score approximately 0.21238458620043624,
- levels approximately 7 / 183,
- submission.parquet created,
- no runtime failure.

Do not submit this notebook unless it unexpectedly improves public-relevant behavior. Its primary purpose is diagnostic logging.
