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

## Visible notebook run

The visible Kaggle notebook run completed successfully in non-rerun mode.

Observed visible-run output:

```text
Local/non-rerun mode: wrote EXP005D2_NON_RERUN_PROOF.txt
Wrote /kaggle/working/submission.parquet dummy fallback.
EXP-005D2 artifact inventory:
 - /kaggle/working/EXP005D2_NON_RERUN_PROOF.txt size=192 mode=non_rerun_visible
 - /kaggle/working/submission.parquet size=2821 mode=non_rerun_visible
```

User attached the visible-run output artifacts:

```text
/kaggle/working/EXP005D2_NON_RERUN_PROOF.txt
/kaggle/working/exp005d2_artifact_inventory.json
```

Attached proof-file content:

```text
EXP-005D2: written in visible notebook/non-rerun mode only.
If this is the only proof file exposed after scoring, Kaggle output is not exposing rerun artifacts.
time=1779641303.7233481
pid=57
```

Interpretation:

- The visible notebook run did not enter `KAGGLE_IS_COMPETITION_RERUN`.
- It correctly wrote only the non-rerun proof file and dummy `submission.parquet`.
- This is the intended pre-submission control condition.
- These files must not be confused with scoring-time submission artifacts.

## Submission status

User reported:

```text
The notebook ran. Submitting for scoring.
```

Then user confirmed:

```text
Submitted for scoring.
```

Current EXP-005D2 state:

```text
EXP-005D2 — Scoring-Time Artifact Capture Proof
Notebook run: completed in visible/non-rerun mode
Submission: submitted for scoring
Public score: pending / not relevant to objective
Artifact validation: pending scoring-output download
```

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

If only these appear:

```text
EXP005D2_NON_RERUN_PROOF.txt
submission.parquet
```

then Kaggle output is exposing visible notebook artifacts only, and future diagnostics must use indirect score-delta, action-reasoning, or recording-based methods.

## What worked

- Created EXP-005D2 cleanly as a diagnostic-only notebook.
- Preserved separation from planner/leaderboard improvements.
- Visible notebook run produced the exact expected non-rerun proof file.
- Dummy `submission.parquet` was produced only in visible/non-rerun mode.
- Linear KAGR-22 was updated with the notebook creation, visible-run result, and validation rule.
- EXP-005D2 was submitted for scoring.

## What failed / unresolved

- We still do not know whether Kaggle exposes scoring-time artifacts.
- No scoring-run artifacts have been inspected yet.
- Public score is not the objective for EXP-005D2.
- The key unresolved question remains whether post-scoring downloadable output includes rerun-branch or agent-runtime proof files.

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

Commits:

```text
2d6b134604d6b792e442d42cf2a40c86c918e691
experiments: add EXP-005D2 artifact capture proof notebook

8c26ac5b43dd19cbd4b4abf7b0a21380d9f5e185
session notes: add EXP-005D2 artifact capture proof plan
```

Updated session note commit:

```text
<created after this edit>
session notes: update EXP-005D2 scoring submission status
```

Branch:

```text
jatalep2018/kagr-22-exp005d-deterministic-control
```

## Next session plan

1. Wait for EXP-005D2 Kaggle scoring to finish.
2. Record submission status, version, public score if shown, and runtime/output size.
3. Download post-scoring output artifacts.
4. Compare downloaded artifacts against the validation rule above.
5. If rerun proof files are exposed, resume real scoring-time diagnostics.
6. If only non-rerun proof files are exposed, stop relying on `/kaggle/working/*.json` artifacts and switch diagnostics to indirect score-delta / action-reasoning / recording-based methods.
7. Only after artifact behavior is understood, decide whether to proceed with EXP-005E.