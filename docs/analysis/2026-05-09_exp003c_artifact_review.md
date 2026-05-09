# 2026-05-09 EXP-003C artifact review

## Purpose

Review the newly attached EXP-003C artifacts and confirm whether they support the next controlled experiment direction.

## Artifact bundle reviewed

The user attached the EXP-003C artifacts:

```text
artifact_manifest (6).csv
exp003c_scorecard_summary (1).json
exp003c_scorecard_by_environment (1).csv
exp003c_scorecard_by_tag (1).csv
exp003c_run_results (1).csv
exp003c_run_details (1).json
exp003c_action_counts (1).json
exp003c_policy_counts (1).json
exp003c_effect_summary_by_game (1).csv
exp003c_action_prior_by_game (1).json
```

This closes the missing-artifact gap from the 2026-05-08 session closeout.

## EXP-003C scorecard confirmation

```text
EXP-003C local score: 0.481950521305291
Levels completed: 7 / 183
Actions: 25,000
Environments completed: 0 / 25
```

## Policy counts

```text
exp001_random_visible_pixel_fallback: 24,296
progress_prior_guardrailed: 416
reset: 288
```

Interpretation:

- EXP-003C mostly behaves like the EXP-001 fallback.
- The progress-prior path is active but sparse.
- The lower prior probability worked as designed, but it did not solve ACTION6 overuse.

## Action counts

```text
ACTION1: 3,007
ACTION2: 3,032
ACTION3: 3,298
ACTION4: 3,345
ACTION5: 1,697
ACTION6: 8,667
ACTION7: 1,666
RESET: 288
```

ACTION6 remains the dominant action.

## Aggregate action diagnostics

```text
ACTION1 count=3,007 | noops=229 | game_over=27 | level_delta=0 | utility=-455.74
ACTION2 count=3,032 | noops=195 | game_over=26 | level_delta=0 | utility=-399.13
ACTION3 count=3,298 | noops=234 | game_over=33 | level_delta=1 | utility=-542.48
ACTION4 count=3,345 | noops=186 | game_over=41 | level_delta=0 | utility=-791.64
ACTION5 count=1,697 | noops=318 | game_over=42 | level_delta=2 | utility=-1147.82
ACTION6 count=8,667 | noops=3,005 | game_over=120 | level_delta=4 | utility=-3968.59
ACTION7 count=1,666 | noops=814 | game_over=0 | level_delta=0 | utility=-157.97
```

## ACTION6 interpretation

ACTION6 is both the most useful and the most dangerous action:

```text
ACTION6 level_delta: 4
ACTION6 noops: 3,005
ACTION6 GAME_OVER: 120
ACTION6 utility: -3968.59
```

K-12 version: ACTION6 is like a risky lever. Sometimes it opens a door, but it often does nothing or breaks the run. We should not remove it completely. We should learn when it is dangerous.

## Games where ACTION6 produced level progress

```text
tn36-ef4dde99 | ACTION6 count=985 | level_delta=1 | game_over=15 | noops=0 | utility=-352.30
lp85-305b61c3 | ACTION6 count=996 | level_delta=1 | game_over=4  | noops=851 | utility=-335.79
vc33-5430563c | ACTION6 count=981 | level_delta=1 | game_over=19 | noops=0 | utility=-453.28
r11l-495a7899 | ACTION6 count=965 | level_delta=1 | game_over=35 | noops=0 | utility=-861.47
```

This is the strongest reason not to globally ban ACTION6.

## Other level-progress actions

```text
m0r0-492f87ba | ACTION3 | level_delta=1 | utility=42.65
cd82-fb555c5d | ACTION5 | level_delta=1 | utility=16.43
sp80-589a99af | ACTION5 | level_delta=1 | utility=-689.78
```

## Tag-level result

```text
keyboard_click | score=0.300761 | levels=3 | environments=13
click          | score=0.736952 | levels=4 | environments=7
keyboard       | score=0.000000 | levels=0 | environments=4
```

This suggests the current random/click-heavy policy still has no solved path for pure keyboard environments.

## Conclusion

The uploaded EXP-003C artifacts confirm the 2026-05-08 provisional conclusion:

1. EXP-003C is a useful near-tie diagnostic.
2. EXP-003C does not beat EXP-003B by local score.
3. EXP-003C improves level count from `6 / 183` to `7 / 183`.
4. ACTION6 remains dominant and risky.
5. ACTION6 cannot be globally banned because it produced `4 / 7` level deltas.
6. No-op-based throttling is risky because it may suppress useful exploration.
7. GAME_OVER-focused throttling is the cleaner next controlled experiment.

## Recommended next experiment

Create EXP-003F as a controlled diagnostic candidate:

```text
Base: EXP-003E diagnostics
Disable no-op-based ACTION6 throttle
Throttle ACTION6 only if local ACTION6 GAME_OVER rate is bad
Protect ACTION6 if it has produced any level_delta in the current game
Use a nonzero keep probability so the action is never fully banned
```

Suggested initial constants:

```text
ACTION6_MIN_OBS_FOR_THROTTLE = 30
ACTION6_BAD_GAME_OVER_RATE = 0.04
ACTION6_THROTTLE_KEEP_PROB = 0.50
ACTION6_LEVEL_DELTA_PROTECT = any current-game ACTION6 level_delta > 0
NO ACTION6 no-op throttle
```

## Validation gate

Do not submit EXP-003F unless:

```text
score >= EXP-003B local score 0.48491096178440257
```

or it is very close while preserving `7 / 183` levels and reducing resets / ACTION6 GAME_OVER events clearly.
