# Controlled Stall Trace Review - 2026-07-08

Source run:

```text
artifacts/kaggle/duck_public_repro_terminal_run/latest/benchmark.json
```

Notebook variant:

```text
notebooks/04_submission_builds/duck_public_repro_terminal_run/arc3_20260704_duck_public_repro_stall_policy.ipynb
```

## Visual Inspection

The workbench notebook already has a visual diagnostics cell:

```text
notebooks/04_submission_builds/duck_public_repro_terminal_run/arc3_20260704_duck_public_repro_workbench.ipynb
cells 18-19: Show the diagnostics
```

After a Kaggle practice run, open section 8. It renders `/kaggle/working/diagnostics.html` inline. The downloaded local equivalents are:

```text
artifacts/kaggle/duck_public_repro_terminal_run/latest/diagnostics.html
artifacts/kaggle/duck_public_repro_terminal_run/latest/movies/
artifacts/kaggle/duck_public_repro_terminal_run/latest/solver_analysis/
```

## Trace Findings

| game | score | levels | actions | generated tokens | zero-token actions | transition actions | observed failure |
|---|---:|---:|---:|---:|---:|---|---|
| `tn36-ef4dde99` | 0.00 | 0/7 | 122 | 69,693 | 61 | none | repeated mouse clicks, no level progress |
| `sc25-635fd71a` | 0.00 | 0/6 | 147 | 70,194 | 92 | none | repeated mouse clicks, no level progress |
| `ft09-0d8bbf25` | 8.10 | 2/6 | 82 | 70,043 | 59 | 42, 63 | real progress from mouse clicks, then stalls on level 3 |
| `tr87-cd924810` | 0.00 | 0/6 | 330 | 61,632 | 307 | none | long keyboard action loop, no level progress |

The dominant constraint is not raw GPU availability. The run reaches the model/action budget while continuing low-value actions. The actionable failure mode is no level progress after many actions, especially where `board_changed=True` is only weak evidence and does not imply game progress.

## Controlled Policy

Use one source-level patch in the notebook variant:

```text
controlled_stall_policy.enabled = true
controlled_stall_policy.min_actions = 24
controlled_stall_policy.max_no_level_progress_actions = 90
controlled_stall_policy.max_consecutive_zero_token_actions = 70
```

Rationale:

```text
ft09 reaches level progress at actions 42 and 63, so a 90-action no-progress limit should preserve the known useful behavior.
tn36, sc25, and tr87 have no level transitions, so the same limit should reduce wasted tokens/actions.
zero-token runs are useful diagnostics, but the longest consecutive zero-token run in tr87 was 55, so zero-token detection alone would not catch the main stall.
```

## Validation Plan

Run the stall-policy notebook on only:

```text
tn36-ef4dde99
sc25-635fd71a
ft09-0d8bbf25
tr87-cd924810
```

Accept the policy only if:

```text
1. ft09 still gets at least 2 level transitions.
2. tn36/sc25/tr87 spend fewer actions and tokens than baseline.
3. diagnostics clearly mark controlled_stall in solver_note for stopped games.
```

Do not submit this variant to the leaderboard until the targeted practice run passes those checks.
