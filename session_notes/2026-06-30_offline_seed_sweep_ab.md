# 2026-06-30 Session Notes — Offline Seed-Salt Sweep A/B

## Session context

We continued ARC Prize 2026 / ARC-AGI-3 work from the Persistent Memory short/gated-BFS v1 line.

The current public-score context remains:

```text
Best observed public score: 0.38
Best observed notebook: Persistent Memory short/gated-BFS v1 — Version 1
Known weak reruns: 0.20 / 0.19 region
Current selected submission: keep 0.38 selected
```

Main working question:

```text
Can we make the 0.38 behavior repeatable, or was it a favorable stochastic trajectory?
```

We therefore continued the offline seed-salt workflow instead of changing architecture.

## What was done

### 1. Repaired / used the offline evaluator workbench

The workbench was run with the repaired diagnostic cells and the v1 short/gated-BFS parameters preserved.

Core configuration for the seed sweep:

```text
run_game = all
max_actions_cap = 501
scan_timeout = 2
bfs_timeout = 35
max_states = 75000
max_depth = 18
deterministic_seed = True
enable_soft_loop_pruning = False
no_change_penalty = 0.0
repeat_state_action_penalty = 0.0
```

Important note: `save_recordings` should be `False` for seed-sweep runs to avoid large artifacts. One early run still had recordings enabled, but the recommendation remains to disable recordings for C/D/E and only enable targeted recordings after the sweep.

### 2. Ran seed A

Experiment:

```text
pm-gated-v1-seed-sweep-a
seed_salt = pm_gated_v1_seed_a
```

Offline result:

```text
Overall offline score: 0.19916968479246552
Games: 25
Total levels completed: 3 / 183
Total actions: 12,550
All games hit 502 actions
```

Progress games:

| Game | Levels completed | Actions | Score | Notes |
|---|---:|---:|---:|---|
| sp80 | 1 | 502 | 4.761905 | Strong recurring signal; level 0 solved very quickly, then cap burn |
| cd82 | 1 | 502 | 0.138929 | Weak progress |
| cn04 | 1 | 502 | 0.078408 | New progress vs previous deterministic seed-control-a |

Interpretation:

```text
Seed A improved slightly over deterministic-seed-control-a: 0.191603 -> 0.199170, and 2 levels -> 3 levels.
```

Decision:

```text
Useful breadth signal, but not enough for Kaggle submission.
```

### 3. Duplicate upload check

A later uploaded artifact set matched seed A again. It was not counted as a new seed because the summary and scorecard matched the same run:

```text
score = 0.19916968479246552
progress games = sp80, cd82, cn04
```

### 4. Ran seed B

Experiment:

```text
pm-gated-v1-seed-sweep-b
seed_salt = pm_gated_v1_seed_b
```

Offline result:

```text
Overall offline score: 0.2397231228026976
Games: 25
Total levels completed: 2 / 183
All games hit 502 actions
```

Progress games:

| Game | Levels completed | Actions | Score | Notes |
|---|---:|---:|---:|---|
| sp80 | 1 | 502 | 4.761905 | Repeated across A and B |
| m0r0 | 1 | 502 | 1.231173 | New higher-value progress game |

Interpretation:

```text
Seed B is the best single deterministic seed so far by offline score.
```

But it lost A's `cd82` and `cn04` progress, so it has less breadth.

## Current seed table

| Seed | Description | Offline score | Levels completed | Progress games | Decision |
|---|---|---:|---:|---|---|
| control-a | pm-gated-v1-deterministic-seed-control-a | 0.191603 | 2 | sp80, cd82 | weak baseline |
| A | pm-gated-v1-seed-sweep-a | 0.199170 | 3 | sp80, cd82, cn04 | useful breadth |
| B | pm-gated-v1-seed-sweep-b | 0.239723 | 2 | sp80, m0r0 | best score so far |
| C | pending | pending | pending | pending | run next |
| D | pending | pending | pending | pending | run after C |
| E | pending | pending | pending | pending | run after D |

## Best-per-game diagnostic upper bound from A+B

