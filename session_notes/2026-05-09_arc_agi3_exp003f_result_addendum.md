# 2026-05-09 ARC-AGI-3 session addendum — EXP-003F result

## Objective

Record EXP-003F local run result and decide whether it changes the current baseline or submission plan.

## K-12 summary

EXP-003F tried a gentler safety rule: only slow down ACTION6 when ACTION6 is clearly causing game-over problems. But the rule never actually activated. So the robot behaved the same as EXP-003C.

## EXP-003F run result

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

## Policy-action counts

```text
fallback ACTION6: 8,635
prior ACTION6: 32
```

## ACTION6 throttle counts

```json
{}
```

No throttle event fired.

## Interpretation

EXP-003F is a null diagnostic result.

It is not a runtime failure. The script ran successfully, produced artifacts, and created `submission.parquet`. But because no ACTION6 throttle event fired, EXP-003F reproduced EXP-003C behavior exactly except for policy naming.

Key comparison:

```text
EXP-003C score: 0.4819505213 | levels: 7 / 183 | ACTION6: 8,667 | RESET: 288
EXP-003F score: 0.4819505213 | levels: 7 / 183 | ACTION6: 8,667 | RESET: 288
```

## Decision

```text
Do not submit EXP-003F.
Keep EXP-003B as public baseline.
```

## Current best score/result

```text
Public best: EXP-003B public score 0.12
Local best by score: EXP-003B local score 0.48491096178440257
Best recent level count: EXP-003C / EXP-003E / EXP-003F at 7 / 183
```

## Lesson

ACTION6 still needs a more precise treatment:

- no-op throttling was too blunt in EXP-003D/E;
- GAME_OVER-only throttling was too weak/inert in EXP-003F;
- global thresholds are not enough;
- the next step should be offline per-game/per-action risk analysis.

## Next session/action recommendation

Do not immediately create another policy variant.

Create an offline comparison notebook first:

```text
notebooks/02_analysis/exp003cde_f_artifact_comparison.ipynb
```

The notebook should compare EXP-003C, EXP-003D, EXP-003E, and EXP-003F artifacts across:

```text
score
levels
resets
ACTION6 count
fallback ACTION6 count
prior ACTION6 count
ACTION6 noops
ACTION6 GAME_OVER
ACTION6 level_delta
per-game action utility
```

Candidate future EXP-003G should only be implemented after that comparison.

## Files updated

```text
docs/experiment_tracker.md
docs/analysis/2026-05-09_exp003f_null_result_review.md
session_notes/2026-05-09_arc_agi3_exp003f_result_addendum.md
```

## Commit references

```text
a0ccb2a64a22367b0577c127b7d5864bf5c1e559 — experiments: record EXP-003F null result
7d093744125d52b16a1c277d6d8c6d24d7b0124c — analysis: add EXP-003F null-result review
```
