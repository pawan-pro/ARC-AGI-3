# 2026-05-09 EXP-003F null-result review

## Purpose

Analyze EXP-003F after the local Kaggle/offline run and decide whether it should be submitted or used only as a diagnostic artifact.

## EXP-003F design

EXP-003F was designed as a controlled follow-up to EXP-003E:

```text
Keep EXP-003E diagnostics.
Disable no-op-based ACTION6 throttle.
Throttle ACTION6 only when local ACTION6 GAME_OVER rate is bad and no current/recent ACTION6 level_delta protects it.
ACTION6_THROTTLE_KEEP_PROB = 0.50
```

K-12 version: EXP-003F tried to stop the robot from pressing the risky ACTION6 button only when that button was clearly breaking the game, not merely when it did nothing.

## Run result

```text
EXP-003F local score: 0.481950521305291
Levels: 7 / 183
Actions: 25,000
Environments completed: 0 / 25
submission.parquet: created
```

## Policy counts

```text
exp001_random_visible_pixel_fallback_action6_gameover_throttle: 24,296
progress_prior_guardrailed: 416
reset: 288
```

These are identical to EXP-003C except for the fallback policy name.

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

These are exactly identical to EXP-003C.

## Policy-action counts

```text
fallback ACTION6: 8,635
prior ACTION6: 32
```

This again confirms ACTION6 overuse is fallback-driven, not progress-prior-driven.

## ACTION6 throttle result

```json
{}
```

No ACTION6 throttle event fired.

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

## Comparison to prior experiments

```text
EXP-003B score: 0.4849109618 | levels: 6 / 183 | ACTION6: 8,613 | RESET: 295
EXP-003C score: 0.4819505213 | levels: 7 / 183 | ACTION6: 8,667 | RESET: 288
EXP-003D score: 0.4809739507 | levels: 6 / 183 | ACTION6: 7,876 | RESET: 304
EXP-003E score: 0.4818242866 | levels: 7 / 183 | ACTION6: 8,086 | RESET: 303
EXP-003F score: 0.4819505213 | levels: 7 / 183 | ACTION6: 8,667 | RESET: 288
```

## Interpretation

EXP-003F is a null diagnostic result.

It did not fail mechanically: the notebook ran, produced artifacts, and created `submission.parquet`. However, the new throttle logic never activated, so the policy behavior was effectively identical to EXP-003C.

Main reason:

```text
The GAME_OVER-only threshold plus level-delta protection made the throttle inert.
```

This means EXP-003F does not add a new leaderboard candidate. It confirms that simply switching from no-op throttle to GAME_OVER-only throttle is not enough unless the trigger is designed at a more precise per-game or per-state level.

## Gate decision

```text
Do not submit EXP-003F.
Keep EXP-003B as public baseline.
```

## Lessons

1. ACTION6 overuse is fallback-driven.
2. No-op throttling can reduce ACTION6 but risks suppressing useful exploration.
3. GAME_OVER-only throttling was too weak/inert in EXP-003F.
4. ACTION6 needs per-game or per-state risk modeling, not another global throttle threshold.
5. The next step should be an offline comparison notebook, not another immediate policy tweak.

## Recommended next step

Create an offline analysis notebook:

```text
notebooks/02_analysis/exp003cde_f_artifact_comparison.ipynb
```

Purpose:

- Compare EXP-003C, EXP-003D, EXP-003E, and EXP-003F artifacts side by side.
- Identify games where ACTION6 is useful versus harmful.
- Separate one-action games from mixed-action games.
- Determine whether resets and level losses are driven by ACTION6 itself or by replacement actions.

## Possible future EXP-003G direction

Do not implement immediately. Candidate after artifact comparison:

```text
Per-game action risk table:
- avoid actions that show high game-over rate and zero level progress in that game;
- preserve actions that have produced level_delta;
- use soft downweighting, not hard bans;
- keep fallback stochasticity.
```
