# 2026-05-22 Session Notes — EXP-005C Regression and EXP-005D Submitted

## Session context

We started the 2026-05-22 ARC-AGI-3 session after receiving the EXP-005C public score.

Current best entering the session:

```text
EXP-005A — BFS Diagnostics + Hidden-State Hash
Version: 9
Public score: 0.17
Status: current best public baseline
```

Recent scored results:

```text
EXP-005B — Stronger Effective-Action Scan
Public score: 0.09
Result: regression versus EXP-005A

EXP-005C — Level-to-Level Transfer from EXP-005A
Version: 12
Public score: 0.10
Result: regression versus EXP-005A
```

## What was analyzed

### 1. EXP-005C result

EXP-005C succeeded as a Kaggle submission but scored only `0.10`, below the EXP-005A reference score of `0.17`.

Interpretation:

- EXP-005C did not validate level-to-level transfer as an improvement.
- It slightly improved over EXP-005B's `0.09`, but still materially regressed versus EXP-005A.
- The project should not continue to EXP-005C2 yet.

K-12 version:

```text
EXP-005A lets the robot solve each level carefully.
EXP-005C tried to reuse old answers on new levels.
That shortcut was not reliable, so the robot did worse.
```

### 2. EXP-005C artifacts

The uploaded EXP-005C JSON/log artifacts were confirmed to be placeholder-only local/non-rerun artifacts.

They indicate:

```text
KAGGLE_IS_COMPETITION_RERUN was not set
main.py --agent myagent did not run in visible notebook mode
submission.parquet was a dummy fallback
```

Important interpretation:

- These files are not real scoring-time BFS/transfer diagnostics.
- The real validation signal is the public Kaggle score: `0.10`.

## Decision

Given the last two planner extensions both regressed:

```text
EXP-005B: broad action scan likely increased BFS branching too much.
EXP-005C: level transfer likely added fragility or overhead.
```

We decided to create a control experiment instead of adding another feature.

Next experiment:

```text
EXP-005D — Deterministic EXP-005A Replay Control
```

Goal:

```text
Test whether EXP-005A's 0.17 result is reproducible when wall-clock stochastic seeding is removed.
```

## What was done

### 1. Linear issue created

Created:

```text
KAGR-22 — 2026-05-22 ARC-AGI-3 session: EXP-005C regression and EXP-005D deterministic control
```

Status:

```text
In Progress
```

### 2. Git branch created

Requested branch name was very long and was blocked by the GitHub connector safety layer.

Created working branch:

```text
jatalep2018/kagr-22-exp005d-deterministic-control
```

### 3. EXP-005D notebook created

Created:

```text
notebooks/01_exploration/exp005d_deterministic_exp005a_control.ipynb
```

Commit:

```text
66c0214f1feacf6dfe23ef41da30b46ddc9c23ff
experiments: add EXP-005D deterministic EXP-005A control notebook
```

EXP-005D changes versus EXP-005A:

- Preserves source-BFS backbone.
- Preserves hidden scalar probing.
- Preserves frame + hidden-field hashing.
- Preserves EXP-005A simple stride-2 effective-action scan.
- Does not include EXP-005B broad scan.
- Does not include EXP-005C transfer.
- Replaces wall-clock seeding with deterministic MD5-based game/level seeds.
- Keeps fallback behavior semantically similar but deterministic.
- Adds EXP-005D artifact paths:
  - `/kaggle/working/exp005d_bfs_events.jsonl`
  - `/kaggle/working/exp005d_run_summary.json`
- Adds non-rerun placeholder artifact creation clearly marked `placeholder_only`.
- Adds tracker row draft.

### 4. EXP-005D submitted to Kaggle

User confirmed EXP-005D was submitted for scoring.

Current status:

```text
EXP-005D: submitted for scoring
Public score: pending
```

## What worked

- EXP-005C score was recorded and interpreted correctly as a regression.
- We avoided overreacting with more feature stacking.
- We created a clean deterministic control notebook from EXP-005A.
- The notebook was committed to a separate branch.
- The experiment was submitted for scoring.

## What failed / unresolved

- EXP-005C failed to improve over EXP-005A.
- Real scoring-time artifacts for EXP-005C were not available.
- EXP-005D public score is still pending.
- The exact long branch name requested could not be created through the connector; a shorter namespaced branch was used.

## Current best score/result

```text
Current best public score: 0.17
Experiment: EXP-005A — BFS Diagnostics + Hidden-State Hash
Version: 9
Status: current best public baseline
```

Pending:

```text
EXP-005D — Deterministic EXP-005A Replay Control
Submitted for scoring
Score pending
```

## Files changed this session

Created:

```text
notebooks/01_exploration/exp005d_deterministic_exp005a_control.ipynb
session_notes/2026-05-22_session_exp005c_regression_exp005d_submitted.md
```

Commits:

```text
66c0214f1feacf6dfe23ef41da30b46ddc9c23ff
```

This session note is committed separately with this file.

## Next session plan

### Step 1 — collect EXP-005D result

Record:

- Public score.
- Kaggle version.
- Succeeded or error.
- Runtime.
- Output size.
- Whether any real scoring-time diagnostics are available.

### Step 2 — decision rule

```text
If EXP-005D ≈ 0.17:
    EXP-005A result is stable enough. Use deterministic EXP-005D as the clean baseline and plan gated EXP-005E.

If EXP-005D < 0.17:
    EXP-005A score may depend on stochastic fallback. Investigate fallback stability before planner feature work.

If EXP-005D > 0.17:
    Deterministic seeding helped. Promote EXP-005D as the new baseline.
```

### Step 3 — possible next experiment

Likely next candidate if EXP-005D is stable:

```text
EXP-005E — gated effective-action scan from deterministic EXP-005A
```

Do not continue EXP-005C2 until transfer diagnostics prove that transfer reliably helps.

## Strategic principle

Protect the current best baseline. Use controlled experiments to isolate one change at a time. Do not claim improvement until validated by a public Kaggle score or reproducible local/log evidence.
