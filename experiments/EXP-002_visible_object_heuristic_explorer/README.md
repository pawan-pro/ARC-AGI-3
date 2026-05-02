# EXP-002 Visible Object Heuristic Explorer

## Purpose

EXP-002 is the first step beyond random visible-pixel clicking. It adds a lightweight visual parser, no-op memory, object-targeted click selection, and directional movement bias.

## Baseline to beat

Current best validated Kaggle baseline:

- EXP-001 public score: 0.11
- EXP-001 local score: 0.21238458620043624
- EXP-001 local levels: 7 / 183

## Hypothesis

A simple object-aware explorer may beat EXP-001 if it:

1. avoids undo by default,
2. uses known directional semantics for ACTION1-4,
3. suppresses actions that do not change the frame,
4. clicks small non-background components instead of arbitrary visible pixels,
5. prefers movement toward target-like components,
6. records candidate object effects for later analysis.

## Important action mapping

- ACTION1 = up
- ACTION2 = down
- ACTION3 = left
- ACTION4 = right
- ACTION5 = spacebar
- ACTION6 = click with x,y
- ACTION7 = undo

## Notebook

notebooks/01_exploration/exp002_visible_object_heuristic_explorer.ipynb

## Validation target before submission

- Local score >= 0.21238458620043624
- Local levels >= 7 / 183
- submission.parquet created
- No runtime failure

If the local score is weaker than EXP-001, do not submit. Treat this as an ablation and improve the parser/planner.
