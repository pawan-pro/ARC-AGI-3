# 2026-05-24 Session Notes — EXP-005D2 Scoring-Time Artifact Capture Proof

## Session context

We confirmed that recent EXP-005B/EXP-005C/EXP-005D downloadable artifacts were repeatedly placeholder-only files from visible/non-rerun Kaggle notebook mode.

Latest validated public scores:

```text
EXP-005A / V9:   0.17  <-- current best
EXP-005B:        0.09
EXP-005C / V12:  0.10
EXP-005D / V13:  0.10
EXP-005D / V14:  0.10
```

The EXP-005D V14 artifact upload still showed:

```text
mode: non_rerun_notebook_mode
status: placeholder_only
reason: KAGGLE_IS_COMPETITION_RERUN was not set, so main.py --agent myagent did not run.
```

Therefore we still do not have real scoring-time BFS/fallback attribution logs.

## What was done

Created a new diagnostic-only notebook:

```text
notebooks/01_exploration/exp005d2_scoring_artifact_capture_proof.ipynb
```

Commit:

```text
2d6b134604d6b792e442d42cf2a40c86c918e691
experiments: add EXP-005D2 artifact capture proof notebook
```

Purpose:

```text
Prove whether files written inside KAGGLE_IS_COMPETITION_RERUN and inside MyAgent during main.py --agent myagent are exposed in Kaggle output after scoring.
```

This is not a leaderboard-improvement experiment and does not change planner logic.

## Expected proof artifacts

Visible/non-rerun mode should create:

```text
/kaggle/working/EXP005D2_NON_RERUN_PROOF.txt
/kaggle/working/submission.parquet
/kaggle/working/exp005d2_artifact_inventory.json
```

Competition rerun branch should create:

```text
/kaggle/working/EXP005D2_RERUN_BRANCH_PROOF.txt
/kaggle/working/exp005d2_rerun_branch_proof.json
```

MyAgent scoring-time runtime should create:

```text
/kaggle/working/EXP005D2_AGENT_INIT_PROOF.txt
/kaggle/working/exp005d2_agent_events.jsonl
/kaggle/working/exp005d2_run_summary.json
```

After `main.py --agent myagent` completes, rerun branch should create:

```text
/kaggle/working/EXP005D2_AFTER_MAIN_PROOF.txt
```

## Validation rule

After Kaggle scoring, inspect downloadable output artifacts.

If these appear:

```text
EXP005D2_RERUN_BRANCH_PROOF.txt
EXP005D2_AGENT_INIT_PROOF.txt
EXP005D2_AFTER_MAIN_PROOF.txt
exp005d2_agent_events.jsonl
exp005d2_run_summary.json
```

then scoring-time artifacts are exposed and future diagnostics can rely on `/kaggle/working` JSON files.

If only this appears:

```text
EXP005D2_NON_RERUN_PROOF.txt
```

then Kaggle output is exposing visible notebook artifacts only, and future diagnostics must use indirect score-delta or recording-based methods.

## Current best score/result

```text
Current best public score: 0.17
Experiment: EXP-005A — BFS Diagnostics + Hidden-State Hash
Version: 9
```

## Files changed

Created:

```text
notebooks/01_exploration/exp005d2_scoring_artifact_capture_proof.ipynb
session_notes/2026-05-24_session_exp005d2_artifact_capture_proof.md
```

## Next session plan

1. Pull latest GitHub branch:

```text
jatalep2018/kagr-22-exp005d-deterministic-control
```

2. Push/run the EXP-005D2 notebook on Kaggle.
3. Submit it as a code submission.
4. After scoring, download output artifacts and compare against the validation rule above.
5. Only after artifact behavior is understood, decide whether to proceed with EXP-005E or switch to indirect diagnostics.