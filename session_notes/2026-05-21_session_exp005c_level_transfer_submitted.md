# 2026-05-21 Session Notes — EXP-005B Regression and EXP-005C Submitted

## Session context

We started the 2026-05-21 ARC-AGI-3 session from the following validated state:

```text
Current best public score: 0.17
Current best experiment: EXP-005A — BFS Diagnostics + Hidden-State Hash
Version: 9
```

EXP-005B had been submitted earlier as a planner-side test of stronger effective-action scanning.

## What was analyzed

### 1. EXP-005B result

User provided the EXP-005B public score:

```text
EXP-005B — Stronger Effective-Action Scan
Public Score: 0.09
Best Score: 0.17 V9
```

Interpretation:

- EXP-005B is a valid scored submission, but it regressed from EXP-005A's `0.17` to `0.09`.
- The stronger/broader action scan did not improve public performance.
- Likely failure mode: too many click/action candidates increased BFS branching and consumed search budget.

Score ladder after EXP-005B:

```text
EXP-005:  0.08
EXP-005A: 0.17  <-- current best
EXP-005B: 0.09  <-- regression
```

K-12 version:

```text
EXP-005A gave the robot a manageable number of doors to try.
EXP-005B gave it many more doors.
Some extra doors might be useful, but the robot spent too much time opening extra doors and ran out of search time.
```

Conclusion:

```text
Do not continue adding more action candidates blindly.
```

### 2. Decision to proceed with EXP-005C

Given EXP-005B's regression, we decided to return to the proven EXP-005A backbone and add a different public-planner advantage:

```text
EXP-005C — level-to-level solution transfer from EXP-005A
```

Reasoning:

- EXP-005A is the current proven planner baseline at `0.17`.
- EXP-005B showed broad scan expansion can hurt by increasing BFS branching.
- Level transfer can reuse previously solved action sequences without broadening the action space.

## What was implemented

### EXP-005C notebook created

Created:

```text
notebooks/01_exploration/exp005c_level_transfer_from_exp005a.ipynb
```

Commit:

```text
902ad238a29df6c175b6d23b95b1252c7d02d98b
experiments: add EXP-005C level transfer notebook
```

EXP-005C scope:

- Uses EXP-005A-style source-BFS backbone.
- Keeps hidden scalar probing and frame+hidden-field state hashes.
- Keeps simpler EXP-005A-style effective-action scan, not EXP-005B's broader scan.
- Adds previous-level solution transfer:
  1. Direct replay of previous level solution.
  2. Object-relative click offset transfer if direct replay fails.
- Saves transfer/BFS diagnostics.

Expected artifacts:

```text
/kaggle/working/exp005c_bfs_events.jsonl
/kaggle/working/exp005c_run_summary.json
```

Key transfer diagnostics:

```text
transfer.direct_status
transfer.offset_status
transfer.dx
transfer.dy
status
solution_len
policy.bfs_or_transfer_replay
```

### EXP-005C local run and artifact check

User pulled/reran the notebook in Kaggle UI and confirmed local/non-rerun artifact creation:

```text
/kaggle/working/exp005c_bfs_events.jsonl exists: True size: 268
/kaggle/working/exp005c_run_summary.json exists: True size: 568
```

Interpretation:

- In visible Kaggle notebook mode, `KAGGLE_IS_COMPETITION_RERUN` is not set.
- Therefore `main.py --agent myagent` does not run.
- Local JSON artifacts are placeholders, not real scoring-time BFS logs.
- The placeholder files confirm output-path plumbing only.

### EXP-005C submitted

User submitted EXP-005C for scoring.

Current EXP-005C status:

```text
EXP-005C: submitted to competition
Scoring: pending
Current best remains EXP-005A / V9 = 0.17 until score returns
```

## What worked

- EXP-005B result was interpreted and documented as a planner-side regression.
- The team avoided fallback-recovery and avoided adding even more scan candidates.
- EXP-005C was created as a clean separate notebook preserving EXP-005A.
- EXP-005C local notebook run produced the expected placeholder JSON artifacts.
- EXP-005C was submitted for scoring.

## What failed / unresolved

- EXP-005B regressed to `0.09`.
- EXP-005C public score is not available yet.
- The visible EXP-005C artifacts are placeholders only; real scoring-time diagnostics still depend on the competition rerun path.
- It is not yet known whether direct replay or object-offset transfer will trigger in hidden scoring environments.

## Current best score/result

```text
Current best public score: 0.17
Experiment: EXP-005A — BFS Diagnostics + Hidden-State Hash
Version: 9
```

Pending:

```text
EXP-005C — Level-to-Level Transfer from EXP-005A
Status: submitted / scoring pending
```

## Files changed this session

Created:

```text
notebooks/01_exploration/exp005c_level_transfer_from_exp005a.ipynb
session_notes/2026-05-21_session_exp005c_level_transfer_submitted.md
```

Commits:

```text
902ad238a29df6c175b6d23b95b1252c7d02d98b
```

This session note is committed separately with this file.

## Next session plan

### Step 1 — collect EXP-005C result

Record:

- Public score.
- Version number.
- Succeeded or Kaggle Error.
- Runtime.
- Output size.
- Whether JSON artifacts are real scoring-time logs or local placeholders.

### Step 2 — compare against EXP-005A

Decision rule:

```text
If EXP-005C > 0.17:
    Level transfer helped. Continue refining transfer.

If EXP-005C ≈ 0.17:
    Transfer did not hurt. Inspect transfer diagnostics and improve triggers.

If EXP-005C < 0.17:
    Transfer may not trigger or may add overhead. Revert to EXP-005A and test transfer in a more gated way.
```

### Step 3 — possible next experiments

If EXP-005C improves:

```text
EXP-005C2 — transfer repeat multipliers and better object matching
```

If EXP-005C regresses:

```text
EXP-005B2 — ranked/gated scan from EXP-005A, not broad scan
```

Longer-term planner ladder:

```text
0.17 -> 0.20–0.25: transfer or gated scan
0.25 -> 0.32: replay validation + improved transfer
0.32 -> 0.38: sprite permutation / IDDFS / counter-A*
0.38 -> 0.45+: adaptive routing and time-budget control
```

## Strategic principle

Continue isolating planner improvements. Avoid using the known EXP-003B fallback merely to recover score; the goal is to grow the source-BFS planner toward the 0.4+ public-notebook range.