Combining the best per-game successes from A and B gives a rough local diagnostic upper bound:

```text
sp80  = 4.761905
m0r0  = 1.231173
cd82  = 0.138929
cn04  = 0.078408
sum   = 6.210415
score = 6.210415 / 25 = 0.248417
levels = 4
```

This is not a valid single-agent score, but it suggests that seed scheduling or per-game seed choice may be worth studying after C/D/E.

## What worked

- The offline evaluator produced valid runs with `exit_code = 0`.
- Deterministic seed salts materially changed behavior.
- Seed A found breadth: `sp80`, `cd82`, `cn04`.
- Seed B found a stronger score path via `m0r0` while preserving `sp80`.
- The workbench diagnostic cells produced useful summaries and comparison tables.

## What failed / unresolved

- No seed is strong enough for Kaggle submission yet.
- All 25 games still hit the 502-action cap.
- The agent is solving isolated level-0 cases and then burning the remaining action budget.
- Seed B improves score but reduces breadth from 3 progress games to 2.
- The reason for the public `0.38` run remains unresolved.
- Full recordings should not be enabled during broad seed sweeps.

## Current best score/result

```text
Best public score: 0.38 — Persistent Memory short/gated-BFS v1 Version 1, keep selected
Best current offline seed-sweep score: 0.239723 — seed B
Best current offline breadth: 3 levels — seed A
Submission decision: do not submit yet
```

## Files / artifacts referenced

Notebook used locally / in Kaggle:

```text
arc3-inspection-tuning-workbench-20260629-seed-control.ipynb
```

Seed A run directory:

```text
/kaggle/working/runs-20260630-114732-pm-gated-v1-seed-sweep-a
```

Seed B run directory:

```text
/kaggle/working/runs-20260630-120047-pm-gated-v1-seed-sweep-b
```

Artifacts reviewed:

```text
summary.txt
summary.csv
scorecard.json
diagnostic_summary.csv
diagnostic_summary_enriched.csv
notebook output pasted in chat
```

## Next session plan

Run remaining deterministic seed salts C, D, and E tomorrow.

Use the same settings except changing `description` and `seed_salt`:

```python
EXPERIMENT = {
    "description": "pm-gated-v1-seed-sweep-c",
    "run_game": "all",
    "max_actions_cap": 501,
    "save_recordings": False,

    "scan_timeout": 2,
    "bfs_timeout": 35,
    "max_states": 75000,
    "max_depth": 18,

    "deterministic_seed": True,
    "seed_salt": "pm_gated_v1_seed_c",

    "enable_soft_loop_pruning": False,
    "no_change_penalty": 0.0,
    "repeat_state_action_penalty": 0.0,

    "patch_agent_after_write": True,
}
```

Then repeat for:

```text
pm_gated_v1_seed_d
pm_gated_v1_seed_e
```

Run cells in order:

```text
Cell 0  - control panel
Cell 2  - write my_agent.py
Cell 2B - patch agent from control panel
Cell 4  - run offline evaluation
Cell 6  - offline run analysis
Cell 7  - deep diagnostics
Cell 8  - compare runs
```

Before Cell 4, verify Cell 2B prints the intended salt, e.g.:

```python
seed = _stable_seed('pm_gated_v1_seed_c', getattr(s, 'game_id', 'unknown'))
```

Promotion rules:

```text
Weak promotion / inspect further: score >= 0.25 or levels completed >= 4
Strong promotion / potential scoring notebook: score >= 0.30 or levels completed >= 5
```

After C/D/E, compare all seeds by:

```text
overall_score
levels_completed
progress games
new games discovered
whether sp80 repeats
whether m0r0/cd82/cn04 repeat
```

Targeted recordings after the sweep should focus on:

```text
sp80
m0r0
cd82
cn04
```

Main diagnostic question for recordings:

```text
Why does the agent solve one level, then fail to transfer or continue efficiently to level 1?
```

Do not generate or submit a Kaggle scoring notebook until the remaining seed sweep is complete and at least one candidate passes the offline promotion gate.
