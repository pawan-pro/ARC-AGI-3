# 2026-09-03 Session Notes — Public AGI_9 Reproduction and Model Strategy

## Starting point

- Current recorded best Kaggle public score: `1.11` from `EXP-DUCK-024`.
- That solver used Qwen3.6-27B-FP8 with game-specific support, including the
  `ft09` replay path and signature-gated `tn36` postlude.
- The unfinished game-specific investigation remains `ft09` level 5: three
  magenta controls were characterized, but no completion sequence was found.

## Public baseline review

We reviewed newer public ARC-AGI-3 notebooks and selected the Apache-2.0 notebook
`[LB 1.17] ARC-AGI-3 Qwen3.6 Duck | Full Code` as the first reproducible baseline.
It is smaller and easier to attribute than the more elaborate `Sandwich` approach.

The later public `1.33` listing appears to contain the same AGI_8/AGI_9 solver
changes. Its short save was a registration path rather than a fresh public-game
evaluation, so `1.33` is not treated as independently reproduced evidence.

## Frozen artifact and validation

Created an isolated reproduction bundle under:

```text
experiments/EXP-DUCK-038_public_agi9_reproduction/
```

The selected notebook was copied exactly as published. “Frozen” refers to the
notebook artifact, not frozen model weights. Its SHA-256 is:

```text
015443fd998f5bac097211fcd8372a30c1ae3abdc4883b11be3535301a42d870
```

Validation results:

- All nine code cells compile.
- Safety anchors are present.
- No Kaggle competition-submission call is present.
- Upstream notebook, source-bundle, wheelhouse, model, and license metadata were
  recorded in the experiment manifest.

## Current run

A new private Kaggle kernel was launched:

```text
jatalepawan/arc3-duck-agi9-public-repro-20260903
Version: 1
Last verified state: RUNNING
```

This is an offline evaluation on the 25 public games. It may write a dummy
`submission.parquet`, but it does not submit to the competition. An hourly monitor
is attached and should remain quiet while the state is unchanged; on completion it
will download and validate outputs, report failure without retrying, and stop.

## How the current notebook works

The notebook runs one Qwen3.6-27B-FP8 model, not a multi-model ensemble. It processes
many game sessions concurrently, but all sessions use the same model.

For each turn the harness provides the current grid, recent observations and actions,
reward/state information, and the model's compact working theory. The prompt asks the
model to inspect the board, update its theory of objects, rules, goals, and uncertainty,
use Python when helpful, choose the shortest reliable move or a useful diagnostic probe,
then observe the result and revise.

Relative to the older `EXP-DUCK-024` approach, the public notebook removes notebook-level
`ft09` and `tn36` shortcuts and adds two general changes:

1. `AGI_8`: if a directional move has no visible effect and the same move is immediately
   requested again in that batch, cancel the repetition and force a fresh observation.
2. `AGI_9`: increase analyzer yield time from 60 to 90 seconds, allowing another inspection
   cycle before scheduling resumes.

The attached source bundle also differs from the earlier experiment, so one reproduction
tests the full artifact and cannot by itself attribute any gain to AGI_8 or AGI_9.

## Model and multimodal decision

The current run is single-model but multimodal: Qwen receives the board representation and
image context and can use computation/tools inside the solver loop. Parallel games should
not be confused with multiple models voting on one move.

Stronger external models and multi-model designs are possible, including a primary player
plus a critic/verifier. However, public-demo harness results for models such as Claude Opus 5
or GPT-5.6 Sol are not directly comparable with Kaggle scores, and external API use must be
checked against competition rules, offline constraints, cost, and reproducibility.

Decision: finish the exact Qwen reproduction first. Then compare models or a proposer-verifier
design on a small controlled subset rather than changing model, prompt, harness, and tools at
the same time.

## Next steps

1. Wait for the private reproduction to reach a terminal state and validate its outputs.
2. Record per-game results, runtime, failures, and aggregate public-game score.
3. If reproducible, run controlled ablations: AGI_8 only, AGI_9 only, then both off.
4. Replicate promising configurations two or three times because Duck runs are variable.
5. Only then test a stronger model or multimodel proposer-verifier setup on the same fixed
   subset and budget.
6. Make no competition submission without explicit user authorization.

## Workspace safeguards

Two pre-existing modified files were deliberately left untouched by this note commit:

```text
docs/experiment_tracker.md
scripts/kaggle_kernel_run.py
```
