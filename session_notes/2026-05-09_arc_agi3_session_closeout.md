# 2026-05-09 ARC-AGI-3 session closeout

## Objective

Close the 2026-05-09 ARC-AGI-3 session after ingesting EXP-003C artifacts, implementing/running EXP-003F, analyzing the 5000-move long-horizon run, and recording the Kaggle submission status.

## K-12 summary

Today we learned that giving the robot more time helps it find more progress, but this does not yet mean it is smarter. The 5000-move run reached more levels, but it used five times as many actions. We also submitted EXP-003F Version 6 to Kaggle as an analysis probe, but the result is not available yet.

## Current public baseline before new submission result

```text
EXP-003B public score: 0.12
EXP-003B local score: 0.48491096178440257
EXP-003B local levels: 6 / 183
```

EXP-003B remains the current confirmed public baseline until the new EXP-003F Version 6 submission result is known.

## Linear issue

Active Linear issue:

```text
KAG-14 — 2026-05-09 ARC-AGI-3 session: artifact comparison and EXP-003F planning
```

## Work completed today

### 1. EXP-003C artifacts ingested

The missing EXP-003C artifacts were attached and reviewed.

Confirmed EXP-003C result:

```text
EXP-003C local score: 0.481950521305291
Levels: 7 / 183
Actions: 25,000
Fallback actions: 24,296
Progress-prior actions: 416
RESET: 288
ACTION6: 8,667
```

Interpretation:

- EXP-003C is a near-tie diagnostic, not a submission candidate.
- It improves level count versus EXP-003B but does not beat EXP-003B by local score.
- ACTION6 remains dominant and risky.
- ACTION6 cannot be globally banned because it produced useful level deltas.

Artifact review note created:

```text
docs/analysis/2026-05-09_exp003c_artifact_review.md
```

### 2. EXP-003F implemented

EXP-003F was created as a GAME_OVER-only ACTION6 throttle:

```text
notebooks/01_exploration/exp003f_gameover_only_action6_throttle.py
experiments/EXP-003F_gameover_only_action6_throttle/README.md
```

Controlled change:

```text
Keep EXP-003E diagnostics.
Disable no-op-based ACTION6 throttle.
Throttle ACTION6 only when local ACTION6 GAME_OVER rate is bad
and no current/recent ACTION6 level_delta protects it.
ACTION6_THROTTLE_KEEP_PROB = 0.50
```

### 3. EXP-003F 1000-move result analyzed

EXP-003F at 1000 moves reproduced EXP-003C exactly.

```text
EXP-003F local score: 0.481950521305291
Levels: 7 / 183
Actions: 25,000
ACTION6: 8,667
RESET: 288
ACTION6 throttle counts: {}
```

Interpretation:

- EXP-003F ran successfully.
- It produced artifacts and `submission.parquet`.
- But the GAME_OVER-only throttle never fired.
- This was a null diagnostic result, not a leaderboard candidate.

Review note created:

```text
docs/analysis/2026-05-09_exp003f_null_result_review.md
```

### 4. EXP-003F 5000-move long-horizon run analyzed

The user increased `MAX_MOVES` from `1000` to `5000` and attached the full artifact bundle.

Confirmed result:

```text
EXP-003F_5000 local score: 0.5105754965839018
Levels: 9 / 183
Actions: 125,000
Environments completed: 0 / 25
```

Counts:

```text
ACTION1: 15,183
ACTION2: 15,009
ACTION3: 15,919
ACTION4: 16,978
ACTION5: 8,478
ACTION6: 43,534
ACTION7: 8,367
RESET: 1,532
```

Policy counts:

```text
fallback: 121,845
progress_prior_guardrailed: 1,623
reset: 1,532
```

Policy-action counts:

```text
fallback ACTION6: 43,496
prior ACTION6: 38
```

Throttle counts:

```json
{}
```

Interpretation:

- This is the best local raw score seen so far.
- It reaches `9 / 183` levels.
- It uses 5x the standard action budget.
- The throttle still never fired.
- The improvement is from longer stochastic exploration, not from smarter policy logic.
- It should be treated as a long-horizon diagnostic, not as a clean baseline replacement.

Review note updated with full artifacts:

```text
docs/analysis/2026-05-09_exp003f_5000_move_review.md
```

### 5. Kaggle submission status

The user attempted/submitted:

```text
EXP-003F — progress-weighted action prior — Version 6
```

Kaggle UI status from screenshot:

```text
Notebook Running
Submitted for scoring / rerun in progress
Daily submission allowance used: 0 submissions remaining today
Reset expected in about 3 hours from screenshot time
```

Important uncertainty:

```text
It is not yet confirmed whether Version 6 corresponds exactly to the 5000-move run.
```

