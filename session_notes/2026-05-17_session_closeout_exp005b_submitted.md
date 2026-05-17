# 2026-05-17 Session Closeout — EXP-005A New Best and EXP-005B Submitted

## Session context

We started the 2026-05-17 ARC-AGI-3 session with the result for EXP-005A available:

```text
EXP-005A — BFS Diagnostics + Hidden-State Hash
Version: 9
Status: Succeeded
Public Score: 0.17
```

This beat the previous validated best:

```text
EXP-003B / V6 public score: 0.12
```

EXP-005 minimal source-BFS had previously scored:

```text
EXP-005 / V8 public score: 0.08
```

## What was done

### 1. Interpreted EXP-005A result

EXP-005A became the new public baseline for this project.

Score ladder after EXP-005A:

```text
EXP-000 random baseline:        0.07
EXP-001 visible-pixel baseline: 0.11
EXP-003B progress prior:        0.12
EXP-005 minimal source-BFS:     0.08
EXP-005A hidden-hash BFS:       0.17  <-- new best
```

Interpretation:

- The source-BFS/planner direction is now validated.
- The improvement from `0.08` to `0.17` likely came from better state representation: frame hash plus hidden scalar fields.
- The key idea: some game states may look identical on screen but differ in hidden counters/flags. EXP-005A avoids collapsing those states incorrectly.

K-12 version:

```text
EXP-005 only remembered what the board looked like.
EXP-005A also remembered hidden switches/counters.
So it stopped throwing away useful practice states that looked the same but were secretly different.
```

### 2. Explained how BFS works in the 0.17 solution

The EXP-005A BFS flow:

1. `find_src` finds the game source/rulebook.
2. `Solver.load` imports the game class.
3. `reset` creates a clean offline practice level.
4. `scan` tests actions and keeps actions/clicks that change the game.
5. `probe` checks which hidden scalar fields change after actions.
6. `sh` creates the BFS state key:

```text
state = visible frame hash + hidden scalar values
```

7. `solve` runs BFS over copied game states.
8. `try_bfs` runs BFS once per level.
9. `choose_action` replays a BFS solution if one was found; otherwise it uses simple fallback exploration.

### 3. Created tracker addendum and session notes

Created tracker addendum:

```text
docs/experiment_tracker_2026-05-17_exp005a_exp005b_addendum.md
```

Commit:

```text
fc1d1325455c3c734468aff6f1b8b12ce9d83730
```

Created session note:

```text
session_notes/2026-05-17_session_exp005a_result_exp005b_plan.md
```

Commit:

```text
59455f9a39f26dc0c940fa1aa262c1a20a3c5ad8
```

### 4. Implemented EXP-005B

Created notebook:

```text
notebooks/01_exploration/exp005b_stronger_effective_action_scan.ipynb
```

Commit:

```text
d416d6cfe4f024f9b9b5d3e0023b64bdfd270964
```

EXP-005B keeps the EXP-005A source-BFS + hidden-state-hash backbone, but changes the BFS action proposal step.

Main EXP-005B updates versus EXP-005A:

1. Stronger click candidate generation:

```text
stride2_non_background
component_center
component_corners
component_edge_midpoints
small_object_priority
neighbor_expansion
```

2. Better scan diagnostics:

```text
scan.generated_by_method
scan.tested_by_method
scan.effective_by_method
scan.unique_effects_by_method
scan.deduped_by_method
scan.timeout_hit
```

3. Larger planner budgets:

```text
EXP-005A: BFS timeout ~25s, max states 50k, depth 30
EXP-005B: BFS timeout ~30s, max states 75k, depth 32, max click tests 700
```

4. JSON artifact paths:

```text
/kaggle/working/exp005b_bfs_events.jsonl
/kaggle/working/exp005b_run_summary.json
```

### 5. Fixed visible artifact plumbing

During the local/non-rerun Kaggle notebook run, the output panel initially showed only:

```text
my_agent.py
submission.parquet
```

No JSON artifacts appeared because in visible notebook mode:

```text
KAGGLE_IS_COMPETITION_RERUN is not set
main.py --agent myagent does not run
MyAgent is not instantiated
real BFS diagnostics are not generated
```

