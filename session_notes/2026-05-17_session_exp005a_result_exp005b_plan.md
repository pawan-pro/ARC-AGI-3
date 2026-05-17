# 2026-05-17 Session Notes — EXP-005A Result and EXP-005B Plan

## Session context

We started the 2026-05-17 ARC-AGI-3 session with the EXP-005A scoring result available.

Result provided by user:

```text
EXP-005A — BFS Diagnostics + Hidden-State Hash
Version 9
Status: Succeeded
Public Score: 0.17
```

Previous validated best:

```text
EXP-003B / V6 public score: 0.12
```

EXP-005 minimal source-BFS result:

```text
EXP-005 / V8 public score: 0.08
```

## What was done

### 1. Interpreted EXP-005A result

EXP-005A is now the current best public submission for the project.

Score ladder:

```text
EXP-000 random baseline:        0.07
EXP-001 visible-pixel baseline: 0.11
EXP-003B progress prior:        0.12
EXP-005 minimal source-BFS:     0.08
EXP-005A hidden-hash BFS:       0.17  <-- new best
```

K-12 version: the first source-BFS robot entered the game but scored low. Adding hidden-state memory made it stronger, so the planner direction is working.

Research version: EXP-005A validates the source-BFS path and hidden-state-aware hashing. The improvement from `0.08` to `0.17` suggests state representation/hash quality matters.

### 2. Strategic clarification

User clarified that the goal is **not** public-score recovery via the known EXP-003B fallback.

The goal is:

```text
Improve BFS/source-planning logic so the score can approach public source-planner notebooks around 0.4+.
```

Therefore:

- Do not prioritize EXP-003B fallback integration yet.
- Keep planner/BFS experiments isolated.
- Build toward stronger source-code planning.

### 3. Tracker addendum created

Created:

```text
docs/experiment_tracker_2026-05-17_exp005a_exp005b_addendum.md
```

Commit:

```text
fc1d1325455c3c734468aff6f1b8b12ce9d83730
```

The addendum records:

- EXP-005 V8 public score `0.08`.
- EXP-005A V9 public score `0.17` and new-best status.
- EXP-005B as the next pending experiment.

## What worked

- EXP-005A succeeded on Kaggle.
- EXP-005A improved public score from `0.08` to `0.17`.
- The planner-focused direction is validated.
- Hidden-state-aware hashing appears to be an important improvement.

## What failed / unresolved

- We still do not have detailed scoring-time artifact inspection in the chat.
- Need to inspect `/kaggle/working/exp005a_bfs_events.jsonl` and `/kaggle/working/exp005a_run_summary.json` if available from output.
- It is not yet clear how much of the `0.17` gain came from:
  - hidden-state hashing,
  - source load success,
  - BFS replay,
  - or incidental fallback behavior.
- EXP-005A still likely misses many useful click/action candidates because scan logic is basic stride-2 non-background scanning.

## Current best score/result

```text
Current best public score: 0.17
Experiment: EXP-005A — BFS Diagnostics + Hidden-State Hash
Version: 9
Status: Succeeded / new public baseline
```

## Files changed

Created:

```text
docs/experiment_tracker_2026-05-17_exp005a_exp005b_addendum.md
session_notes/2026-05-17_session_exp005a_result_exp005b_plan.md
```

Upcoming file to create in this session:

```text
notebooks/01_exploration/exp005b_stronger_effective_action_scan.ipynb
```

## Next session / next step plan

### P0 baseline

Keep EXP-005A as the current validated public baseline.

### P1 robust planner improvement

Create and run:

```text
EXP-005B — stronger effective-action scan
```

Primary change:

```text
Improve BFS action candidate generation.
```

Add:

- Connected-component click candidates.
- Object centers.
- Object corners / edges.
- Small-object priority.
- Neighbor expansion around useful hits.
- Per-method scan diagnostics.

### P2 leaderboard improvement

Submit EXP-005B only after notebook mechanics pass.

Target: improve over `0.17` by increasing BFS-solved levels.

### P3 medal-level research bet

Continue building source-code planner capabilities:

- hidden-state-aware hash,
- stronger effective-action scan,
- level-to-level transfer,
- counter-A*,
- ACMD / hidden-trigger priority,
- IDDFS for low-branching deep games,
- sprite permutation for pure-click games.

### P4 paper-track narrative

Emerging story:

```text
Minimal source-BFS alone regressed to 0.08.
Adding hidden-state-aware hashing improved to 0.17.
This suggests ARC-AGI-3 source planners need both visible-state and hidden-state reasoning.
Next bottleneck is action proposal quality.
```

## EXP-005B validation checklist

After running EXP-005B, inspect:

```text
/kaggle/working/exp005b_bfs_events.jsonl
/kaggle/working/exp005b_run_summary.json
```

Key fields:

- `scan.generated_by_method`
- `scan.effective_by_method`
- `scan.unique_effects`
- `scan.deduped`
- `scan.timeout_hit`
- `hidden`
- `hidden_hash`
- `explored`
- `unique`
- `status`
- `solution_len`
- `policy.bfs_replay`
- `policy.fallback`

## Codex prompt for EXP-005B

```text
Create a new notebook:
notebooks/01_exploration/exp005b_stronger_effective_action_scan.ipynb

Base it on:
notebooks/01_exploration/exp005a_bfs_diagnostics_hidden_hash.ipynb

Objective:
Improve BFS effective-action scanning while preserving hidden-state hashing and JSON diagnostics.

Requirements:
1. Do not modify EXP-005A.
2. Add connected-component extraction over non-background pixels.
3. Generate click candidates by method:
   - stride2_non_background
   - component_center
   - component_corners
   - component_edge_midpoints
   - small_object_priority
   - neighbor_expansion
4. For each method, log:
   - generated candidate count
   - tested candidate count
   - effective candidate count
   - unique effect count
   - deduped count
5. Preserve directional ACTION1–ACTION5 scanning.
6. Preserve hidden-state probing and frame+hidden-field hashing.
7. Save artifacts:
   - /kaggle/working/exp005b_bfs_events.jsonl
   - /kaggle/working/exp005b_run_summary.json
8. Keep fallback simple; do not integrate EXP-003B fallback.
9. Include a tracker-row draft but do not mark improvement until public/local result is known.
```