This submission should be treated as an analysis probe, not as a confirmed baseline improvement, until the public score and rerun logs are available.

## What worked

- EXP-003C artifact gap was closed.
- EXP-003F was implemented as a controlled GAME_OVER-only throttle experiment.
- EXP-003F 1000-move result clarified that the GAME_OVER-only throttle was inert.
- EXP-003F 5000-move result showed that longer stochastic search can improve local raw score and level count.
- Full EXP-003F_5000 artifacts were attached and reviewed.
- Experiment tracker was updated with EXP-003F and EXP-003F_5000.
- Linear KAG-14 was updated through the session.

## What failed / limitations

- EXP-003F throttle did not fire at either 1000 or 5000 moves.
- EXP-003F 1000 did not improve over EXP-003C.
- EXP-003F_5000 used 125,000 actions, so it is not directly comparable to 25,000-action local baselines.
- The 5000-move local improvement may not translate to Kaggle because action efficiency matters.
- The public result for EXP-003F Version 6 is not available yet.
- It is not confirmed whether submitted Version 6 is exactly the 5000-move variant.

## Current best results

Confirmed public best:

```text
EXP-003B public score: 0.12
```

Confirmed local best by raw score:

```text
EXP-003F_5000 local score: 0.5105754965839018
```

Confirmed local best under 25k-action budget:

```text
EXP-003B local score: 0.48491096178440257
```

Best recent level count:

```text
EXP-003F_5000: 9 / 183
EXP-003C / EXP-003F_1000: 7 / 183
```

## Files changed today

```text
session_notes/2026-05-09_arc_agi3_session_start.md
docs/analysis/2026-05-09_exp003c_artifact_review.md
experiments/EXP-003F_gameover_only_action6_throttle/README.md
notebooks/01_exploration/exp003f_gameover_only_action6_throttle.py
docs/experiment_tracker.md
docs/analysis/2026-05-09_exp003f_null_result_review.md
session_notes/2026-05-09_arc_agi3_exp003f_result_addendum.md
docs/analysis/2026-05-09_exp003f_5000_move_review.md
session_notes/2026-05-09_arc_agi3_session_closeout.md
```

## Key commits

```text
570d042e — session_notes: start 2026-05-09 ARC-AGI-3 artifact comparison session
dbfa40ad — analysis: add EXP-003C artifact review
e349dfd6 — experiments: add EXP-003F GAME_OVER-only throttle README
3a6eec57 — notebooks: add EXP-003F GAME_OVER-only ACTION6 throttle
ce28be89 — experiments: record EXP-003F scaffold
a0ccb2a6 — experiments: record EXP-003F null result
7d093744 — analysis: add EXP-003F null-result review
c9eb935e — session_notes: add EXP-003F null-result addendum
9e43bb65 — experiments: record EXP-003F 5000-move diagnostic result
4ac4a612 — analysis: add EXP-003F 5000-move review
1cc8494f — analysis: confirm EXP-003F 5000-move review with full artifacts
```

## Next session plan

### Step 1 — Wait for Kaggle result

Check the result for:

```text
EXP-003F — progress-weighted action prior — Version 6
```

Record:

```text
public score
runtime / success status
whether Version 6 used MAX_MOVES=5000
whether output was accepted without errors
```

If the public score improves above `0.12`, update the public baseline. If it does not, keep EXP-003B.

### Step 2 — Attach Kaggle rerun logs/artifacts

Before final analysis of the Kaggle submission, attach or record:

```text
Kaggle public score screenshot or log
notebook version details
run logs
submission output confirmation
any generated artifacts from the rerun if accessible
```

### Step 3 — Decide on budget sweep

If Version 6 performs well or is close, create a budget sweep:

```text
EXP-003H_budget_sweep
MAX_MOVES = 1000, 1500, 2000, 3000, 5000
Base behavior: EXP-003C / EXP-003F fallback + sparse prior
Goal: optimize score/action-efficiency tradeoff
```

### Step 4 — Do not create another blind throttle yet

No immediate EXP-003G/003H policy rewrite until we compare:

```text
raw score
levels
actions
resets
ACTION6 level_delta
ACTION6 GAME_OVER
score per 1,000 actions
levels per 1,000 actions
```

## Standing artifact rule

Every experiment analysis must include the CSV/JSON artifacts where available. If artifacts are missing, ask the user to download and attach them before final conclusions.

## Session closeout decision

```text
Session closed.
EXP-003F Version 6 has been submitted/running as an analysis probe.
No confirmed new public baseline yet.
Current confirmed public baseline remains EXP-003B at 0.12.
Next session starts with Kaggle Version 6 result analysis.
```
