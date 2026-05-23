# 2026-05-23 Session Notes — EXP-005D Attribution Diagnostic Rerun

## Session context

We started from the EXP-005D Version 13 result:

```text
EXP-005D — Deterministic EXP-005A Replay Control
Version: 13
Public score: 0.10
Current best remains: EXP-005A / V9 public score 0.17
```

Decision from the prior matrix:

```text
EXP-005D < 0.17
=> EXP-005A may depend on stochastic fallback.
=> Investigate fallback stability before adding planner features.
```

## What was changed

Updated:

```text
notebooks/01_exploration/exp005d_deterministic_exp005a_control.ipynb
```

Commit:

```text
d702bdc5d948cfcd68c16e9e0eea24a7169a8b87
experiments: add EXP-005D attribution diagnostics
```

The notebook still preserves the EXP-005A backbone:

- source-BFS,
- hidden scalar probing,
- frame plus hidden-field hashing,
- simple EXP-005A stride-2 scan,
- no EXP-005B broad scan,
- no EXP-005C transfer.

Added attribution diagnostics:

```text
source_lookup
load status
last_bfs_status
attribution
fallback_reasons
last_fallback_reason
bfs_replay_actions
fallback_actions
reset_actions
error_fallback_actions
last_level_seed
```

Purpose:

```text
Determine whether fallback is caused by source load failure, scan/no-actions, BFS timeout/exhaustion, BFS error, no solution, or replay exhaustion.
```

## Kaggle action

Pushed updated notebook to Kaggle:

```text
Kernel: jatalepawan/exp-005d-deterministic-exp-005a-replay-control
Kernel version: 15
Message/intent: EXP-005D attribution diagnostics rerun
```

Initial immediate competition submission attempt returned:

```text
400 Bad Request from CreateCodeSubmission
```

Interpretation:

- The kernel version was still running when the submit call was attempted.
- After the kernel completed, duplicate manual submit calls still returned `400 Bad Request`.
- Kaggle's submissions table nevertheless shows a pending EXP-005D code submission:

```text
Submission ref: 52960131
File: submission.parquet
Date: 2026-05-23 16:09:09 UTC
Description: Notebook EXP-005D — Deterministic EXP-005A Replay Control | Version 14
Status: PENDING
```

The latest kernel visible-output artifacts confirm the diagnostic notebook code was run:

```text
my_agent.py size: 14075 bytes
exp005d_run_summary.json includes attribution/fallback expected fields
visible run remains placeholder_only / non_rerun_notebook_mode
```

Working interpretation:

```text
Kaggle accepted the EXP-005D diagnostic notebook for scoring and reports it as pending submission ref 52960131.
Manual CLI resubmission appears to fail because a code submission is already pending or because Kaggle maps the latest run to displayed Version 14.
```

## Current status at note creation

```text
EXP-005D attribution notebook: pushed to GitHub and Kaggle as kernel version 15
Kernel run: complete
Competition submission: pending, ref 52960131
```

## Decision matrix remains

| Observation after diagnostic rerun | Decision |
|---|---|
| Real scoring logs show many `bfs_replay_actions` and low fallback | Deterministic planner works but scoring variance remains; inspect solved-level identity and time budget. |
| Logs show `source_not_found_or_load_failed` | Fix source lookup/load before planner work. |
| Logs show `no_effective_actions` | Improve scan conservatively, not broad EXP-005B-style expansion. |
| Logs show `timeout_or_exhausted` | Tune BFS depth/states/time or rank actions before adding new candidates. |
| Logs show high fallback despite successful BFS setup | Investigate fallback seed/trajectory sensitivity before EXP-005E. |

## Next step

After Kaggle completion:

1. Wait for submission ref `52960131` to finish scoring.
2. Record public score/version.
3. Download scoring-time `exp005d_bfs_events.jsonl` and `exp005d_run_summary.json` if Kaggle exposes real rerun artifacts.
4. Inspect attribution fields before choosing EXP-005E or a fallback-stability experiment.
