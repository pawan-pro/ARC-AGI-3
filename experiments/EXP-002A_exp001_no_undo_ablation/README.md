# EXP-002A — EXP-001 No-Undo Ablation

## Purpose

Smallest controlled ablation after EXP-002 regressed locally.

EXP-002A keeps the EXP-001 visible-pixel random policy almost unchanged and removes only ACTION7 / undo from the random action pool.

## Baseline to beat

Current best validated Kaggle baseline:

- EXP-001 public score: 0.11
- EXP-001 local score: 0.21238458620043624
- EXP-001 local levels: 7 / 183

EXP-002 routed heuristic failed local gate:

- EXP-002 local score: 0.14996300324361506
- EXP-002 local levels: 5 / 183

## Hypothesis

Random ACTION7 / undo may waste actions or reverse useful accidental progress. Removing it while keeping EXP-001 randomness may improve or at least preserve local performance.

## Notebook

notebooks/01_exploration/exp002a_exp001_no_undo_ablation.ipynb

## Validation gate before submission

Submit only if local run is at least competitive with EXP-001:

- Local score >= 0.21238458620043624
- Local levels >= 7 / 183
- submission.parquet created
- no runtime failure

If it underperforms, do not submit. Treat it as a clean ablation result.
