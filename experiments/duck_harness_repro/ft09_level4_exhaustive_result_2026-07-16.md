# ft09 Level-4 Exhaustive Candidate Diagnostic Result

Date: 2026-07-16

Experiment: `EXP-DUCK-006`

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-ft09-level4-exhaustive
```

Artifacts:

```text
artifacts/kaggle/duck_ft09_level4_exhaustive/latest/
```

## Result

The run completed, but the helper did not solve level 4.

```text
label: duck-harness-kaggle-duck-ft09-level4-exhaustive-20260715
game: ft09-0d8bbf25
score: 23.80859375
levels: 3 / 6
actions_per_level: [9, 7, 32, 142, 0, 0]
total actions: 190
tokens: 126,904
solver_note: ft09_mask_cycle=level4:white_is_center+orange_wins; helper_actions=96; candidates=5; ft09_prefix_replay_actions=48; reached_level=4; target_level=4
```

The replay prefix again reached level 4 at action 48.

## Candidate Trace

The direct candidate trace JSON was not present in the downloaded artifacts, so the trace below was reconstructed from:

```text
artifacts/kaggle/duck_ft09_level4_exhaustive/latest/artifacts/ft09-0d8bbf25_p0_events.jsonl
```

using:

```text
experiments/duck_harness_repro/ft09_level4_truth_table.py
```

| Candidate | Actions | Completed? | Stop reason | Before centers | Target centers | After centers |
|---|---:|---|---|---|---|---|
| `level4:gray_is_center+blue_wins` | 12 / 12, actions 49-60 | yes | none | `bbbbbbbbbbbbbbbbbb` | `ObbRbObbObbbROObbb` | `ObbRbObbObbbROObbb` |
| `level4:white_cycles_from_center+parity` | 15 / 15, actions 61-75 | yes | none | `ObbRbObbObbbROObbb` | `RbbRORbORbRbRRRbbb` | `RbbRORbORbRbRRRbbb` |
| `level4:white_is_center+majority` | 30 / 30, actions 76-105 | yes | none | `RbbRORbORbRbRRRbbb` | `bObbRbbRbObbbbbOOO` | `bObbRbbRbObbbbbOOO` |
| `level4:gray_is_center+majority` | 23 / 23, actions 106-128 | yes | none | `bObbRbbRbObbbbbOOO` | `ObbRbObbObObROObbb` | `ObbRbObbObObROObbb` |
| `level4:white_is_center+orange_wins` | 16 / 24, actions 129-144 | no | `GAME_OVER`, then `RESET` | `ObbRbObbObObROObbb` | `bORbRbRRbObbbbbOOO` | `bORbRbRRbObbbOObbb` |

Candidates 6-8 were not reached because candidate 5 triggered game over.

## Interpretation

K-12 version: we removed the safety timer that stopped the helper too early. The helper got farther this time, but the fifth answer was bad enough to lose the room. So we still did not see all 8 answers, and none of the first 5 solved the room.

What this tells us:

- the zero-token stall guard was no longer the blocker
- the helper can execute candidate layouts exactly
- candidate 5 is harmful and should be treated as a losing mapping
- the current clue-to-target mapping family is probably wrong
- continuing to add blind candidate guesses is not the right next move

## Important Bug

The direct candidate trace JSON did not appear in downloaded Kaggle artifacts. The helper wrote to `_artifacts_dir()`, but Kaggle output packaging did not include the expected `*_ft09_level4_candidate_trace.json` file.

For future trace artifacts, write through the same sidecar/event mechanism used by the viewer, or write to a location already known to be included in notebook outputs.

## Next Step

Stop candidate guessing for level 4.

Recommended next experiment:

```text
EXP-DUCK-007: ft09 level-4 visual clue mapping inspection
```

Instead of running more candidate layouts, inspect the level-4 board directly:

1. Identify which visible objects are actual editable cells versus clues.
2. Build a coordinate map of all 18 normal centers and 3 special clue centers.
3. Compare the initial level-4 board to candidate 1-5 after states.
4. Look for any visual invariant that remained unsatisfied before game over.
5. Only then write a corrected level-4 helper.

Evaluation notebook gate remains unchanged: do not run a full evaluation notebook until a targeted run improves `ft09` from 3/6 to at least 4/6, or until this helper generalizes to another game family.
