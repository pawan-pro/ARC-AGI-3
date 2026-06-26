# 2026-06-26 Session Notes — Offline Workbench Runner Failure

## Session context

We continued ARC Prize 2026 / ARC-AGI-3 work from the Persistent Memory short/gated-BFS line.

Current public context:

```text
Best observed public score: 0.38
Best observed notebook: Persistent Memory short/gated-BFS v1 — Version 1
Known v1 rerun/control score: 0.20
Latest v2 public score: 0.19
```

Main question remains:

```text
Can we make the 0.38 behavior repeatable?
```

## New Kaggle result reviewed

The user reported:

```text
Submission: Persistent Memory short/gated-BFS v2 — Version 1
Status: Succeeded
Public Score: 0.19
```

Interpretation:

- The submission succeeded.
- Treat `0.19` as a real policy result, not a Kaggle crash.
- v2 does not improve on the current best `0.38`.
- v2 is also below the stable FORGE / no-BFS region previously observed around `0.26–0.28`.

Decision:

```text
Reject Persistent Memory short/gated-BFS v2 as an improvement candidate.
Return focus to v1 deterministic seed control and offline evaluator validation.
```

## Offline workbench reviewed

The self-contained offline workbench was run:

```text
arc3-self-contained-offline-gold-workbench.ipynb
```

The notebook now has the correct architecture:

- no external v1/v2 source notebook inputs;
- Cell 0 control panel for hyperparameters;
- Cell 2 embedded Persistent Memory / Gated-BFS agent;
- Cell 2B agent patching from the control panel;
- Cell 4 single offline run;
- Cells 6–8 diagnostics and run comparison.

Important knobs exposed in Cell 0 include:

```text
max_actions_cap
scan_timeout
bfs_timeout
max_states
max_depth
deterministic_seed
seed_salt
epsilon_start / epsilon_min / epsilon_decay
ttt_max
batch_size
train_frequency
PER / CLEAR / PersistentAEM capacities
enable_bfs
enable_clear
enable_persistent_aem
```

## Offline workbench result

The active experiment was:

```text
A_v1_current_best_stochastic
```

Agent generation worked. Cell 2B reported successful patching of:

```text
MAX_ACTIONS cap
BFSSolver constructor defaults
BFSSolver instantiation
epsilon_start / epsilon_min / epsilon_decay
ttt_max
batch_size
train_frequency
PERBuffer config
CLEAR archive capacity
PersistentAEM capacity
```

But the offline run failed before gameplay:

```text
Overall score: N/A
exit_code: 1
overall_score: None
```

Diagnostic cells showed:

```text
games: 25
nonzero_score_games: 0
completed_level_games: 0
mean_actions: 0.0
median_actions: 0.0
cap_hit_games: 0
all games state = waiting
all action_count = 0
```

Correct interpretation:

```text
Offline evaluator failed before gameplay.
No actions were executed.
No valid scorecard was produced.
This is not a valid offline score of 0.0.
```

## What worked

- The notebook is now self-contained.
- External v1/v2 notebook placeholders were removed from the workflow.
- The control panel exposes the right experiment knobs.
- The embedded agent was written to `/kaggle/working/my_agent.py`.
- The patch layer applied the active A configuration successfully.
- Run directories and artifact paths were created.

## What failed / unresolved

- Offline runner exited with `exit_code = 1`.
- No games executed.
- All 25 games stayed in `waiting` state.
- All action counts were `0`.
- No valid offline scorecard was produced.
- The exact traceback was not visible in the exported PDF.
- The next step is to inspect the failed run's `run.log` tail.

Likely failure class:

- `my_agent.py` import or syntax error;
- `agents/__init__.py` patch mismatch;
- `main.py` CLI/environment mismatch;
- local fake `/api/games` shim starts but the runner crashes afterward;
- environment path or repo-copy mismatch.

## Current best score/result

```text
Best observed public score: 0.38
Best observed notebook: Persistent Memory short/gated-BFS v1 — Version 1
Known rerun/control score: 0.20
Latest v2 public score: 0.19
Offline workbench result: invalid runner failure before gameplay
```

## Decision

Do not run B, B2, B3, BFS sweeps, or gold-directed hyperparameter sweeps yet.

First fix the offline runner until `A_v1_current_best_stochastic` produces:

```text
exit_code = 0
scorecard.json exists
overall_score is parsed
action_count > 0 for at least some games
recordings exist
```

## Files / artifacts referenced

```text
notebook28edd781bb - Colab.pdf
arc3-self-contained-offline-gold-workbench.ipynb
/kaggle/working/runs-20260626-125626-a-v1-current-best-stochastic
```

## Next session plan

1. Inspect the failed run log tail:

```text
/kaggle/working/runs-20260626-125626-a-v1-current-best-stochastic/run.log
```

2. Identify exact traceback/import/runtime failure.
3. Patch the offline runner or agent import path.
4. Add a validation guard after Cell 4 so failed runs are not summarized as valid `0.0` results.
5. Re-run `A_v1_current_best_stochastic`.
6. Run `B_v1_deterministic_seed_only` only after A produces a valid offline scorecard.
7. Keep the public `0.38` submission selected unless a new Kaggle run beats it.
