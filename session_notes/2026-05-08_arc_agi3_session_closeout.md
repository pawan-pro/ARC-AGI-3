# 2026-05-08 ARC-AGI-3 session closeout

## Objective

Close the 2026-05-08 ARC-AGI-3 session after running and analyzing EXP-003C, EXP-003D, and EXP-003E. Preserve the current public baseline, record experiment artifacts, and define the next-session plan.

## K-12 summary

Today we tested three versions of the robot's “careful button habit.”

- EXP-003C made the progress habit rarer and safer, but ACTION6 stayed high.
- EXP-003D reduced ACTION6 a lot, but it also lost a level.
- EXP-003E made the ACTION6 brake softer. It got the level back and reduced ACTION6 somewhat, but it still did not beat the current best score.

So we keep EXP-003B as the official public baseline and treat EXP-003C/D/E as useful diagnostics.

## Starting baseline

Current confirmed public baseline at session start:

```text
EXP-003B public score: 0.12
EXP-003B local score: 0.48491096178440257
EXP-003B local levels: 6 / 183
```

EXP-003B remains the current public baseline at session close.

## Linear status

Created/used Linear project:

- `ARC-AGI-3 Kaggle 2026`

Session issue:

- `KAG-13 — 2026-05-08 ARC-AGI-3 session: EXP-003C refinement and baseline review`

Linear was updated throughout the session with:

- session setup
- EXP-003C runtime blocker/fix
- EXP-003C local result and artifact analysis
- EXP-003D implementation and result analysis
- EXP-003E implementation and wrapper failure fix
- EXP-003E closeout result

## EXP-003C result

Design:

- Lowered progress prior from `0.10` to `0.05`.
- Raised `MIN_PRIOR_OBS` from `8` to `12`.
- Strengthened `GAME_OVER` penalty.
- Added prior same-action cap.
- Added repeated ACTION6 prior penalty.

Result:

```text
EXP-003C local score: 0.481950521305291
Levels: 7 / 183
Actions: 25,000
Prior actions: 416
Fallback actions: 24,296
ACTION6: 8,667
RESET: 288
```

Interpretation:

- Near-tie with EXP-003B by score.
- Improved level count from `6` to `7`.
- Reduced prior usage sharply.
- Did **not** reduce ACTION6.

Decision:

```text
Do not submit EXP-003C.
Use as diagnostic input.
```

## EXP-003D result

Design:

- Added policy-action diagnostics.
- Added per-game action diagnostics.
- Added local fallback ACTION6 throttle.
- Triggered throttle when ACTION6 local no-op or game-over evidence looked bad.

Result:

```text
EXP-003D local score: 0.4809739507291212
Levels: 6 / 183
Actions: 25,000
Prior actions: 398
ACTION6: 7,876
Fallback ACTION6: 7,844
Prior ACTION6: 32
RESET: 304
ACTION6 throttled/replaced: 822
ACTION6 throttled/but kept: 526
```

Interpretation:

- ACTION6 dropped materially versus EXP-003C.
- Confirmed ACTION6 overuse is primarily fallback-driven, not prior-driven.
- But score and levels regressed.
- Throttle was too blunt.

Decision:

```text
Do not submit EXP-003D.
Use as diagnostic input.
```

## EXP-003E result

Design:

- Softened EXP-003D ACTION6 throttle.
- Raised no-op throttle threshold from `0.45` to `0.70`.
- Kept GAME_OVER threshold and keep probability unchanged.
- Fixed wrapper failure by making EXP-003E standalone and Kaggle-safe.

Runtime fix:

The first EXP-003E implementation was a wrapper over EXP-003D and failed in Kaggle when the EXP-003D source file was not present. This was fixed by replacing EXP-003E with a standalone source file.

Fix commit:

```text
f3e24453d54f5729eb3a8da1043ae2a1514ae2a3 — notebooks: make EXP-003E standalone Kaggle-safe
```

Result:

```text
EXP-003E local score: 0.4818242866472396
Levels: 7 / 183
Actions: 25,000
Prior actions: 402
ACTION6: 8,086
Fallback ACTION6: 8,054
Prior ACTION6: 32
RESET: 303
ACTION6 throttled/replaced: 611
ACTION6 throttled/but kept: 490
```

Comparison:

```text
EXP-003B score: 0.4849109618 | levels: 6 / 183 | ACTION6: 8,613 | RESET: 295
EXP-003C score: 0.4819505213 | levels: 7 / 183 | ACTION6: 8,667 | RESET: 288
EXP-003D score: 0.4809739507 | levels: 6 / 183 | ACTION6: 7,876 | RESET: 304
EXP-003E score: 0.4818242866 | levels: 7 / 183 | ACTION6: 8,086 | RESET: 303
```

Interpretation:

- EXP-003E recovered EXP-003C's `7 / 183` levels.
- EXP-003E reduced ACTION6 by `581` versus EXP-003C, about `6.7%`.
- EXP-003E improved score versus EXP-003D, but not versus EXP-003C or EXP-003B.
- EXP-003E remains slightly below EXP-003B by score.
- EXP-003E still has more resets than EXP-003B and EXP-003C.

Decision:

```text
Do not submit EXP-003E yet.
Keep EXP-003B as the public baseline.
```

## Aggregate EXP-003E action diagnostics

EXP-003E aggregate action summary from uploaded artifacts:

