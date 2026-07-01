# 2026-07-01 Session Notes — Offline Seed-Salt Sweep C/D/E and Next Schedule

## Session context

We continued ARC Prize 2026 / ARC-AGI-3 work from the Persistent Memory short/gated-BFS v1 offline evaluation workflow.

Prior state entering today:

```text
Best observed public score: 0.38
Best observed notebook: Persistent Memory short/gated-BFS v1 — Version 1
Current selected submission: keep 0.38 selected
Best offline seed from 2026-06-30: seed B, score 0.239723
Best offline breadth from 2026-06-30: seed A, 3 progress games
```

Main working question remained:

```text
Can deterministic seed salts reproduce or approximate the strong 0.38 public behavior?
```

The planned work for today was to finish the remaining seed sweep: C, D, and E.

## Offline evaluator settings

The intended sweep settings remained:

```text
run_game = all
max_actions_cap = 501
save_recordings = False
scan_timeout = 2
bfs_timeout = 35
max_states = 75000
max_depth = 18
deterministic_seed = True
enable_soft_loop_pruning = False
no_change_penalty = 0.0
repeat_state_action_penalty = 0.0
patch_agent_after_write = True
```

Important operational reminder:

```text
After changing seed_salt, rerun Cell 0, Cell 2, and Cell 2B before Cell 4.
Confirm the Cell 2B sanity snippet contains the intended seed salt.
```

## What was done today

### 1. Ran seed C

Experiment:

```text
pm-gated-v1-seed-sweep-c
seed_salt = pm_gated_v1_seed_c
```

Run directory:

```text
/kaggle/working/runs-20260701-140721-pm-gated-v1-seed-sweep-c
```

Offline result:

```text
exit_code = 0
overall_score = 0.19047619047619047
total_levels_completed = 1 / 183
total_actions = 12,550
```

Progress games:

| Game | Levels completed | Actions | Score | Notes |
|---|---:|---:|---:|---|
| sp80 | 1 | 502 | 4.761905 | recurring robust signal |

Interpretation:

```text
Seed C is valid but weak. It only solved the recurring sp80 level-0 case and added no new useful games.
```

Decision:

```text
Reject seed C as a standalone scoring candidate.
```

### 2. Ran seed D

Experiment:

```text
pm-gated-v1-seed-sweep-d
seed_salt = pm_gated_v1_seed_d
```

Run directory:

```text
/kaggle/working/runs-20260701-142127-pm-gated-v1-seed-sweep-d
```

Offline result:

```text
exit_code = 0
overall_score = 0.19047619047619047
total_levels_completed = 1 / 183
total_actions = 12,550
```

Progress games:

| Game | Levels completed | Actions | Score | Notes |
|---|---:|---:|---:|---|
| sp80 | 1 | 502 | 4.761905 | same as seed C |

Interpretation:

```text
Seed D has the same score and game-level pattern as seed C.
```

Concern:

```text
D may genuinely behave like C, but because C/D artifacts appear identical, verify the saved run agent contains pm_gated_v1_seed_d before treating it as fully independent.
```

Decision:

```text
Reject seed D as a standalone scoring candidate.
```

### 3. Ran seed E

Experiment:

```text
pm-gated-v1-seed-sweep-e
seed_salt = pm_gated_v1_seed_e
```

Run directory from pasted console:

```text
/kaggle/working/runs-20260701-142957-pm-gated-v1-seed-sweep-e
```

Pasted console result:

```text
exit_code = 0
overall_score = 0.19161491783449486
```

Uploaded artifact result:

```text
overall_score = 0.19047619047619047
total_levels_completed = 1 / 183
total_actions = 12,550
progress game = sp80 only
```

Interpretation:

```text
There is a small mismatch between the pasted console score and uploaded scorecard/summary artifacts.
```

Possible explanations:

