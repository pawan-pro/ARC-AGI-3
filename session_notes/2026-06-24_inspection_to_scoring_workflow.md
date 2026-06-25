# 2026-06-24 Session Notes — Inspection-to-Scoring Workflow

## Session context

We continued ARC Prize 2026 / ARC-AGI-3 work after identifying that the current best observed `0.38` result from the Persistent Memory short/gated-BFS v1 notebook is not yet stable.

Latest validated ladder:

| Experiment | Public Score | Decision |
|---|---:|---|
| FORGE V1 instrumented | 0.26 | validated baseline |
| FORGE V1 no-BFS | 0.28 | useful ablation |
| Persistent Memory BFS exact replication | 0.30 | older baseline |
| Persistent Memory no-BFS | 0.17 | rejected |
| Persistent Memory short/gated-BFS v1 V1 | 0.38 | best observed; keep selected |
| Persistent Memory gated-BFS v2 | 0.18 | rejected |
| Persistent Memory v1 + loop/no-change pruning | 0.24 | rejected |
| Persistent Memory short/gated-BFS v1 V2 | 0.20 | rerun instability / seed-sensitive |

Main prior conclusion:

```text
The next question is no longer only “how do we improve from 0.38?”
It is “how do we make the 0.38 behavior repeatable?”
```

## What was done today

### 1. Discussed inspection-first workflow

The user asked whether we can use an inspection notebook that displays and analyzes outputs, then add analysis cells for logs, summaries, recordings, hyperparameters, constraints, and tunable inputs.

Decision:

```text
Yes. Development should move to a two-notebook workflow:
1. Inspection / tuning workbench notebook.
2. Minimal scoring notebook.
```

The intended workflow:

```text
Current best scoring notebook
        ↓ copy agent / params
Inspection notebook
        ↓ run offline evaluator and inspect logs/recordings/summaries
Change exactly one parameter or mechanism
        ↓ generate candidate agent
Candidate scoring notebook
        ↓ submit to Kaggle scoring
Promote only if public score improves
```

### 2. Created inspection/tuning workbench notebook

Generated notebook artifact:

```text
arc3-inspection-tuning-workbench.ipynb
```

Purpose:

```text
Use this as the laboratory notebook for offline inspection, recordings, log review, parameter sweeps, and next-experiment brainstorming.
```

The inspection notebook is intended to include:

- offline evaluator + recording viewer,
- editable experiment control panel,
- patch cell for BFS budgets / MAX_ACTIONS / deterministic seed,
- diagnostic summary tables,
- multi-run comparison table,
- Gold-path experiment matrix.

Initial recommended use:

```text
max_actions_cap = 1000
deterministic_seed = False
BFS budget = validated v1 values
```

Then calibrate offline score with:

```text
MAX_ACTIONS = 501 / 1000 / 2000
```

to learn which offline cap correlates with public leaderboard behavior.

### 3. Created scoring notebook for current best line

Generated scoring notebook artifact:

```text
arc3-scoring-persistent-memory-short-gated-bfs-v1-current-best.ipynb
```

Purpose:

```text
Minimal Kaggle scoring notebook for the current-best Persistent Memory short/gated-BFS v1 line.
```

The scoring notebook should be used for Kaggle submission only.

Recommended use:

```text
1. Upload scoring notebook to Kaggle.
2. Run all cells.
3. Submit for scoring.
4. Keep the existing 0.38 selected unless this beats it.
```

### 4. User submitted latest scoring notebook

The user reported that the scoring notebook was submitted for Kaggle scoring.

Current status:

```text
Notebook: arc3-scoring-persistent-memory-short-gated-bfs-v1-current-best.ipynb
Submission status: submitted for scoring
Public score: pending
```

## Agreed workflow from next session onward

From the next session, the process should be:

```text
1. Receive latest public score.
2. Record score and compare with experiment hypothesis.
3. Use inspection notebook to run offline diagnostics.
4. Inspect:
   - summary.csv
   - scorecard.json
   - run.log
   - recordings
   - diagnostic tables
5. Identify failure pattern.
6. Modify exactly one control/hyperparameter/mechanism in the inspection workbench.
7. Generate/update scoring notebook.
8. Submit scoring notebook.
9. Push session notes.
```

This moves development away from ad hoc notebook edits and toward a reproducible experiment loop.

## Proposed control panel for future experiments

The inspection notebook should centralize tunable controls such as:

```python
BFS_TIMEOUT = 35
SCAN_TIMEOUT = 2
MAX_STATES = 75000
MAX_DEPTH = 18
ENABLE_HIDDEN_RETRY = True
ENABLE_TTT = True
ENABLE_PER = True
ENABLE_CLEAR = True
ENABLE_CLTI = True
ENABLE_LOOP_PENALTY = False
ENABLE_STATE_HASH = True
DETERMINISTIC_SEED = False
MAX_ACTIONS_CAP = 1000
SEED_SALT = "pm_gated_v1"
```

Rule:

```text
Change one thing at a time unless explicitly running a designed sweep.
```

## What worked

- We created a clear separation between inspection and scoring notebooks.
- We generated both the inspection/tuning notebook and the scoring notebook.
- The user submitted the scoring notebook for scoring.
- We agreed to use the inspection notebook from the next session to analyze logs and recordings before changing the scoring notebook.

## What failed / unresolved

- Latest scoring result is pending.
- The `0.38` current best remains unstable based on the previous `0.20` rerun.
- Deterministic seed control remains the next major stabilization experiment, but should be implemented through the new inspection-to-scoring workflow.
- Offline evaluator action-cap calibration remains unresolved.

## Current best score/result

```text
Best observed public score: 0.38
Best observed notebook: Persistent Memory short/gated-BFS v1 — Version 1
Latest rerun/control score: 0.20
Current scoring notebook submitted: pending
```

## Files / artifacts created

```text
arc3-inspection-tuning-workbench.ipynb
arc3-scoring-persistent-memory-short-gated-bfs-v1-current-best.ipynb
```

Session note created:

```text
session_notes/2026-06-24_inspection_to_scoring_workflow.md
```

## Next session reminder flow

When the latest score arrives, follow this sequence:

1. Record the public score.
2. Compare against current best `0.38` and latest rerun `0.20`.
3. Decide whether it is:
   - improvement,
   - neutral/stable,
   - regression,
   - or error.
4. Open the inspection notebook.
5. Run offline diagnostics with current-best settings.
6. Inspect summary tables, logs, and recordings.
7. Choose exactly one next change.
8. Generate/update scoring notebook.
9. Submit scoring notebook.
10. Push session notes.

## Next likely experiment

Unless the pending score changes the plan, the next highest-value experiment remains:

```text
Persistent Memory short/gated-BFS v1 — deterministic seed control
```

Goal:

```text
Make the strong 0.38 behavior repeatable rather than relying on stochastic luck.
```
