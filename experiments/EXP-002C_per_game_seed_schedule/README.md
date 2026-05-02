# EXP-002C — Per-Game Seed Schedule

## Purpose

Use the EXP-002B seed sweep to test whether different public tasks benefit from different random seeds under the same EXP-001 visible-pixel random policy.

This is a controlled ablation, not a general intelligence improvement yet. It may overfit the 25 public demo environments, so it should only be submitted if local validation is clearly stronger and we understand the risk.

## Baseline to beat

- EXP-001 public score: 0.11
- EXP-001 local score: 0.21238458620043624
- EXP-001 local levels: 7 / 183
- EXP-001 seed: 42

## Design

Keep the EXP-001 policy exactly the same, including ACTION7 and visible-pixel random complex actions.

Only change:

- choose seed by game_id where the seed sweep showed a different seed completing a level locally;
- otherwise use seed 42 fallback.

## Initial seed map

The first seed map uses the printed EXP-002B seed-sweep log:

- vc33-detected local completion with seed 0/2/3/5/100; use seed 0
- r11l-detected local completion with seed 1/3/10/100/123; use seed 10
- all other games use seed 42 unless the seed sweep clearly showed a better per-game level result

## Notebook

notebooks/01_exploration/exp002c_per_game_seed_schedule.ipynb

## Validation gate before submission

Submit only if local validation beats EXP-001:

- Local score > 0.21238458620043624
- Local levels >= 7 / 183, preferably > 7 / 183
- submission.parquet created
- no runtime failure

## Caution

This may not generalize to hidden games because hidden game_ids may differ. Treat this as a measurement of seed variance and per-game stochastic sensitivity, not as the final medal-level strategy.