```text
1. The pasted console was from the intended E run, but uploaded files corresponded to a stale C/D-style run.
2. The E run agent was not repatched correctly and behaved like C/D.
3. The difference is a minor artifact selection/upload mismatch.
```

Decision:

```text
Seed E is weak either way. Do not submit.
```

Required validation if revisiting E:

```python
from pathlib import Path
agent_e = Path('/kaggle/working/runs-20260701-142957-pm-gated-v1-seed-sweep-e/my_agent.py').read_text()
idx = agent_e.find('_stable_seed')
print(agent_e[idx:idx+500])
```

Expected seed line:

```python
seed = _stable_seed('pm_gated_v1_seed_e', getattr(s, 'game_id', 'unknown'))
```

## Completed seed-sweep table

| Seed | Offline score | Levels completed | Progress games | Decision |
|---|---:|---:|---|---|
| control-a | 0.191603 | 2 | sp80, cd82 | weak baseline |
| A | 0.199170 | 3 | sp80, cd82, cn04 | useful breadth |
| B | 0.239723 | 2 | sp80, m0r0 | best single seed |
| C | 0.190476 | 1 | sp80 | weak |
| D | 0.190476 | 1 | sp80 | weak / possible duplicate of C |
| E | 0.191615 pasted; 0.190476 uploaded | likely 1 | likely sp80 only | weak / artifact mismatch |

## Main conclusion

The seed-salt sweep did **not** find a single deterministic seed strong enough for Kaggle submission.

Current best single deterministic seed remains:

```text
Seed B
score = 0.2397231228026976
progress games = sp80, m0r0
```

Current best breadth seed remains:

```text
Seed A
score = 0.19916968479246552
progress games = sp80, cd82, cn04
```

The repeated pattern is:

```text
sp80 is robust across seeds.
m0r0 appears under seed B.
cd82 and cn04 appear under seed A.
C/D/E add no useful new standalone behavior.
```

Therefore, the next experiment should not be another global seed sweep. The next controlled experiment should be a **per-game deterministic seed schedule**.

## What worked

- The remaining C/D/E runs completed with `exit_code = 0`.
- The seed sweep produced a clear ranking.
- The workflow now has enough evidence to stop broad global seed search.
- `sp80` was confirmed as a robust recurring progress game.
- Seed-specific strengths were identified: A for breadth, B for score via `m0r0`.

## What failed / unresolved

- No deterministic seed approached the public `0.38` selected result.
- C/D/E were weak and mainly repeated `sp80` only.
- All games still hit the 502-action cap.
- The agent still tends to solve one level and then burn the remaining action budget.
- D and E artifacts require caution because C/D/E outputs look very similar and E has a pasted-vs-uploaded score mismatch.
- The true cause of the original `0.38` public run remains unresolved.

## Current best score/result

```text
Best public score: 0.38 — keep selected
Best offline single seed: B, 0.239723
Best offline breadth seed: A, 3 progress games
Current submission decision: do not submit A/B/C/D/E as-is
```

## Files / artifacts referenced

Notebook/workbench:

```text
arc3-inspection-tuning-workbench-20260629-seed-control.ipynb
```

Run directories:

```text
/kaggle/working/runs-20260630-114732-pm-gated-v1-seed-sweep-a
/kaggle/working/runs-20260630-120047-pm-gated-v1-seed-sweep-b
/kaggle/working/runs-20260701-140721-pm-gated-v1-seed-sweep-c
/kaggle/working/runs-20260701-142127-pm-gated-v1-seed-sweep-d
/kaggle/working/runs-20260701-142957-pm-gated-v1-seed-sweep-e
```

Artifacts reviewed:

```text
summary.txt
summary.csv
scorecard.json
diagnostic_summary.csv
diagnostic_summary_enriched.csv
pasted notebook console outputs
```

## Next session plan

### P1: Validate seed patching integrity

Before new experiments, add a small verification cell to the notebook:

