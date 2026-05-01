# 2026-05-01 ARC-AGI-3 EXP-001 setup

## Objective

Implement a clean P1 baseline from the public simplified submission approach and push it to GitHub so it can be pulled into Kaggle.

## K-12 summary

The old robot pressed random buttons. EXP-001 is still random, but it clicks pixels that are actually visible in the game screen. This is like telling the robot: do not poke empty air; poke things you can see.

## What was created

- notebooks/01_exploration/exp001_simplified_random_pixel_click.ipynb
- experiments/EXP-001_simplified_random_pixel_click/README.md
- session_notes/2026-05-01_arc_agi3_exp001_setup.md
- docs/experiment_tracker.md updated with planned EXP-001 row

## Baseline reference

From the uploaded simplified submission log:

- MAX_MOVES = 1000
- Public/local validation games: 25
- Levels completed: approximately 6 / 183
- Total actions: 25000
- Local score: approximately 0.1219

This is not yet a validated result for our cleaned notebook. It is the reproduction target.

## Important implementation choices

- Plotting removed from the scoring loop to reduce runtime and artifact bloat.
- USE_PER_GAME_SEED = False by default to preserve the original reference behavior using Random(42) per game.
- USE_PER_GAME_SEED = True is included as a later toggle, but should not be used for the first reproduction run.
- H100 is not required for EXP-001 because the bottleneck is behavior/search quality, not model inference or fine-tuning.

## Validation steps for Kaggle

1. Pull the repo into Kaggle or upload the notebook from GitHub.
2. Attach it to ARC Prize 2026 / ARC-AGI-3.
3. Keep internet disabled.
4. Run the notebook on standard hardware first.
5. Confirm output artifacts in /kaggle/working and /kaggle/working/exp001_artifacts.
6. Check whether local score is near the reference target 0.1219.
7. Submit only after the local run completes cleanly.

## What worked

- We identified the simplified random pixel-click notebook as the best P1 starting point from the uploaded evidence.
- The cleaned notebook is ready for Kaggle-side validation.
- The experiment tracker now distinguishes validated P0 from planned P1.

## What failed / not yet validated

- EXP-001 has not yet been run in Kaggle from the cleaned notebook.
- The 0.1219 score is a reference target from the uploaded public notebook/log, not a claimed new validated result.
- No heuristic memory, no loop avoidance, and no object reasoning have been added yet.

## Current best result

- Kaggle public validated score: 0.07 from EXP-000.
- EXP-001 target local reproduction score: approximately 0.1219.

## Files changed

- notebooks/01_exploration/exp001_simplified_random_pixel_click.ipynb
- experiments/EXP-001_simplified_random_pixel_click/README.md
- session_notes/2026-05-01_arc_agi3_exp001_setup.md
- docs/experiment_tracker.md

## Next session plan

1. Pull the GitHub updates into Kaggle.
2. Run exp001_simplified_random_pixel_click.ipynb.
3. Compare cleaned-notebook score to the reference 0.1219.
4. If close, submit to Kaggle and record leaderboard score.
5. Start EXP-002: visible-object heuristic explorer with no-op loop avoidance and tag-aware action bias.
