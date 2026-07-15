# ft09 Level-4 Exhaustive Candidate Diagnostic Plan

Date: 2026-07-15

Experiment: `EXP-DUCK-006`

Notebook variant:

```text
notebooks/04_submission_builds/duck_public_repro_terminal_run/arc3_20260704_duck_public_repro_ft09_level4_exhaustive.ipynb
```

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-ft09-level4-exhaustive
```

## Plan

This is a diagnostic-only run. It reuses the 48-action `ft09` prefix replay, reaches level 4, and then runs the existing 8 mask-cycle candidates to true exhaustion.

Changes from `EXP-DUCK-005`:

- disables the deterministic-run zero-token stall cap by setting `max_consecutive_zero_token_actions` to `None`
- raises `max_actions_per_game` from `220` to `420`
- writes a direct JSON candidate trace to:

```text
artifacts/<game_id>_ft09_level4_candidate_trace.json
```

Trace fields:

```text
candidate_index
candidate
start_action
planned_actions
executed_actions
before_centers
target_centers
after_centers
completed_candidate
solved
```

## Iteration Boundary

Run this fixed 8-candidate set once.

If one candidate solves level 4, promote that mapping into a cleaner helper and test a full-game targeted run.

If all 8 candidates fail, stop adding candidate guesses. The next step should be direct visual/mapping analysis of level 4, not more blind variants.

## Evaluation Notebook Gate

Do not run a full evaluation notebook yet.

Run evaluation only after a targeted diagnostic shows either:

- `ft09` improves from 3/6 to at least 4/6, or
- the same helper generalizes to at least one more game/mechanic family.

Until then, full evaluation is too expensive and mostly measures noise around an unproven helper.
