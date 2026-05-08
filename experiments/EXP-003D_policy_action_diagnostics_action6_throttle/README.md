# EXP-003D — Policy-Action Diagnostics and Local ACTION6 Throttle

## Purpose

EXP-003C was a near-tie with EXP-003B on local score and improved levels from `6 / 183` to `7 / 183`, but artifact analysis showed the intended safety target did not work:

- EXP-003B ACTION6: `8,613`
- EXP-003C ACTION6: `8,667`
- EXP-003B prior actions: `1,411`
- EXP-003C prior actions: `416`

EXP-003C reduced prior usage but did not reduce ACTION6 usage. Therefore the repeated ACTION6 problem is mostly coming from fallback/random/action-space behavior, not only from the progress prior.

EXP-003D is a diagnostic-first refinement, not an immediate Kaggle candidate.

K-12 version: ACTION6 is a risky button. Sometimes it opens a door, but many times it crashes the game or does nothing. We should not ban it. We should learn when it is dangerous in the current game and temporarily use it less.

## Baseline context

Current public baseline:

- EXP-003B public score: `0.12`
- EXP-003B local score: `0.48491096178440257`
- EXP-003B local levels: `6 / 183`

Latest local near-tie:

- EXP-003C local score: `0.481950521305291`
- EXP-003C local levels: `7 / 183`
- EXP-003C ACTION6: `8,667`
- EXP-003C progress prior actions: `416`

## Hypothesis

If ACTION6 is harmful in a specific game based on recent online evidence, downweighting it from fallback selection may reduce no-ops and game-over events without losing games where ACTION6 genuinely causes level progress.

## Implemented diagnostics

EXP-003D adds artifacts that EXP-003C lacked:

- `exp003d_policy_action_counts.json`
- `exp003d_policy_action_by_game.csv`
- `exp003d_action_diagnostics_by_game.csv`
- `exp003d_action6_throttle_by_game.csv`

These separate fallback ACTION6 from prior ACTION6.

## Implemented first variant

Start from EXP-003C constants:

- `PRIOR_PROB = 0.05`
- `MIN_PRIOR_OBS = 12`
- `GAME_OVER_PENALTY = 30.0`
- `MAX_CONSECUTIVE_SAME_PRIOR = 2`

Add local ACTION6 fallback throttle:

- only applies to fallback random selection;
- only after enough ACTION6 observations in the current game;
- does not ban ACTION6 globally;
- does not suppress ACTION6 if it recently produced positive `level_delta`;
- uses local no-op and game-over rates to downweight ACTION6.

## Do not change

- No public game-id hard-coding.
- No per-game seed schedule.
- No object/component targeting.
- No broad architecture rewrite.
- No Kaggle submission before artifact analysis.

## Notebook-source target

`notebooks/01_exploration/exp003d_policy_action_diagnostics_action6_throttle.py`

## Validation gate

EXP-003D is only submit-worthy if it satisfies at least one:

1. local score beats EXP-003B `0.48491096178440257`; or
2. local score is very close to EXP-003B and ACTION6/game-over/no-op diagnostics are clearly safer.

Minimum artifact gate:

- `submission.parquet` created
- no runtime failure
- policy-action counts exported
- ACTION6 throttle diagnostics exported
- compare ACTION6 count and GAME_OVER count versus EXP-003C

## Fallback plan

If EXP-003D underperforms, do not submit. Keep EXP-003B as public baseline and use EXP-003D diagnostics to design per-action/per-game risk models.
