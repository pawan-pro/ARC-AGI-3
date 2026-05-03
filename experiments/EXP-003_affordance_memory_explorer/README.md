# EXP-003 — Affordance Memory Explorer

## Purpose

EXP-003 is the first durable generalization step after EXP-002C failed to improve public score.

The goal is not to hard-code a specific public game or optimize a random seed. The goal is to let the agent build a tiny memory table during play:

object/action -> observed effect

## Current baseline

Current validated public baseline:

- EXP-001 public score: 0.11
- EXP-001 local score: 0.21238458620043624
- EXP-001 local levels: 7 / 183

EXP-002C local result improved to 9 / 183 levels but public score stayed 0.11, confirming likely public-demo overfit.

## Hypothesis

A conservative affordance-memory agent may improve over EXP-001 if it mostly preserves random visible-pixel exploration while softly preferring objects/actions that previously caused useful changes.

## First implementation scope

EXP-003 should be conservative:

- 80% to 90% EXP-001-style random visible-pixel actions
- 10% to 20% memory-biased actions
- record every action effect
- bias toward candidate objects that previously caused frame changes
- avoid hard policy routing that replaces random exploration

## Effects to record

- frame changed
- number of changed pixels
- object/click target
- level count changed
- game state changed
- action was no-op
- candidate was clicked before

## Notebook

notebooks/01_exploration/exp003_affordance_memory_explorer.ipynb

## Validation gate before submission

Submit only if local validation is at least competitive with EXP-001:

- Local score >= 0.21238458620043624
- Local levels >= 7 / 183
- submission.parquet created
- no runtime failure

If it underperforms, do not submit. Use logs to design EXP-003A/B ablations.

## Expected artifacts

- exp003_scorecard_summary.json
- exp003_scorecard_by_environment.csv
- exp003_scorecard_by_tag.csv
- exp003_run_results.csv
- exp003_run_details.json
- exp003_effect_memory.json
- exp003_policy_counts.json
- exp003_action_counts.json
- exp003_noop_counts.json
