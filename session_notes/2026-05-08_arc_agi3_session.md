# 2026-05-08 ARC-AGI-3 session — EXP-003C / EXP-003D

## Objective

Start the 2026-05-08 ARC-AGI-3 work session from the latest validated repo/session state and Linear tracking state.

Primary goals:

1. Prepare and run EXP-003C as a controlled refinement of EXP-003B.
2. Analyze EXP-003C artifacts.
3. Create EXP-003D as a diagnostic-first refinement after EXP-003C showed ACTION6 was not fixed.

## K-12 summary

Our robot improved from random button pressing to a small progress-aware habit. That habit raised the real Kaggle score from `0.11` to `0.12`, but it may be pressing one helpful-looking button too often.

EXP-003C made the habit more careful and scored almost the same, but it did not reduce the risky ACTION6 button. EXP-003D now adds better counters and a local rule to use ACTION6 less only when it looks harmful in the current game.

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

## Linear work

Created Linear project:

- `ARC-AGI-3 Kaggle 2026`

Created Linear issue:

- `KAG-13 — 2026-05-08 ARC-AGI-3 session: EXP-003C refinement and baseline review`
- Status: In Progress
- Priority: High
- Due date: 2026-05-08

Added comments to KAG-13 for:

- EXP-003C setup
- `arc_agi` import blocker/fix
- EXP-003C local run result
- EXP-003C artifact analysis
- EXP-003D implementation handoff

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

## EXP-003C local result

Run completed successfully after the package fix.

```text
EXP-003C local score: 0.481950521305291
Levels completed: 7 / 183
Actions: 25,000
Environments completed: 0 / 25
submission.parquet: created
```

Comparison to EXP-003B:

```text
EXP-003B local score: 0.48491096178440257
EXP-003B levels: 6 / 183

EXP-003C local score: 0.481950521305291
EXP-003C levels: 7 / 183
```

Score delta:

```text
-0.00296044047911155, about -0.61%
```

## EXP-003C artifact analysis

EXP-003C policy counts:

```json
{
  "exp001_random_visible_pixel_fallback": 24296,
  "progress_prior_guardrailed": 416,
  "reset": 288
}
```

EXP-003C action counts:

```json
{
  "ACTION1": 3007,
  "ACTION2": 3032,
  "ACTION3": 3298,
  "ACTION4": 3345,
  "ACTION5": 1697,
  "ACTION6": 8667,
  "ACTION7": 1666,
  "RESET": 288
}
```

Key comparison:

```text
EXP-003B prior actions: 1,411
EXP-003C prior actions: 416
Delta: -995, about -70.5%

EXP-003B ACTION6: 8,613
EXP-003C ACTION6: 8,667
Delta: +54

EXP-003B RESET: 295
EXP-003C RESET: 288
Delta: -7
```

Aggregate ACTION6 diagnostics from EXP-003C:

```text
ACTION6 count: 8,667
ACTION6 noops: 3,005
ACTION6 game_over: 120
ACTION6 level_delta: 4
ACTION6 utility: -3968.589849
```

Interpretation:

- EXP-003C reduced progress-prior usage substantially.
- EXP-003C did not reduce ACTION6.
- ACTION6 is both useful and harmful: it produced the most level deltas but also the most no-ops and GAME_OVER events.
- Therefore ACTION6 should not be globally banned; it needs local/game-specific throttling.

Gate decision:

- Do not submit EXP-003C yet.
- Keep EXP-003B as public baseline.
- Use EXP-003C as a diagnostic near-tie ablation.

## EXP-003D design

EXP-003D is diagnostic-first, not an immediate Kaggle candidate.

Created:

- `experiments/EXP-003D_policy_action_diagnostics_action6_throttle/README.md`
- `notebooks/01_exploration/exp003d_policy_action_diagnostics_action6_throttle.py`

EXP-003D adds:

1. `policy_action_counts` so we can separate fallback ACTION6 from prior ACTION6.
2. Per-game action diagnostics:
   - count
   - no-op rate
   - game-over rate
   - level_delta
   - utility per action
3. ACTION6 throttle diagnostics:
   - throttle reason
   - replacements
   - kept-after-throttle counts
4. Local fallback ACTION6 throttle:
   - applies only to fallback random action selection;
   - only after enough local ACTION6 observations;
   - does not ban ACTION6 globally;
   - does not suppress ACTION6 if recent ACTION6 produced level progress;
   - downweights ACTION6 when no-op or GAME_OVER evidence is locally bad.

Implemented constants:

