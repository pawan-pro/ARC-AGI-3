# EXP-002B — EXP-001 Seed Sweep

## Purpose

Measure how sensitive the EXP-001 visible-pixel random baseline is to the random seed.

EXP-002 and EXP-002A both regressed locally. Before adding more heuristics, we need to quantify stochastic variance and identify whether a better seed exists under the same core policy.

## Baseline to beat

Current best validated Kaggle baseline:

- EXP-001 public score: 0.11
- EXP-001 local score: 0.21238458620043624
- EXP-001 local levels: 7 / 183
- EXP-001 seed: 42

## Design

Run the EXP-001 policy across a set of seeds.

Default seed list:

- 0
- 1
- 2
- 3
- 4
- 5
- 10
- 42
- 100
- 123

## Notebook

notebooks/02_analysis/exp002b_exp001_seed_sweep.ipynb

## Outputs

- exp002b_seed_sweep_summary.csv
- exp002b_seed_sweep_details.json
- exp002b_best_seed_summary.json
- exp002b_best_seed_per_game.csv
- artifact_manifest.csv

## Decision rule

If a seed beats EXP-001 local score and levels, create a scoring notebook with that seed and submit only after local validation.

If no seed beats EXP-001, keep EXP-001 as baseline and continue with controlled policy ablations.
