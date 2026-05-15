# 2026-05-15 Session Notes — ARC-AGI-3 EXP-005 Source-BFS Pivot

## Session context

We started the 2026-05-15 ARC-AGI-3 session from the existing state:

- Current internal public baseline: `EXP-003B`
- Current best public score: `0.12`
- EXP-003B local score: `0.4849109618`
- EXP-003B local levels: `6 / 183`
- EXP-004 / EXP-004_100k were discovery-only long-horizon experiments, not submission baselines.

The main new input was a review of public ARC-AGI-3 notebooks scoring materially higher than our baseline:

- Ash / CHRONOS-style public notebook around `0.42`
- Public variant reported around `0.46`
- FORGE v16 public notebook around `0.31–0.35`

These public notebooks showed that the stronger leaderboard direction is not just random/progress-prior exploration. The key pattern is:

```text
source-code access → offline game instantiation → BFS/planning → online replay
```

K-12 version: instead of only playing by trial and error, the agent opens a practice copy of the game, tests moves safely, finds a path, and then plays that path in the real game.

## What was done

### 1. Public notebook strategy analyzed

We compared the public notebook architecture against our current EXP-003B/EXP-004 direction.

Key takeaways:

- Public notebooks use direct access to current game source files under the competition environment.
- They dynamically import the game class.
- They instantiate a local/offline simulator.
- They scan for effective actions before search.
- They use BFS/planning to find level-completing action sequences.
- They replay solved sequences online.
- More advanced versions add hidden-state hashing, click-neighbor probing, counter/A*/ACMD/IDDFS variants, solution transfer, and CNN fallback.

Conclusion: our next priority should pivot from EXP-004 long-horizon compression to a clean source-BFS reproduction.

### 2. EXP-005 notebook created and pushed

Created a new notebook:

```text
notebooks/01_exploration/exp005_minimal_source_bfs_baseline.ipynb
```

Git commit:

```text
e06627b4e130796366ed4d57e62bc3fb085885fe
```

Commit message:

```text
experiments: add EXP-005 minimal source-BFS baseline notebook
```

EXP-005 scope:

- Install `arc-agi` from competition wheels.
- Write `/kaggle/working/my_agent.py`.
- Locate current game source from `arc_env.environment_info.local_dir` first.
- Fall back to conservative glob search if needed.
- Dynamically import the game class with `importlib.util`.
- Instantiate the game offline.
- Set the current level.
- Reset exactly twice.
- Scan effective `ACTION1`–`ACTION5` actions.
- Scan `ACTION6` clicks over visible/non-background pixels with stride-2 plus neighbor refinement.
- Run bounded BFS with configurable timeout, max states, and depth.
- If BFS finds a solution, replay the action sequence online.
- If BFS fails, fall back to a simple visible-pixel/random-action policy.
- Keep a dummy `submission.parquet` fallback for non-rerun Kaggle mode.
- Include a tracker-row draft but do not update `docs/experiment_tracker.md` until validation results are available.

Deliberately not included yet:

- CNN fallback.
- Hidden-state-aware hashing.
- Level-to-level solution transfer.
- Counter A*.
- ACMD.
- IDDFS.
- Sprite-permutation search.
- Full public FORGE-stack copy.

### 3. EXP-005 was run and submitted for scoring

The user ran the notebook and submitted it for scoring.

Important observation from visible log:

```text
Local/non-rerun mode: competition gateway is not available. Writing dummy submission fallback.
Wrote /kaggle/working/submission.parquet dummy fallback.
```

Interpretation:

- The visible notebook run was normal Kaggle notebook mode, not the competition rerun path.
- In normal/non-rerun mode, the code correctly writes a dummy fallback `submission.parquet`.
- In competition scoring, Kaggle should set `KAGGLE_IS_COMPETITION_RERUN=1`, which triggers the real gateway path:

```text
python main.py --agent myagent
```

We should wait for the Kaggle public score and logs before judging EXP-005.

### 4. Linear updated

Added a handoff comment to Linear issue:

```text
KAG-14 — 2026-05-09 ARC-AGI-3 session: artifact comparison and EXP-003F planning
```

The comment records:

- EXP-005 notebook path.
- Commit hash.
- Scope.
- Validation gate.
- Deliberately excluded features.

## What worked

- The ARC GitHub repo was accessible.
- The new EXP-005 notebook was successfully created on `main`.
- The notebook contains a clean first source-BFS baseline rather than a large public-notebook copy.
- The notebook preserves a valid non-rerun dummy submission fallback.
- The source-BFS direction is now represented as a reproducible repo artifact.
- Linear has a session handoff comment for continuity.

## What failed / unresolved

- EXP-005 score is not available yet.
- The visible Kaggle output was non-rerun mode, so it does not prove the live gateway path executed.
- No `docs/experiment_tracker.md` row was added yet because we do not have a real result.
- EXP-005 currently does not export rich BFS logs as files; it stores logs in agent memory. This may make post-submission debugging harder unless Kaggle captures printed logs or we add explicit artifact writes later.
- EXP-005 still lacks the strongest public-notebook refinements: hidden-state hashing and solution transfer.

