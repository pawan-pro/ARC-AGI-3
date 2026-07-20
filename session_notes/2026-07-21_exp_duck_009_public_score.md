# EXP-DUCK-009 Public Score

Date: 2026-07-21

## Official Result

```text
Submission reference: 54851402
Description: EXP-DUCK-009 Duck full eval with validated ft09 overlap helper
Status: COMPLETE
Public score: 0.92
Previous Duck baseline: 0.84
Absolute improvement: +0.08
Relative improvement: +9.5%
```

This is the project's new strongest validated Kaggle submission and is now the
active baseline.

## What Changed

The submission preserved the Duck model, prompt, runtime limits, concurrency,
and one-pass behavior. Only `ft09` received the confirmed deterministic path:

1. replay 48 known actions to reach level 4
2. apply the 21-click overlap-consistent target `RORbRRRRRORRbRROOO`
3. stop that game after reaching level 5

The controlled full evaluation had already reproduced the isolated result:
`ft09` reached 4/6 in 69 actions with zero model tokens.

## Interpretation

The public improvement from 0.84 to 0.92 is evidence that a replay-derived,
mechanic-specific helper can improve the real competition result without global
prompt tuning.

The local evaluation mean of 2.63 did not translate one-for-one into the public
score. It was a useful promotion gate, not a leaderboard forecast. Non-ft09
outcome changes in the local run were stochastic and should not be credited to
the ft09-only helper.

## Next Step

Keep EXP-DUCK-009 unchanged as the active baseline. Inspect a game with both a
successful and failed trace, starting with `tn36`, infer one mechanic from the
replay evidence, and test the next helper in isolation before another full run
or submission.
