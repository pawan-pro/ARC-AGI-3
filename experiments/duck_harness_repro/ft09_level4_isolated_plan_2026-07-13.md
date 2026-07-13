# ft09 Level-4 Isolated Diagnostic Plan

Date: 2026-07-13

Experiment: `EXP-DUCK-005`

Notebook variant:

```text
notebooks/04_submission_builds/duck_public_repro_terminal_run/arc3_20260704_duck_public_repro_ft09_level4_isolated.ipynb
```

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-ft09-level4-isolated
```

## Why this experiment exists

`EXP-DUCK-004` was supposed to test the level-4 mask-cycle helper, but the solver stalled on level 1. The helper never activated, so the run did not tell us whether the level-4 idea is useful.

K-12 version: the tool was made for room 4, but the player got stuck in room 1. This run carries the player through the first three rooms using a known-good replay, then tests the room-4 tool.

## Change

This diagnostic variant:

1. Replays the 48-action successful prefix from `EXP-DUCK-003`.
2. Verifies whether the replay reaches level 4.
3. Runs the level-4 mask-cycle helper.
4. Stops after the helper attempt so the result is not mixed with more LLM exploration.

## Guardrails

- Target game only: `ft09-0d8bbf25`.
- Not a leaderboard candidate.
- No prompt/model change.
- Uses the same level-4 candidate generator from `EXP-DUCK-004`.

## Acceptance Criteria

Positive:

- prefix replay reaches level 4, and
- mask-cycle helper completes level 4 or produces measurable progress.

Useful negative:

- prefix replay reaches level 4, but helper exhausts candidates without progress. That means the level-4 clue mapping is wrong and should be inspected directly.

Invalid:

- prefix replay fails before level 4. Then the saved prefix is not portable across runs and we need a state snapshot/replay harness instead.
