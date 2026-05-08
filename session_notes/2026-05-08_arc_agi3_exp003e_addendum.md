# 2026-05-08 ARC-AGI-3 session addendum — EXP-003E setup

## Objective

Create EXP-003E after EXP-003D showed that ACTION6 throttling worked mechanically but was too blunt.

## K-12 summary

The robot pressed the risky ACTION6 button less in EXP-003D, but the score got slightly worse and it solved fewer levels. So EXP-003E keeps the same counters but makes the rule softer: only slow down ACTION6 when it does nothing a lot, not just somewhat often.

## Starting point

Current public baseline remains:

- EXP-003B public score: `0.12`
- EXP-003B local score: `0.48491096178440257`
- EXP-003B local levels: `6 / 183`

Recent local diagnostics:

- EXP-003C local score: `0.481950521305291`
- EXP-003C levels: `7 / 183`
- EXP-003C ACTION6: `8,667`
- EXP-003C resets: `288`

- EXP-003D local score: `0.4809739507291212`
- EXP-003D levels: `6 / 183`
- EXP-003D ACTION6: `7,876`
- EXP-003D resets: `304`
- EXP-003D throttled/replaced ACTION6: `822`
- EXP-003D throttle reason: `bad_noop_rate`

## EXP-003D lesson

EXP-003D confirmed that ACTION6 overuse is primarily fallback-driven:

- fallback ACTION6: `7,844`
- prior ACTION6: `32`

But reducing ACTION6 too aggressively hurt level count and slightly hurt score.

Interpretation:

- ACTION6 is noisy and dangerous, but still useful.
- No-op throttling at `0.45` was too strict.
- The next ablation should soften the no-op trigger rather than remove ACTION6 entirely.

## EXP-003E implemented

Created:

- `experiments/EXP-003E_soft_action6_throttle/README.md`
- `notebooks/01_exploration/exp003e_soft_action6_throttle.py`

Tracker updated:

- `docs/experiment_tracker.md`

## EXP-003E design

EXP-003E is a controlled wrapper over EXP-003D.

It keeps:

```text
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
GAME_OVER_PENALTY = 30.0
MAX_CONSECUTIVE_SAME_PRIOR = 2
ACTION6_BAD_GAME_OVER_RATE = 0.04
ACTION6_THROTTLE_KEEP_PROB = 0.15
```

It changes only:

```text
ACTION6_BAD_NOOP_RATE = 0.70
```

This means ACTION6 is throttled for no-op behavior only when the no-op rate is extremely high, not merely moderately high.

## Implementation note

`exp003e_soft_action6_throttle.py` is a wrapper over the EXP-003D source file. It expects:

```text
notebooks/01_exploration/exp003d_policy_action_diagnostics_action6_throttle.py
```

to exist in the repo checkout. If running from Kaggle with only the EXP-003E file copied manually, copy the EXP-003D source file to `/kaggle/working/` as well.

## Validation gate

Do not submit EXP-003E before artifact analysis.

EXP-003E becomes submit-worthy only if one of these is true:

1. local score beats EXP-003B local score `0.48491096178440257`; or
2. local score is close to EXP-003B and diagnostics clearly improve ACTION6/no-op/GAME_OVER behavior without losing levels.

Minimum artifact checks:

- `submission.parquet` created
- `exp003e_scorecard_summary.json`
- `exp003e_action_counts.json`
- `exp003e_policy_counts.json`
- `exp003e_policy_action_counts.json`
- `exp003e_action6_throttle_counts.json`
- `exp003e_action_diagnostics_by_game.csv`

## Current best score/result

- Current public best: EXP-003B public score `0.12`.
- Current local best by score: EXP-003B local score `0.48491096178440257`.
- Best recent level count among these refinements: EXP-003C with `7 / 183`.

## Files changed in this addendum

- `experiments/EXP-003E_soft_action6_throttle/README.md`
- `notebooks/01_exploration/exp003e_soft_action6_throttle.py`
- `docs/experiment_tracker.md`
- `session_notes/2026-05-08_arc_agi3_exp003e_addendum.md`

## Commit highlights

- `a24a37d720343669adb77071d639018fb9269e47` — `experiments: add EXP-003E soft ACTION6 throttle README`
- `d5c91540c01dea596be4b4d26c5fdd1f135ee9a8` — `notebooks: add EXP-003E soft ACTION6 throttle wrapper`
- `4781de12028b9ad8742f88f327469a8511d10cea` — `experiments: record EXP-003D result and EXP-003E scaffold`

## Next step

Run:

```text
notebooks/01_exploration/exp003e_soft_action6_throttle.py
```

Then compare against EXP-003C and EXP-003D:

```text
EXP-003C score: 0.481950521305291 | levels: 7 / 183 | ACTION6: 8,667 | resets: 288
EXP-003D score: 0.4809739507291212 | levels: 6 / 183 | ACTION6: 7,876 | resets: 304
```

## Fallback plan

If EXP-003E underperforms:

- do not submit EXP-003E;
- keep EXP-003B as public baseline;
- try GAME_OVER-only throttling or diagnostics-only analysis;
- avoid broad heuristic rewrites.
