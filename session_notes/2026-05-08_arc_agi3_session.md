# 2026-05-08 ARC-AGI-3 session — EXP-003C setup

## Objective

Start the 2026-05-08 ARC-AGI-3 work session from the latest validated repo/session state and Linear tracking state.

Primary goal: prepare EXP-003C as a controlled refinement of EXP-003B, not a broad rewrite.

## K-12 summary

Our robot improved from random button pressing to a small progress-aware habit. That habit raised the real Kaggle score from `0.11` to `0.12`, but it may be pressing one helpful-looking button too often. Today we set up the next experiment to make that habit more careful.

## Starting state

Current confirmed public baseline:

- EXP-003B public score: `0.12`
- EXP-003B local score: `0.48491096178440257`
- EXP-003B local levels: `6 / 183`
- EXP-003B notebook: `notebooks/01_exploration/exp003b_progress_weighted_action_prior.ipynb`

Previous durable fallback baseline:

- EXP-001 public score: `0.11`
- EXP-001 local score: `0.21238458620043624`
- EXP-001 local levels: `7 / 183`

Safe instrumentation scaffold:

- EXP-003A reproduced EXP-001 exactly while collecting logs.
- Use EXP-003A-style logging as the safe diagnostic base when needed.

## Linear work created

Created Linear project:

- `ARC-AGI-3 Kaggle 2026`

Created Linear issue:

- `KAG-13 — 2026-05-08 ARC-AGI-3 session: EXP-003C refinement and baseline review`
- Status: In Progress
- Priority: High
- Due date: 2026-05-08

## Repo work completed

Created:

- `experiments/EXP-003C_progress_prior_guardrails/README.md`

Updated:

- `docs/experiment_tracker.md`

## EXP-003C design

EXP-003C should start from EXP-003B and modify only the prior guardrails.

Controlled changes to test:

1. Lower prior probabilities: `0.03`, `0.05`, optionally `0.08`.
2. Stronger `GAME_OVER` penalty.
3. Cap consecutive same-action prior choices.
4. Reduce repeated `ACTION6` loops.
5. Require stronger evidence before prior selection.
6. Preserve EXP-001 fallback behavior.

## Do not change yet

- Do not add public game-id hard-coding.
- Do not add per-game seed schedules.
- Do not add object/component targeting.
- Do not rewrite the agent architecture.
- Do not submit to Kaggle before local validation.

## Validation gate

Submit EXP-003C only if one of these is true:

- local score beats EXP-003B local score `0.48491096178440257`; or
- local score is close to EXP-003B and logs show safer/more robust behavior.

Minimum mechanics gate:

- `submission.parquet` created
- no runtime failure
- action/policy counts exported
- scorecard artifacts exported
- no major collapse below EXP-001 unless explicitly recorded as a failed ablation

## What worked

- Repo and session notes were inspected.
- Linear had no existing ARC project, so a dedicated ARC-AGI-3 project and issue were created.
- EXP-003C was documented as a controlled next experiment.
- Experiment tracker now records EXP-003C as planned and not yet validated.

## What failed / constraints

- No notebook execution was performed in this ChatGPT session.
- No local score was generated yet for EXP-003C.
- No Kaggle submission was made.
- Linear project icon creation with emoji failed, so the project was created without a custom icon.

## Current best score/result

- Current public best: EXP-003B public score `0.12`.
- Current local best: EXP-003B local score `0.48491096178440257`.

## Files changed

- `experiments/EXP-003C_progress_prior_guardrails/README.md`
- `docs/experiment_tracker.md`
- `session_notes/2026-05-08_arc_agi3_session.md`

## Next session plan

1. Copy `notebooks/01_exploration/exp003b_progress_weighted_action_prior.ipynb` into `notebooks/01_exploration/exp003c_progress_prior_guardrails.ipynb`.
2. Implement one EXP-003C variant at a time.
3. First test: lower prior probability to `0.05` with same EXP-003B logic.
4. Second test: add same-action prior cap.
5. Third test: strengthen `GAME_OVER` penalty.
6. Compare local score, levels, action counts, prior counts, reset counts, and repeated ACTION6 frequency against EXP-003B.
7. Submit to Kaggle only if local validation passes the gate.

## Fallback plan

If EXP-003C underperforms:

- keep EXP-003B as public baseline,
- return to EXP-003A/EXP-003B logs,
- build an offline analyzer for true `level_delta` events,
- design priors from actual progress events rather than weak visual changes.
