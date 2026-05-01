# 2026-05-01 ARC-AGI-3 EXP-001 setup and local validation

## Objective

Implement a clean P1 baseline from the public simplified submission approach, push it to GitHub, run it in Kaggle local validation mode, and submit it for leaderboard scoring.

## K-12 summary

The old robot pressed random buttons. EXP-001 is still random, but it clicks pixels that are actually visible in the game screen. This is like telling the robot: do not poke empty air; poke things you can see.

Today, that robot did better than expected in local testing and was submitted to the official scoreboard.

## What was created

- notebooks/01_exploration/exp001_simplified_random_pixel_click.ipynb
- experiments/EXP-001_simplified_random_pixel_click/README.md
- experiments/EXP-001_simplified_random_pixel_click/results_2026-05-01.md
- session_notes/2026-05-01_arc_agi3_exp001_setup.md
- docs/experiment_tracker.md updated with EXP-001 row and local validation result

## Baseline reference

From the uploaded simplified submission log:

- MAX_MOVES = 1000
- Public/local validation games: 25
- Levels completed: approximately 6 / 183
- Total actions: 25000
- Local score: approximately 0.1219

This was the initial reproduction target.

## EXP-001 local validation result

Kaggle local validation completed successfully after running the cleaned notebook.

- EXP ID: EXP-001
- MAX_MOVES: 1000
- Seed: 42
- USE_PER_GAME_SEED: False
- Local score: 0.21238458620043624
- Levels completed: 7 / 183
- Environments completed: 0 / 25
- Total actions: 25000
- submission.parquet created: yes

This beats the initial reproduction target of approximately 0.1219 and 6 / 183 levels.

## Tag signal from local scorecard

- keyboard_click: score approximately 0.317911; levels completed: 5
- click: score approximately 0.002229; levels completed: 2
- keyboard: score 0.000000; levels completed: 0

Interpretation: keyboard_click is carrying the useful signal. Keyboard-only is currently not useful. EXP-002 should be tag-aware and should not spend equal effort across all action modes.

## Important implementation choices

- Plotting removed from the scoring loop to reduce runtime and artifact bloat.
- USE_PER_GAME_SEED = False by default to preserve the original reference behavior using Random(42) per game.
- USE_PER_GAME_SEED = True is included as a later toggle, but was not used for the first validation run.
- H100 is not required for EXP-001 because the bottleneck is behavior/search quality, not model inference or fine-tuning.

## Kaggle submission status

EXP-001 has been submitted for Kaggle scoring.

Pending artifact from user:

- submission notebook log
- public score
- best score / version
- observed rank, if available

Do not update the Kaggle result field or claim leaderboard improvement until the submitted score is available.

## What worked

- EXP-001 notebook was created and pushed to GitHub.
- Kaggle local validation ran successfully.
- Local score was 0.21238458620043624, above the expected reproduction target.
- submission.parquet was created successfully.
- GitHub tracker was updated with the local validation result.
- EXP-001 was submitted for official scoring.

## What failed / not yet validated

- Kaggle public score is not available yet.
- No heuristic memory, no loop avoidance, and no object reasoning have been added yet.
- No official improvement claim should be made until the submission result is returned.

## Current best result

- Validated Kaggle public score: 0.07 from EXP-000.
- EXP-001 local validation score: 0.21238458620043624.
- EXP-001 Kaggle score: pending.

## Files changed

- notebooks/01_exploration/exp001_simplified_random_pixel_click.ipynb
- experiments/EXP-001_simplified_random_pixel_click/README.md
- experiments/EXP-001_simplified_random_pixel_click/results_2026-05-01.md
- session_notes/2026-05-01_arc_agi3_exp001_setup.md
- docs/experiment_tracker.md

## Next session plan

1. Ingest the Kaggle submission notebook log and leaderboard score once available.
2. Update docs/experiment_tracker.md with public score, best score/version, and observed rank.
3. If EXP-001 improves on EXP-000, mark it as the new Kaggle baseline.
4. Start EXP-002: visible-object heuristic explorer.
5. EXP-002 first changes should be small and testable:
   - tag-aware action bias toward keyboard_click,
   - no-op loop detection,
   - repeated-action suppression,
   - frame-change memory,
   - visible non-background object targeting.

## Fallback plan

If EXP-001 public score is weak or below EXP-000, keep EXP-000 as the official clean Kaggle baseline and treat EXP-001 as a useful local-only diagnostic. Then run controlled ablations before submitting EXP-002.
