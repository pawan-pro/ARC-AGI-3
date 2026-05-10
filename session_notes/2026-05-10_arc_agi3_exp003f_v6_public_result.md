# 2026-05-10 ARC-AGI-3 — EXP-003F Version 6 public result

## Objective

Record and analyze the Kaggle public result for:

```text
EXP-003F — progress-weighted action prior — Version 6
```

## Result

User reported Kaggle result:

```text
Public Score: 0.12
Best Score: 0.12 V6
```

## Key interpretation

EXP-003F Version 6 tied the current public best but did not improve beyond it.

Current confirmed public baseline remains:

```text
EXP-003B public score: 0.12
```

Version 6 should therefore be recorded as a public tie / no-improvement probe, not a new baseline.

## Uploaded rerun log finding

The uploaded Kaggle log shows EXP-003C-style code and settings:

```text
EXP_ID = "EXP-003C"
MAX_MOVES = 1000
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
```

The log output confirms:

```text
EXP-003C envs=25 MAX_MOVES=1000 SEED=42 PRIOR_PROB=0.05 MIN_PRIOR_OBS=12
Score: 0.4820
Levels: 7 / 183
Actions: 25,000
```

The scorecard summary in the log confirms:

```text
score: 0.481950521305291
total_levels_completed: 7
total_levels: 183
total_actions: 25,000
```

## Important conclusion

The public Version 6 submission does **not** appear to be the 5000-move long-horizon local variant.

The submitted/rerun code corresponds to the 1000-move EXP-003C-style run, not:

```text
EXP-003F_5000 local score: 0.5105754965839018
MAX_MOVES = 5000
Actions = 125,000
```

Therefore, the 5000-move result remains a local long-horizon diagnostic only and has not been validated publicly.

## Decision

```text
Do not update public baseline.
Keep EXP-003B as public baseline at 0.12.
Record EXP-003F V6 as public tie / no-improvement.
```

## Lessons

1. Public score did not improve despite local 7-level EXP-003C/EXP-003F behavior.
2. Version 6 likely submitted the 1000-move EXP-003C-style configuration.
3. Local long-horizon `MAX_MOVES=5000` remains unsubmitted/unvalidated publicly.
4. The next research step should still be EXP-004 long-horizon discovery logging, not another blind submission.

## Next steps

1. Preserve EXP-003B as clean public baseline.
2. Keep EXP-003F_5000 as a local discovery signal only.
3. Implement `EXP-004_long_horizon_discovery` to record progress windows around `level_delta > 0`.
4. Optionally create a separate high-budget Kaggle probe later, but only with explicit version naming and after confirming runtime/action-budget implications.

## Files updated

```text
docs/experiment_tracker.md
session_notes/2026-05-10_arc_agi3_exp003f_v6_public_result.md
```

## Commit reference

```text
263b2c4743d2627b5b88d3fea470f15dc004b8b4 — experiments: record EXP-003F V6 public score
```
