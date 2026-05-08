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
- `notebooks/01_exploration/exp003c_progress_prior_guardrails.py`

Updated:

- `docs/experiment_tracker.md`

## EXP-003C design

EXP-003C starts from EXP-003B and modifies only the prior guardrails.

Implemented first variant:

1. Lower prior probability from `0.10` to `0.05`.
2. Raise `MIN_PRIOR_OBS` from `8` to `12`.
3. Strengthen `GAME_OVER` penalty to `30.0`.
4. Add cap on consecutive same-action prior choices: `MAX_CONSECUTIVE_SAME_PRIOR = 2`.
5. Add repeated `ACTION6` prior penalty: `ACTION6_EXTRA_REPEAT_PENALTY = 0.25`.
6. Require positive prior score: `MIN_PRIOR_SCORE = 0.02`.
7. Preserve EXP-001 fallback behavior.

## Runtime blocker and fix

User hit this error while running the pulled 3C notebook-source scaffold:

```text
ModuleNotFoundError: No module named 'arc_agi'
```

Root cause:

- The pulled `.py` scaffold had the Kaggle wheel install command commented as a notebook cell note.
- When run directly, the install step did not execute before `import arc_agi`.

Fix committed:

- `notebooks/01_exploration/exp003c_progress_prior_guardrails.py` now includes `ensure_arc_packages()`.
- It tries to import `arc_agi`/`arcengine` first.
- If missing, it installs `arc-agi`, `python-dotenv`, and `pyarrow` from Kaggle's local wheel directory:
  - `/kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels`
- If the wheel directory is missing, it raises a clear message to attach the ARC competition dataset / run inside Kaggle.

Fix commit:

- `c962d82ffe2aafd4a948d3907c32543959a30541` — `notebooks: make EXP-003C self-install ARC packages`

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
- Experiment tracker now records EXP-003C as implemented scaffold and not yet validated.
- Runtime import blocker was fixed with self-install logic.

## What failed / constraints

- Initial pulled EXP-003C scaffold failed at `import arc_agi` because package install was not executed.
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
- `notebooks/01_exploration/exp003c_progress_prior_guardrails.py`

## Next session plan

1. Pull latest `main` or copy commit `c962d82f` version of `exp003c_progress_prior_guardrails.py`.
2. Run the updated scaffold in Kaggle.
3. Confirm the self-install block prints the local wheel install only if needed.
4. Compare local score, levels, action counts, prior counts, reset counts, and repeated ACTION6 frequency against EXP-003B.
5. Submit to Kaggle only if local validation passes the gate.

## Fallback plan

If EXP-003C underperforms:

- keep EXP-003B as public baseline,
- return to EXP-003A/EXP-003B logs,
- build an offline analyzer for true `level_delta` events,
- design priors from actual progress events rather than weak visual changes.
