# EXP-001 Simplified Random Pixel Click Baseline

Purpose: clean P1 reproduction baseline for ARC-AGI-3.

Core idea: choose a random non-reset action. For complex click actions, choose a random color present in the current frame, then choose a random pixel with that color.

Reference target from uploaded simplified-submission log:

- MAX_MOVES = 1000
- Public/local games = 25
- Levels completed = about 6 / 183
- Total actions = 25000
- Score = about 0.1219

Primary notebook:

notebooks/01_exploration/exp001_simplified_random_pixel_click.ipynb

Expected Kaggle artifacts:

- /kaggle/working/submission.parquet
- /kaggle/working/exp001_artifacts/exp001_run_results.csv
- /kaggle/working/exp001_artifacts/exp001_scorecard_summary.json
- /kaggle/working/exp001_artifacts/exp001_scorecard_by_environment.csv
- /kaggle/working/exp001_artifacts/exp001_scorecard_by_tag.csv

Reproducibility notes:

- Keep USE_PER_GAME_SEED = False for the first reproduction run.
- Do not enable plotting during scoring.
- Do not use H100 for this experiment; the bottleneck is behavior, not GPU compute.
- Preserve EXP-000 as the clean Kaggle submission control baseline.

Next experiment: EXP-002 visible-object heuristic explorer with no-op loop detection, repeated-action suppression, tag-aware action selection, and frame-change memory.
