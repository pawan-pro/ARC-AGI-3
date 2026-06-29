# 2026-06-29 Session Notes — Offline Evaluation, Seed Control, and Next Workflow

## Session context

We started the 2026-06-29 ARC Prize 2026 / ARC-AGI-3 session after several Kaggle scoring runs showed that the current best observed `0.38` result is not yet reproducible.

Latest known public-score ladder entering this session:

| Experiment | Public Score | Decision |
|---|---:|---|
| FORGE V1 instrumented | 0.26 | historical validated baseline |
| FORGE V1 no-BFS | 0.28 | historical useful ablation |
| Persistent Memory BFS exact replication | 0.30 | older baseline |
| Persistent Memory no-BFS | 0.17 | rejected |
| Persistent Memory short/gated-BFS v1 — Version 1 | 0.38 | best observed; keep selected |
| Persistent Memory short/gated-BFS v1 — Version 2 | 0.20 | rerun instability / weak |
| Persistent Memory short/gated-BFS v2 — Version 1 | 0.19 | rejected |
| Persistent Memory gated-BFS v2 / wider budget | 0.18 | rejected |
| Persistent Memory v1 + loop/no-change pruning | 0.24 | rejected |

Main working conclusion before this session:

```text
The 0.38 run was real but unstable. The immediate objective is to understand and stabilize the 0.38 behavior before adding new architecture changes.
```

## What was done today

### 1. Reviewed latest public scores

The user reported:

```text
Persistent Memory short/gated-BFS v2 - Version 1: 0.19
Persistent Memory short/gated-BFS v1 - Version 2: 0.20
```

Interpretation:

- Both scores are far below the best observed `0.38`.
- v2 is rejected.
- v1 is high-variance / seed-sensitive / timing-sensitive.
- The best observed `0.38` remains selected, but it should not yet be treated as a stable expected score.

Current decision:

```text
Keep the 0.38 submission selected. Do not expand BFS budget further. Do not add more pruning. Focus on offline inspection and variance analysis.
```

### 2. Created updated inspection notebook for seed-control workflow

The user supplied a notebook referred to as the v1 notebook, though the uploaded filename was:

```text
persistent-memory-short-gated-bfs-v2.ipynb
```

Inspection showed the embedded BFS defaults matched the short/gated v1 budget:

```text
scan_timeout = 2
bfs_timeout = 35
max_states = 75000
max_depth = 18
```

Generated updated inspection notebook:

```text
arc3-inspection-tuning-workbench-20260629-seed-control.ipynb
```

Purpose:

```text
Use the inspection notebook as the laboratory for offline evaluation, recording review, diagnostics, parameter control, and scoring-notebook generation.
```

The key experiment was:

```text
Persistent Memory short/gated-BFS v1 + deterministic seed control
```

Goal:

```text
Test whether deterministic seeding can stabilize the 0.38 behavior or whether it locks into the weaker 0.19–0.20 trajectory.
```

### 3. Ran offline evaluator with deterministic seed control

The user ran the inspection notebook offline and uploaded the output artifacts:

```text
summary.txt
summary.csv
scorecard.json
Pasted text from notebook output
```

Large artifacts were not uploaded because:

- two game recordings exceeded 50 MB each,
- the run log was also around 50 MB,
- all games ran to the action cap, creating large frame-by-frame recordings.

Offline run description:

```text
pm-gated-v1-deterministic-seed-control-a
```

Offline result:

```text
Overall offline score: 0.19160326852634543
Games: 25
Total levels completed: 2 / 183
Total actions: 25025
All games hit 1001 actions
```

Games with progress:

| Game | Levels completed | Actions | Score |
|---|---:|---:|---:|
| sp80 | 1 | 1001 | 4.761905 |
| cd82 | 1 | 1001 | 0.028177 |

All other games scored zero and ran to the cap.

Key summary from `summary.txt`:

```text
ar25 0 levels 1001 actions score 0
bp35 0 levels 1001 actions score 0
cd82 1 level 1001 actions score 0.028177
...
sp80 1 level 1001 actions score 4.761905
...
Overall score: 0.191603
```

Key summary from `scorecard.json`:

```text
score: 0.19160326852634543
total_levels_completed: 2
total_levels: 183
total_actions: 25025
```

## Interpretation

The deterministic-seed offline run behaved like the weak public-score runs around `0.19–0.20`, not like the best observed `0.38` run.

Working interpretation:

```text
Deterministic seed control, as currently configured, did not stabilize the 0.38 behavior. It likely locked the agent into a mediocre exploration trajectory.
```

Therefore:

```text
Do not promote deterministic-seed-control-a as a scoring candidate yet.
Do not submit this deterministic version unless a later offline/seed-sweep result improves.
```

The result is useful because it supports the hypothesis that the `0.38` result came from favorable stochastic exploration, timing, or seed/replay ordering.

## Large-file issue

The uploaded artifacts were large because:

```text
MAX_ACTIONS_CAP = 1000
```

and all 25 games reached the cap. The recording viewer showed examples such as:

```text
cd82 | 1001 frames
```

Large artifacts are expected when recording all games at 1000 frames each.

Decision:

```text
Do not record every game in future inspection runs.
```