```text
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
GAME_OVER_PENALTY = 30.0
MAX_CONSECUTIVE_SAME_PRIOR = 2
ACTION6_MIN_OBS_FOR_THROTTLE = 30
ACTION6_BAD_NOOP_RATE = 0.45
ACTION6_BAD_GAME_OVER_RATE = 0.04
ACTION6_RECENT_WINDOW = 40
ACTION6_RECENT_LEVEL_DELTA_PROTECT = 1
ACTION6_THROTTLE_KEEP_PROB = 0.15
```

Expected EXP-003D artifacts:

- `exp003d_action_counts.json`
- `exp003d_policy_counts.json`
- `exp003d_policy_action_counts.json`
- `exp003d_action6_throttle_counts.json`
- `exp003d_policy_action_by_game.csv`
- `exp003d_action_diagnostics_by_game.csv`
- `exp003d_action6_throttle_by_game.csv`
- `exp003d_effect_summary_by_game.csv`
- `exp003d_scorecard_summary.json`

## Validation gate

Submit EXP-003D only if one of these is true:

- local score beats EXP-003B local score `0.48491096178440257`; or
- local score is close to EXP-003B and logs show clearly safer ACTION6/no-op/GAME_OVER behavior.

Minimum mechanics gate:

- `submission.parquet` created
- no runtime failure
- policy-action counts exported
- ACTION6 throttle diagnostics exported
- no major collapse below EXP-001 unless explicitly recorded as a failed ablation

## What worked

- Repo and session notes were inspected.
- Linear had no existing ARC project, so a dedicated ARC-AGI-3 project and issue were created.
- EXP-003C was documented as a controlled next experiment.
- EXP-003C runtime import blocker was fixed with self-install logic.
- EXP-003C ran successfully and produced a near-tie local result.
- EXP-003C artifact analysis found the real failure mode: prior usage dropped, but ACTION6 remained high.
- EXP-003D was created to separate fallback ACTION6 from prior ACTION6 and test local ACTION6 throttling.

## What failed / constraints

- Initial pulled EXP-003C scaffold failed at `import arc_agi` because package install was not executed.
- EXP-003C did not reduce ACTION6 usage.
- EXP-003C was not submitted to Kaggle.
- EXP-003D has not yet been locally run.
- No Kaggle submission was made today so far.
- Linear project icon creation with emoji failed, so the project was created without a custom icon.

## Current best score/result

- Current public best: EXP-003B public score `0.12`.
- Current local best by score: EXP-003B local score `0.48491096178440257`.
- Current near-tie diagnostic: EXP-003C local score `0.481950521305291`, levels `7 / 183`.

## Files changed

- `experiments/EXP-003C_progress_prior_guardrails/README.md`
- `experiments/EXP-003D_policy_action_diagnostics_action6_throttle/README.md`
- `docs/experiment_tracker.md`
- `session_notes/2026-05-08_arc_agi3_session.md`
- `notebooks/01_exploration/exp003c_progress_prior_guardrails.py`
- `notebooks/01_exploration/exp003d_policy_action_diagnostics_action6_throttle.py`

## Commit highlights

- `c962d82ffe2aafd4a948d3907c32543959a30541` — `notebooks: make EXP-003C self-install ARC packages`
- `78c1c27358c129bdebb15a0c38b4739837c842d3` — `session_notes: record EXP-003C arc_agi import fix`
- `7960b052f8ab9ce1bd9afe76014b85579e8ca9ea` — `experiments: add EXP-003D diagnostics README`
- `8b738a845ba8a0ee0b30077512dd50442b797ee6` — `notebooks: add EXP-003D policy-action diagnostics and ACTION6 throttle`
- `303c06942a58998bed97c2be2022c12a9efba8c5` — `experiments: record EXP-003C result and EXP-003D scaffold`

## Next step

Run:

```text
notebooks/01_exploration/exp003d_policy_action_diagnostics_action6_throttle.py
```

Then inspect:

```text
/kaggle/working/exp003d_artifacts/exp003d_scorecard_summary.json
/kaggle/working/exp003d_artifacts/exp003d_action_counts.json
/kaggle/working/exp003d_artifacts/exp003d_policy_counts.json
/kaggle/working/exp003d_artifacts/exp003d_policy_action_counts.json
/kaggle/working/exp003d_artifacts/exp003d_action6_throttle_counts.json
/kaggle/working/exp003d_artifacts/exp003d_action_diagnostics_by_game.csv
```

Compare against EXP-003C:

```text
EXP-003C score: 0.481950521305291
EXP-003C levels: 7 / 183
EXP-003C ACTION6: 8,667
EXP-003C ACTION6 game_over: 120
EXP-003C ACTION6 noops: 3,005
EXP-003C resets: 288
```

## Fallback plan

If EXP-003D underperforms:

- keep EXP-003B as public baseline,
- do not submit EXP-003D,
- use EXP-003D diagnostics to build a per-game action-risk model,
- avoid broad heuristic rewrites.
