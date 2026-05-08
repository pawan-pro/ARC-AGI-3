# EXP-003C — Progress Prior Guardrails

## Purpose

EXP-003B is the current confirmed public baseline with Kaggle public score `0.12`. It showed that a small online progress-weighted action prior can improve beyond EXP-001, but it also shifted the action distribution heavily toward `ACTION6` and the large local gain only partially generalized.

EXP-003C is a controlled refinement of EXP-003B, not a rewrite.

K-12 version: the robot learned a small habit that helped a little. Now we are making that habit more careful so it does not keep pressing the same button when it is risky.

## Baseline to beat

Current public baseline:

- EXP-003B public score: `0.12`
- EXP-003B local score: `0.48491096178440257`
- EXP-003B local levels: `6 / 183`
- notebook: `notebooks/01_exploration/exp003b_progress_weighted_action_prior.ipynb`

Safety fallback:

- EXP-001 public score: `0.11`
- EXP-001 local score: `0.21238458620043624`
- EXP-003A confirms instrumentation can reproduce EXP-001 exactly while logging effects.

## Hypothesis

A lower and safer progress-prior probability may preserve EXP-003B's useful online adaptation while reducing over-commitment to noisy action utilities and repeated `ACTION6` loops.

## Planned controlled changes

Start from EXP-003B and change only the prior-selection guardrails:

1. Test lower prior probabilities: `0.03`, `0.05`, and optionally `0.08`.
2. Strengthen `GAME_OVER` penalty.
3. Add a cap on consecutive same-action prior choices.
4. Reduce repeated `ACTION6` loops.
5. Require stronger evidence before prior selection.
6. Preserve EXP-001 fallback behavior.

## Do not change in EXP-003C

- Do not add public game-id hard-coding.
- Do not add per-game seed schedules.
- Do not add object/component targeting.
- Do not rewrite the agent architecture.
- Do not claim improvement before local or Kaggle validation.

## Notebook target

`notebooks/01_exploration/exp003c_progress_prior_guardrails.ipynb`

## Validation gate before Kaggle submission

Submit only if one of these is true:

- local score beats EXP-003B local score `0.48491096178440257`, or
- local score is close to EXP-003B while the policy is clearly safer/more robust from logs.

Minimum mechanics gate:

- `submission.parquet` created
- no runtime failure
- action/policy counts exported
- scorecard artifacts exported
- no major collapse below EXP-001 unless explicitly kept as a failed ablation

## Expected artifacts

- `exp003c_scorecard_summary.json`
- `exp003c_scorecard_by_environment.csv`
- `exp003c_scorecard_by_tag.csv`
- `exp003c_run_results.csv`
- `exp003c_run_details.json`
- `exp003c_action_counts.json`
- `exp003c_policy_counts.json`
- `exp003c_action_prior_by_game.json`
- `exp003c_effect_summary_by_game.csv`

## Fallback plan

If EXP-003C underperforms, keep EXP-003B as the public baseline and use EXP-003A/EXP-003B logs to build an offline analyzer for actual `level_delta` events before adding more policy logic.