Future offline evaluation should separate summary-only runs from targeted recording runs.

## Notebook issues found

### Cell 7 syntax error

Cell 7 failed because of broken multiline strings:

```python
print("
High-level diagnostics:")
```

This caused:

```text
SyntaxError: unterminated string literal
```

### Cell 8 syntax error

Cell 8 has the same pattern:

```python
print("
Game-level long table:")
```

and needs repair before the next analysis cycle.

Decision:

```text
First action next session: fix Cells 7 and 8 of the inspection notebook.
```

## Updated offline evaluation workflow

Do not run full recordings for all games by default.

### Stage 1 — Fast all-game summary

Run:

```text
RUN_GAME = all
MAX_ACTIONS_CAP = 501
SAVE_RECORDINGS = False, if supported
```

Purpose:

```text
Quickly estimate whether a seed/config is dead or promising without huge artifacts.
```

If `SAVE_RECORDINGS = False` is not supported by the current evaluator, then use the lowest practical recording setting and avoid downloading recordings.

### Stage 2 — Target successful games

Run only:

```text
sp80
cd82
```

Settings:

```text
MAX_ACTIONS_CAP = 1000
SAVE_RECORDINGS = True
```

Purpose:

```text
Inspect why the agent made progress and whether the success came from BFS, replay, TTT, or stochastic action choice.
```

### Stage 3 — Target failed games

Run a small failure subset:

```text
sb26
lf52
g50t
lp85
sk48
```

Settings:

```text
MAX_ACTIONS_CAP = 501
SAVE_RECORDINGS = True
```

Purpose:

```text
Inspect common stuck behavior without producing huge artifacts.
```

## Inspection-to-scoring workflow for next chat

The next chat should continue with this exact sequence:

```text
1. Open / update the inspection notebook.
2. Fix Cells 7 and 8 syntax errors.
3. Add or verify a central control panel:
   - SCAN_TIMEOUT
   - BFS_TIMEOUT
   - MAX_STATES
   - MAX_DEPTH
   - ENABLE_HIDDEN_RETRY
   - ENABLE_TTT
   - ENABLE_PER
   - ENABLE_CLEAR
   - ENABLE_CLTI
   - DETERMINISTIC_SEED
   - SEED_SALT
   - MAX_ACTIONS_CAP
   - RUN_GAME
   - SAVE_RECORDINGS, if possible
4. Run summary-only offline evaluation.
5. Inspect summary.csv and scorecard.json.
6. Run targeted recordings only for selected games.
7. Brainstorm from diagnostics.
8. Change exactly one parameter or mechanism.
9. Generate scoring notebook from the inspection notebook.
10. Submit scoring notebook to Kaggle.
11. Record public score.
12. Push session notes.
```

## Recommended next experiment

Do not make new architecture changes yet.

Next controlled direction:

```text
Seed-salt sweep around Persistent Memory short/gated-BFS v1
```

Reason:

```text
Single deterministic seed performed like 0.19. The 0.38 run may depend on favorable stochastic exploration. A seed-salt sweep can identify whether stable high-performing deterministic seeds exist.
```

Suggested seed salts:

```text
pm_gated_v1_seed_a
pm_gated_v1_seed_b
pm_gated_v1_seed_c
pm_gated_v1_seed_d
pm_gated_v1_seed_e
```

Initial evaluation for each seed:

```text
RUN_GAME = all
MAX_ACTIONS_CAP = 501
recordings off / do not inspect recordings
```

Promote only seeds that produce more progress than deterministic-seed-control-a.

Potential scoring notebook only after offline evidence:

```text
Persistent Memory short/gated-BFS v1 — deterministic seed salt candidate
```

## Current best score/result

```text
Best observed public score: 0.38
Best observed notebook: Persistent Memory short/gated-BFS v1 — Version 1
Latest weak reruns: 0.20 and 0.19
Latest deterministic offline score: 0.191603
Current selected submission should remain: 0.38
```

## What worked today

- The inspection workflow successfully ran offline evaluation through the official path.
- The deterministic-seed experiment produced clear diagnostics.
- We identified that deterministic seed control did not reproduce the 0.38 behavior.
- We identified why artifacts were huge and created a better staged offline-evaluation plan.
- We found concrete notebook defects in Cells 7 and 8 that need repair.

## What failed / unresolved

- Deterministic-seed-control-a offline score was weak at `0.191603`.
- Only 2 of 25 games made any progress.
- All games hit the 1001 action cap.
- Recordings and logs became too large for efficient upload/inspection.
- Cells 7 and 8 need syntax fixes.
- The true cause of the 0.38 public run remains unknown.

## Files / artifacts referenced

Uploaded by user:

```text
summary.txt
summary.csv
scorecard.json
Pasted text.txt
```

Generated earlier:

```text
arc3-inspection-tuning-workbench-20260629-seed-control.ipynb
```

Session note created:

```text
session_notes/2026-06-29_offline_evaluation_seed_control_workflow.md
```

## Next-session starting point

Start the next chat from this principle:

```text
The goal is no longer to blindly tune for a higher score. The goal is to understand and reproduce the 0.38 behavior by using the inspection notebook, repairing its diagnostic cells, running controlled seed-salt/offline evaluations, and only then generating a scoring notebook.
```