```text
ACTION6 count: 8,086
ACTION6 noops: 2,545
ACTION6 GAME_OVER: 127
ACTION6 level_delta: 4
ACTION6 utility: -4037.9811
ACTION6 noop rate: 31.47%
ACTION6 GAME_OVER rate: 1.57%
```

Key interpretation:

- ACTION6 still provides the most level_delta signal among actions.
- ACTION6 remains highly damaging in aggregate.
- Any ACTION6 suppression must be game-local and progress-protected.
- No-op-only throttling is insufficient; next work should inspect game-over-triggered behavior and per-game action families.

## What worked

- EXP-003C ran after fixing the `arc_agi` install/import issue.
- EXP-003C, EXP-003D, and EXP-003E all produced valid local runs and `submission.parquet`.
- EXP-003D added useful policy-action diagnostics.
- EXP-003D confirmed fallback ACTION6 is the main source of ACTION6 overuse.
- EXP-003E softened the throttle and recovered the 7-level result while reducing ACTION6 relative to EXP-003C.
- All tested changes stayed controlled and did not overwrite EXP-003B.

## What failed / what did not improve enough

- EXP-003C did not reduce ACTION6.
- EXP-003D reduced ACTION6 but hurt score and levels.
- EXP-003E improved over EXP-003D but did not beat EXP-003B or EXP-003C.
- No experiment after EXP-003B is submit-worthy yet.
- EXP-003E initially failed because it was implemented as a wrapper and Kaggle did not have the EXP-003D source file available.
- EXP-003C artifacts were downloaded but not attached in full due to file limits. The analysis used available shared counts and summaries.

## Current best score/result

Public best:

```text
EXP-003B public score: 0.12
```

Local best by score:

```text
EXP-003B local score: 0.48491096178440257
```

Best recent level count among EXP-003C/D/E:

```text
EXP-003C: 7 / 183
EXP-003E: 7 / 183
```

Current recommendation:

```text
Do not submit EXP-003C, EXP-003D, or EXP-003E.
Keep EXP-003B as the clean public baseline.
```

## Files changed today

Experiment docs:

- `experiments/EXP-003C_progress_prior_guardrails/README.md`
- `experiments/EXP-003D_policy_action_diagnostics_action6_throttle/README.md`
- `experiments/EXP-003E_soft_action6_throttle/README.md`

Notebook/source scaffolds:

- `notebooks/01_exploration/exp003c_progress_prior_guardrails.py`
- `notebooks/01_exploration/exp003d_policy_action_diagnostics_action6_throttle.py`
- `notebooks/01_exploration/exp003e_soft_action6_throttle.py`

Tracking/session notes:

- `docs/experiment_tracker.md`
- `session_notes/2026-05-08_arc_agi3_session.md`
- `session_notes/2026-05-08_arc_agi3_exp003e_addendum.md`
- `session_notes/2026-05-08_arc_agi3_session_closeout.md`

## Important artifact-handling rule for future sessions

Every experiment result analysis must include the full artifacts needed for reproducible analysis.

Minimum required artifacts per experiment:

```text
artifact_manifest.csv
*_scorecard_summary.json
*_scorecard_by_environment.csv
*_scorecard_by_tag.csv
*_run_results.csv
*_run_details.json
*_action_counts.json
*_policy_counts.json
*_policy_action_counts.json, if available
*_effect_summary_by_game.csv
*_action_diagnostics_by_game.csv, if available
*_action_prior_by_game.json, if available
*_action6_throttle_counts.json, if applicable
*_action6_throttle_by_game.csv, if applicable
```

Standing workflow rule:

```text
Before final analysis of any experiment, confirm that the user has downloaded and attached the artifact CSV/JSON files.
If the artifacts are missing, explicitly remind the user to download and attach them before drawing final conclusions.
```

For today's session:

- EXP-003E artifacts were attached and analyzed.
- EXP-003C artifacts were downloaded by the user but could not be fully shared due to file limits. Next session should attach any missing EXP-003C artifacts if deeper comparison is needed.

## Next session plan

P0 — Baseline protection:

- Keep EXP-003B as public baseline.
- Do not submit EXP-003C/D/E unless there is a specific public validation reason.

P1 — Diagnostics:

- Build a small offline comparison notebook to compare EXP-003C, EXP-003D, and EXP-003E artifacts side-by-side.
- Prioritize per-game analysis where ACTION6 was throttled/replaced.
- Identify whether lost/kept levels correlate with ACTION6 throttling, resets, or specific game families.

P2 — Next controlled experiment candidate:

- Try GAME_OVER-only ACTION6 throttle, not no-op throttle.
- Alternative: keep diagnostics only and remove active throttle while learning per-game action risk scores.

Candidate EXP-003F:

```text
Keep EXP-003E diagnostics.
Disable no-op-based ACTION6 throttle.
Throttle ACTION6 only if local ACTION6 GAME_OVER rate exceeds threshold and no recent level_delta occurred.
```

P3 — Research direction:

- Move from global action counts to game-family/action-space models.
- Treat ACTION6 as useful but dangerous, not as bad globally.
- Continue using controlled ablations with full artifacts attached.

## Session closeout decision

```text
Session complete.
No Kaggle submission from EXP-003C/D/E.
Current public baseline remains EXP-003B at 0.12.
Next session should start with artifact comparison and optionally EXP-003F GAME_OVER-only throttle.
```
