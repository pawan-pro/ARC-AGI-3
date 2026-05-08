# EXP-003E — Soft ACTION6 Throttle

## Purpose

EXP-003D confirmed that ACTION6 overuse is mostly fallback-driven and that the local throttle works mechanically, but the throttle was too blunt:

- EXP-003C score: `0.481950521305291`, levels `7 / 183`, ACTION6 `8,667`, resets `288`
- EXP-003D score: `0.4809739507291212`, levels `6 / 183`, ACTION6 `7,876`, resets `304`

EXP-003D reduced ACTION6 by about `9.1%`, but score and levels regressed. The throttle fired only on `bad_noop_rate`, which likely suppressed useful exploration too early.

EXP-003E is a controlled softening of EXP-003D.

K-12 version: yesterday we told the robot, “stop pressing the risky button if it often does nothing.” That was too strict. Now we only slow it down when the button is doing nothing *a lot*.

## Baseline context

Current public baseline:

- EXP-003B public score: `0.12`
- EXP-003B local score: `0.48491096178440257`
- EXP-003B local levels: `6 / 183`

Latest diagnostics:

- EXP-003C local score: `0.481950521305291`, levels `7 / 183`
- EXP-003D local score: `0.4809739507291212`, levels `6 / 183`

## Hypothesis

Raising the ACTION6 no-op throttle threshold from `0.45` to `0.70` may preserve useful ACTION6 exploration while still reducing only the most clearly harmful repeated ACTION6 behavior.

## Implemented change vs EXP-003D

Keep EXP-003D diagnostics and throttle mechanism, but change:

```text
ACTION6_BAD_NOOP_RATE = 0.70
```

Keep:

```text
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
GAME_OVER_PENALTY = 30.0
MAX_CONSECUTIVE_SAME_PRIOR = 2
ACTION6_BAD_GAME_OVER_RATE = 0.04
ACTION6_THROTTLE_KEEP_PROB = 0.15
```

## Runtime fix

Initial EXP-003E was implemented as a wrapper over EXP-003D and failed in Kaggle when only the EXP-003E file was available:

```text
FileNotFoundError: EXP-003D source file was not found
```

EXP-003E is now standalone and Kaggle-safe. It no longer requires copying `exp003d_policy_action_diagnostics_action6_throttle.py` alongside it.

Standalone source:

```text
notebooks/01_exploration/exp003e_soft_action6_throttle.py
```

Fix commit:

```text
f3e24453d54f5729eb3a8da1043ae2a1514ae2a3 — notebooks: make EXP-003E standalone Kaggle-safe
```

## Validation gate

Do not submit EXP-003E unless one of these is true:

1. local score beats EXP-003B `0.48491096178440257`; or
2. local score is close to EXP-003B and diagnostics clearly improve ACTION6/no-op/GAME_OVER behavior without losing levels.

Minimum artifact gate:

- `submission.parquet` created
- no runtime failure
- `exp003e_policy_action_counts.json` exported
- `exp003e_action6_throttle_counts.json` exported
- compare against EXP-003C and EXP-003D

## Fallback plan

If EXP-003E underperforms, do not submit. Keep EXP-003B as public baseline and pivot to diagnostics-only analysis or GAME_OVER-only throttling.