A final artifact-check cell was added in Kaggle so that local/non-rerun mode writes placeholder JSON artifacts. This confirms the output paths and output panel plumbing.

Visible output after the artifact-check cell:

```text
/kaggle/working/exp005b_bfs_events.jsonl exists: True size: 268
/kaggle/working/exp005b_run_summary.json exists: True size: 571
```

Important interpretation:

- These local artifacts are placeholders, not real BFS logs.
- Real BFS logs require competition rerun mode, where Kaggle sets `KAGGLE_IS_COMPETITION_RERUN` and runs:

```text
python main.py --agent myagent
```

### 6. Submitted EXP-005B to competition

EXP-005B was submitted to the competition after the artifact placeholder cell was added.

Current submission status at closeout:

```text
EXP-005B: submitted
Scoring: pending
Current best remains: EXP-005A / V9 public score 0.17
```

## What worked

- EXP-005A improved public score to `0.17`, becoming the new best baseline.
- The source-BFS path is validated.
- Hidden-state-aware hashing appears to be a meaningful improvement.
- EXP-005B was implemented as a clean planner-side follow-up, not a fallback-recovery patch.
- EXP-005B output artifact paths now appear in the Kaggle output panel in local/non-rerun mode.
- Linear was updated throughout the session.

## What failed / unresolved

- We still need EXP-005B's public score.
- Local JSON artifacts are placeholders only; scoring-time JSON artifacts still need to be inspected after the competition run.
- It is still not proven how many levels EXP-005A solved via BFS replay versus fallback.
- EXP-005B may improve action proposal quality, but it may also broaden the action set too much and waste BFS budget.

## Current best score/result

```text
Current best public score: 0.17
Experiment: EXP-005A — BFS Diagnostics + Hidden-State Hash
Version: 9
Status: Succeeded / current public baseline
```

Pending:

```text
EXP-005B — Stronger Effective-Action Scan
Submitted to competition
Score pending
```

## Files changed this session

Created:

```text
docs/experiment_tracker_2026-05-17_exp005a_exp005b_addendum.md
session_notes/2026-05-17_session_exp005a_result_exp005b_plan.md
notebooks/01_exploration/exp005b_stronger_effective_action_scan.ipynb
session_notes/2026-05-17_session_closeout_exp005b_submitted.md
```

Commits:

```text
fc1d1325455c3c734468aff6f1b8b12ce9d83730
59455f9a39f26dc0c940fa1aa262c1a20a3c5ad8
d416d6cfe4f024f9b9b5d3e0023b64bdfd270964
```

Closeout note commit is created with this file.

## Next session plan

### Step 1 — collect EXP-005B result

Record:

- Public score.
- Version number.
- Succeeded or Kaggle Error.
- Runtime.
- Output size.
- Whether real JSON artifacts are available or only placeholders.

### Step 2 — inspect EXP-005B artifacts if available

Inspect:

```text
/kaggle/working/exp005b_bfs_events.jsonl
/kaggle/working/exp005b_run_summary.json
```

Key fields:

```text
scan.generated_by_method
scan.tested_by_method
scan.effective_by_method
scan.unique_effects_by_method
scan.deduped_by_method
scan.timeout_hit
hidden
hidden_hash
explored
unique
status
solution_len
policy.bfs_replay
policy.fallback
```

### Step 3 — decide next experiment based on result

If EXP-005B > `0.17`:

```text
Proceed to EXP-005C — level-to-level solution transfer.
```

If EXP-005B ≈ `0.17`:

```text
Use artifacts to tune scan ranking, candidate ordering, and click-test budget.
```

If EXP-005B < `0.17`:

```text
Action scan likely became too broad or slow. Add candidate gating/ranking before adding transfer.
```

### Step 4 — continue toward 0.4+

Milestone ladder:

```text
0.17 -> 0.20–0.25: action scan + diagnostics
0.25 -> 0.32: level transfer + replay validation
0.32 -> 0.38: planner fallback variants: sprite permutation, IDDFS, counter-A*
0.38 -> 0.45+: adaptive routing and time-budget control
```

## Strategic principle

Do not chase fallback recovery. Continue isolating planner improvements and only stack features when diagnostics show the previous layer works.