```python
from pathlib import Path

agent_src = Path('/kaggle/working/my_agent.py').read_text()
expected = EXPERIMENT['seed_salt']
assert expected in agent_src, f'Expected seed_salt {expected} not found in patched agent.'
print('Verified patched seed_salt:', expected)
```

Also inspect saved run agents for C/D/E if needed:

```python
for rd in [
    '/kaggle/working/runs-20260701-140721-pm-gated-v1-seed-sweep-c',
    '/kaggle/working/runs-20260701-142127-pm-gated-v1-seed-sweep-d',
    '/kaggle/working/runs-20260701-142957-pm-gated-v1-seed-sweep-e',
]:
    p = Path(rd) / 'my_agent.py'
    print('\n', rd)
    txt = p.read_text()
    idx = txt.find('_stable_seed')
    print(txt[idx:idx+500])
```

### P1: Run per-game seed schedule A/B

New experiment:

```text
pm-gated-v1-per-game-seed-schedule-ab
```

Seed schedule idea:

```text
sp80  -> seed B or A
m0r0  -> seed B
cd82  -> seed A
cn04  -> seed A
all others -> seed B
```

Diagnostic upper bound from A+B:

```text
sp80  = 4.761905
m0r0  = 1.231173
cd82  = 0.138929
cn04  = 0.078408
sum   = 6.210415
score = 6.210415 / 25 = 0.248417
levels = 4
```

This is not a proven score. It is the target diagnostic for checking whether per-game seed routing can combine the best discoveries from A and B.

Suggested control settings:

```python
EXPERIMENT = {
    'description': 'pm-gated-v1-per-game-seed-schedule-ab',
    'run_game': 'all',
    'max_actions_cap': 501,
    'save_recordings': False,

    'scan_timeout': 2,
    'bfs_timeout': 35,
    'max_states': 75000,
    'max_depth': 18,

    'deterministic_seed': True,
    'seed_salt': 'pm_gated_v1_seed_b',
    'per_game_seed_salts': {
        'sp80': 'pm_gated_v1_seed_b',
        'm0r0': 'pm_gated_v1_seed_b',
        'cd82': 'pm_gated_v1_seed_a',
        'cn04': 'pm_gated_v1_seed_a',
    },

    'enable_soft_loop_pruning': False,
    'no_change_penalty': 0.0,
    'repeat_state_action_penalty': 0.0,
    'patch_agent_after_write': True,
}
```

Implementation requirement:

```text
The seed utility must choose a per-game salt if present, otherwise default to seed_salt.
```

Pseudo-code:

```python
per_game_seed_salts = {
    'sp80': 'pm_gated_v1_seed_b',
    'm0r0': 'pm_gated_v1_seed_b',
    'cd82': 'pm_gated_v1_seed_a',
    'cn04': 'pm_gated_v1_seed_a',
}

gid = getattr(s, 'game_id', 'unknown')
salt = per_game_seed_salts.get(gid, 'pm_gated_v1_seed_b')
seed = _stable_seed(salt, gid)
```

Promotion thresholds:

```text
Weak promotion / inspect further: score >= 0.25 or levels completed >= 4
Strong promotion / possible scoring notebook: score >= 0.30 or levels completed >= 5
```

### P2: Targeted recordings after schedule test

If the per-game schedule reaches or exceeds the weak promotion gate, run targeted recordings for:

```text
sp80
m0r0
cd82
cn04
```

Use:

```text
run_game = one selected game
max_actions_cap = 1000
save_recordings = True
```

Main diagnostic question:

```text
Why does the agent solve one level and then fail to transfer or continue efficiently to level 1?
```

## Do not do next

```text
Do not submit A/B/C/D/E as-is.
Do not run another broad global seed sweep yet.
Do not expand BFS budget.
Do not add loop/no-change pruning.
Do not enable full recordings for all games.
Do not generate a Kaggle scoring notebook until a candidate passes the offline promotion gate.
```
