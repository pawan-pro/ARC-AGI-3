# 2026-06-24 Session Notes — v1 Instability and Seed-Control Next Step

## Session context

We continued ARC Prize 2026 / ARC-AGI-3 experiments from the Persistent Memory short/gated-BFS line.

Best observed public score before this session:

```text
Persistent Memory short/gated-BFS v1 — Version 1: 0.38
```

This score placed the project around the reported public bronze/silver boundary region, with an approximate rank previously reported around `~100 / 1355`. The user also noted the public/private leaderboard caveat: the public leaderboard is calculated on approximately 50% of the test data, while final standings use the other 50%.

## What was reviewed today

### 1. Loop/no-change pruning result

Latest loop-pruning scoring result:

```text
notebook1be3ebd1f3 - Version 1
Status: Succeeded
Public Score: 0.24
```

This notebook was based on the validated `0.38` Persistent Memory short/gated-BFS v1 baseline and added soft loop/no-change action pruning.

Interpretation:

- The notebook ran successfully.
- The score dropped from `0.38` to `0.24`.
- This was a real policy regression, not a build or Kaggle error.
- The pruning layer likely interfered with necessary exploration/backtracking or useful repeated actions.

Decision:

```text
Reject loop/no-change pruning v1.
Return to the validated short/gated-BFS v1 baseline.
```

Likely failure causes:

- no-change penalties were too strong,
- state hashes may have been too coarse,
- useful revisits/backtracking may have been treated as loops,
- repeated actions may be required by some game mechanics,
- pruning may have conflicted with BFS replay / PersistentAEM / PER / CLEAR / TTT.

### 2. Exact v1 rerun / Version 2 result

The user then submitted an exact/rerun version of the current best notebook:

```text
Persistent Memory short/gated-BFS v1 - Version 2
Status: Succeeded
Public Score: 0.20
```

Comparison:

```text
Persistent Memory short/gated-BFS v1 — Version 1: 0.38
Persistent Memory short/gated-BFS v1 — Version 2: 0.20
```

This is a large instability signal.

Interpretation:

- The notebook appears to have run/build correctly.
- The v1 method can produce a high score of `0.38`, but the behavior is not yet stable across submissions.
- The likely cause is stochastic exploration / time-based seeding / process-randomized Python hash behavior.

Key suspected seed pattern:

```python
seed = int(time.time() * 1e6) + hash(s.game_id) % 1000000
random.seed(seed)
np.random.seed(seed % (2 ** 32 - 1))
torch.manual_seed(seed % (2 ** 32 - 1))
```

Issues:

- `time.time()` changes every run.
- Python built-in `hash()` can vary between processes unless `PYTHONHASHSEED` is fixed.
- Small exploration differences can cascade into large public-score changes.

## Updated experiment ladder

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

## Main conclusion

The key conclusion changed from:

```text
Can we improve beyond 0.38?
```

to:

```text
Can we make the 0.38 behavior repeatable?
```

Current best observed score remains:

```text
0.38
```

But stable expected score is now uncertain.

## Decision

Do not continue broad architecture changes yet.

Reject:

- larger BFS-budget expansion,
- hard or blunt loop/no-change pruning,
- another unseeded/random rerun as the main experiment.

Next best experiment:

```text
Persistent Memory short/gated-BFS v1 — deterministic seed control
```

Purpose:

```text
Remove time-based randomness and make behavior reproducible.
```

Proposed deterministic seed utility:

```python
import hashlib

def stable_seed(game_id, level_idx=0, salt="pm_gated_v1"):
    key = f"{salt}:{game_id}:{level_idx}".encode()
    return int(hashlib.md5(key).hexdigest()[:8], 16)
```

Use this instead of wall-clock time and Python process-randomized `hash()`.

## Decision matrix for deterministic v1

| Deterministic v1 score | Interpretation | Next action |
|---:|---|---|
| 0.36–0.40 | Strong behavior stabilized. | Promote deterministic v1 as preferred baseline. |
| 0.30–0.35 | Stable but weaker; useful reproducible baseline. | Tune seed salt / controlled exploration. |
| 0.20–0.29 | The 0.38 was likely a lucky stochastic run. | Keep 0.38 selected but improve robustness. |
| < 0.20 | Deterministic policy locked into poor exploration. | Try small seed ensemble / deterministic multi-salt schedule. |
| Kaggle Error | Notebook wrapper issue. | Inspect log; patch wrapper only. |

## What worked

- We validated that the loop-pruning direction, as implemented, is too restrictive.
- We performed a v1 rerun/control check.
- The rerun exposed major instability, which is valuable before further changes.
- We identified deterministic seed control as the next highest-value experiment.

## What failed / unresolved

- Loop/no-change pruning dropped to `0.24`.
- Exact v1 rerun dropped to `0.20`, showing high variance.
- Stable expected score of the v1 architecture is unknown.
- The cause of the `0.38` versus `0.20` spread is not proven, but seeding/stochasticity is the leading hypothesis.
- We still need to preserve the best observed `0.38` submission as selected while testing reproducibility.

## Current best score/result

```text
Best observed public score: 0.38
Best observed notebook: Persistent Memory short/gated-BFS v1 — Version 1
Latest rerun/control score: 0.20
Conclusion: v1 is high-variance / seed-sensitive
```

## Files / artifacts referenced

Uploaded artifacts reviewed by user during this session:

```text
notebook1be3ebd1f3.log
persistent-memory-short-gated-bfs-v1.log
persistent-memory-short-gated-bfs-v1.ipynb
```

Session note created:

```text
session_notes/2026-06-24_v1_instability_and_seed_control_next.md
```

## Next session plan

1. Create a deterministic-seed version of Persistent Memory short/gated-BFS v1.
2. Replace wall-clock and Python-hash seeding with stable `hashlib`-based seeds.
3. Keep the validated v1 BFS budget unchanged.
4. Submit deterministic v1 for scoring.
5. Compare against both `0.38` best observed and `0.20` rerun result.
6. If deterministic score is stable but lower, test controlled seed salts rather than changing architecture.
7. Keep the `0.38` submission selected unless a new run beats it.
