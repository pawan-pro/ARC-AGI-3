# Full Duck Evaluation with Confirmed ft09 Helper

Date: 2026-07-17

Experiment: `EXP-DUCK-009`

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-full-eval-ft09-overlap
```

## Controlled Change

Run every baseline game once. Only `ft09-0d8bbf25` receives:

1. the confirmed 48-action replay to level 4
2. the confirmed 21-click overlap-consistent level-4 target
3. a per-game stop after reaching level 5

All non-ft09 games retain the baseline model, prompt, action cap, runtime cap,
concurrency, game list, and one-pass evaluation behavior.

The controlled stall policy is disabled. The targeted diagnostic's shared
120-action cap and four-game concurrency cap are removed.

## Acceptance Criteria

```text
25 games run exactly once
ft09 reaches at least 4/6 in 69 actions
non-ft09 settings remain baseline-equivalent
no run-wide cap is changed when ft09 finishes
```

Compare total levels, score sum, actions, tokens, and per-game outcomes against
the stored Duck public reproduction benchmark. A public leaderboard score still
requires a real competition submission; this kernel is the complete offline
evaluation first.