## Current best score/result

Current validated internal baseline remains:

```text
EXP-003B public score: 0.12
EXP-003B local score: 0.4849109618
EXP-003B local levels: 6 / 183
```

EXP-005 status:

```text
Created and submitted for scoring
Public score: pending
Validation status: pending
```

No improvement should be claimed until Kaggle score/logs are available.

## Files changed

Created:

```text
notebooks/01_exploration/exp005_minimal_source_bfs_baseline.ipynb
```

Created this session note:

```text
session_notes/2026-05-15_session_exp005_source_bfs.md
```

Git commits:

```text
e06627b4e130796366ed4d57e62bc3fb085885fe
experiments: add EXP-005 minimal source-BFS baseline notebook
```

Session note commit is created separately after this file is added.

## Next session plan

### Step 1 — collect EXP-005 scoring result

When Kaggle scoring finishes, record:

- Public score.
- Best score/version.
- Runtime.
- Whether submission succeeded.
- Any gateway errors.
- Any visible BFS/source-loading errors.
- Whether score beats `0.12`.

Then update:

```text
docs/experiment_tracker.md
```

with the real EXP-005 result.

### Step 2 — if EXP-005 fails or ties weakly, inspect failure mode

Likely failure modes:

- Source path not found.
- Game class import failed.
- Reset sequence mismatch.
- BFS action scan found too few useful actions.
- BFS timeout too short.
- Frame-only hash incorrectly pruned hidden states.
- Fallback too weak.

### Step 3 — implement EXP-005A hidden-state-aware BFS

Recommended next notebook:

```text
notebooks/01_exploration/exp005a_hidden_state_bfs.ipynb
```

Objective:

```text
Copy EXP-005 and add hidden-state-aware hashing.
```

Add:

- `_probe_hidden_fields(game, actions)`.
- Inspect `game.__dict__` for scalar fields: `int`, `float`, `bool`.
- Exclude obvious runtime/noise fields like `_action_count`, `_full_reset`, `_action_complete`.
- Include detected hidden fields in BFS state hash:

```text
frame_md5 + "|" + field_name=value
```

Log:

- `hidden_fields_detected`
- `hidden_hash_enabled`
- `unique_states`
- `explored`
- `solution_len`
- `status`

Do not add CNN, transfer, A*, ACMD, or IDDFS yet.

### Step 4 — after EXP-005A, add EXP-005B click scan improvement

Candidate features:

- Connected components.
- Object centers.
- Object corners and edges.
- Small-object priority.
- Click effect deduplication.

### Step 5 — after EXP-005B, add EXP-005C level-to-level transfer

Candidate features:

- Direct replay of previous level solution.
- Object-relative click offset transfer.
- Small repeat multipliers.

### Step 6 — after source-BFS stabilizes, add EXP-005D fallback upgrade

Replace the simple fallback with our known EXP-003B-style progress-weighted action prior:

```text
BFS if solved; otherwise EXP-003B fallback.
```

This should be safer than jumping directly to CNN fallback.

## Codex prompt for next implementation

```text
Create a new notebook:

notebooks/01_exploration/exp005a_hidden_state_bfs.ipynb

Base it on:
notebooks/01_exploration/exp005_minimal_source_bfs_baseline.ipynb

Objective:
Add hidden-state-aware BFS hashing while keeping the rest of EXP-005 unchanged.

Requirements:
1. Keep EXP-005 unchanged.
2. Copy EXP-005 into EXP-005A.
3. Add a method in MinimalBFSSolver:

   _probe_hidden_fields(game, actions)

   It should inspect game.__dict__ and collect scalar fields:
   - int
   - float
   - bool

   Exclude:
   - _action_count
   - _full_reset
   - _action_complete
   - obvious private runtime/cache fields if they are not stable

4. Before BFS begins, run a small probe:
   - start from reset game
   - apply up to first 10 candidate actions on deep copies
   - detect scalar fields that change
   - keep fields that may affect hidden state

5. Replace frame-only state hash with:

   frame_md5 + "|" + field_name=value for each selected field

6. Add logs:
   - hidden_fields_detected
   - hidden_hash_enabled
   - unique_states
   - explored
   - solution_len
   - status

7. Keep bounded BFS limits configurable:
   - EXP005_BFS_TIMEOUT
   - EXP005_MAX_STATES
   - EXP005_MAX_DEPTH

8. Keep simple visible-pixel fallback unchanged.
9. Do not add CNN, transfer, A*, ACMD, or IDDFS yet.
10. Add tracker row draft only; do not update docs/experiment_tracker.md until validation results are available.

Validation:
Compare against EXP-005 and EXP-003B.

EXP-003B reference:
public score 0.12
local score 0.4849109618
levels 6 / 183

Expected output:
- notebook runs in Kaggle commit mode
- submission.parquet produced
- BFS logs show source path and hidden fields if found
```
