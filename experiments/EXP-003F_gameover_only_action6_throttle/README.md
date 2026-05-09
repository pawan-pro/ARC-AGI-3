# EXP-003F — GAME_OVER-only ACTION6 throttle

## Purpose

EXP-003C artifacts confirmed that ACTION6 is both useful and risky:

- ACTION6 produced `4 / 7` level deltas in EXP-003C.
- ACTION6 also produced `3,005` no-ops and `120` GAME_OVER events.
- EXP-003D reduced ACTION6 but lost a level.
- EXP-003E softened no-op throttling and recovered 7 levels, but still did not beat EXP-003B.

EXP-003F is the next controlled diagnostic experiment.

K-12 version: ACTION6 is a risky lever. We should not stop using it just because it often does nothing. We should only slow it down when it is actually breaking the game.

## Baseline context

Current public baseline:

```text
EXP-003B public score: 0.12
EXP-003B local score: 0.48491096178440257
EXP-003B local levels: 6 / 183
```

Recent local diagnostics:

```text
EXP-003C score: 0.4819505213 | levels: 7 / 183 | ACTION6: 8,667 | RESET: 288
EXP-003D score: 0.4809739507 | levels: 6 / 183 | ACTION6: 7,876 | RESET: 304
EXP-003E score: 0.4818242866 | levels: 7 / 183 | ACTION6: 8,086 | RESET: 303
```

## Controlled change

EXP-003F keeps EXP-003E-style diagnostics but removes no-op-based ACTION6 throttling.

Throttle rule:

```text
Throttle ACTION6 only when local ACTION6 GAME_OVER rate is bad
and no current/recent ACTION6 level_delta protects it.
```

Initial constants:

```text
ACTION6_MIN_OBS_FOR_THROTTLE = 30
ACTION6_BAD_GAME_OVER_RATE = 0.04
ACTION6_THROTTLE_KEEP_PROB = 0.50
ACTION6_RECENT_LEVEL_DELTA_PROTECT = 1
No ACTION6 no-op throttle
```

## Notebook-source target

```text
notebooks/01_exploration/exp003f_gameover_only_action6_throttle.py
```

The script is standalone and Kaggle-safe. It does not depend on EXP-003D or EXP-003E files being present.

## Expected artifacts

```text
artifact_manifest.csv
exp003f_scorecard_summary.json
exp003f_scorecard_by_environment.csv
exp003f_scorecard_by_tag.csv
exp003f_run_results.csv
exp003f_run_details.json
exp003f_action_counts.json
exp003f_policy_counts.json
exp003f_policy_action_counts.json
exp003f_effect_summary_by_game.csv
exp003f_action_diagnostics_by_game.csv
exp003f_action_prior_by_game.json
exp003f_action6_throttle_counts.json
exp003f_action6_throttle_by_game.csv
```

## Validation gate

Do not submit EXP-003F unless one of these is true:

1. local score beats EXP-003B local score `0.48491096178440257`; or
2. local score is very close, preserves `7 / 183` levels, and clearly reduces ACTION6 GAME_OVER / RESET behavior.

## Fallback plan

If EXP-003F underperforms, do not submit. Keep EXP-003B as public baseline and pivot to offline per-game action-risk analysis before changing policy again.
