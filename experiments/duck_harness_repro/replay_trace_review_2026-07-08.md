# Duck Replay Trace Review - 2026-07-08

This note summarizes the first visual/trace pass over the Duck public repro and the controlled stall-policy run.

## Runs Reviewed

Baseline:

```text
artifacts/kaggle/duck_public_repro_terminal_run/latest/benchmark.json
```

Controlled stall run:

```text
artifacts/kaggle/duck_controlled_stall_policy/latest/benchmark.json
```

Replay index:

```text
artifacts/kaggle/duck_controlled_stall_policy/latest/target_game_replay_index.html
```

Important caveat: the first controlled stall run accidentally played all 25 games. The notebook filtered `bm.games`, then the run cell rebuilt the game list later. The corrected notebook now applies the target-game filter after construction of the live/offline game list.

## Target Game Results

| game | baseline levels | baseline actions | baseline tokens | controlled levels | controlled actions | controlled tokens | readout |
|---|---:|---:|---:|---:|---:|---:|---|
| `ft09-0d8bbf25` | 2/6 | 82 | 70,043 | 3/6 | 110 | 96,551 | Real puzzle understanding. Preserve and convert into a deterministic helper. |
| `tn36-ef4dde99` | 0/7 | 122 | 69,693 | 1/7 | 99 | 19,376 | Stall policy saved tokens and even found one level. Needs replay review before broadening. |
| `sc25-635fd71a` | 0/6 | 147 | 70,194 | 0/6 | 90 | 41,110 | Stall policy reduced waste; no evidence of useful late progress. |
| `tr87-cd924810` | 0/6 | 330 | 61,632 | 0/6 | 90 | 16,439 | Biggest waste reduction. Long action loops should be cut earlier. |

## Clean Four-Game Rerun

After fixing the target filter, the controlled stall notebook ran only:

```text
tn36-ef4dde99
sc25-635fd71a
ft09-0d8bbf25
tr87-cd924810
```

Fresh run summary:

| game | baseline | controlled stall | readout |
|---|---:|---:|---|
| `ft09-0d8bbf25` | 2/6, 82 actions, 70,043 tokens | 2/6, 126 actions, 71,628 tokens | Preserved progress, but did not improve efficiency. The first two levels took 29 and 7 actions; level 3 burned 90 actions until cutoff. |
| `tn36-ef4dde99` | 0/7, 122 actions, 69,693 tokens | 0/7, 90 actions, 70,452 tokens | Fewer actions, no token saving. |
| `sc25-635fd71a` | 0/6, 147 actions, 70,194 tokens | 0/6, 90 actions, 50,946 tokens | Useful waste reduction. |
| `tr87-cd924810` | 0/6, 330 actions, 61,632 tokens | 0/6, 90 actions, 33,355 tokens | Strong waste reduction. |

Conclusion: the stall policy is worth keeping as a safety rail, but it is not a scoring strategy. The next scoring work should turn `ft09`'s discovered small-grid rule into direct deterministic clicks, especially to stop level-3 thrashing.

## Solved/Partially Solved Patterns

| game | observed mechanic | what Duck did well | failure mode | next helper candidate |
|---|---|---|---|---|
| `ft09-0d8bbf25` | 3x3 click/toggle grid with Boolean-like relation across examples. | Identified the board as a small symbolic logic puzzle and made level progress through mouse clicks. | Re-discovers rules manually each level and spends many tokens on repeated analysis. | `toggle_grid_helper.py`: infer Boolean rule from examples, compute target grid, click only differing cells. |
| `sb26-7fbdac44` | Palette/slot or color-fill mapping puzzle. | Recognized that colors must be selected and applied to target regions. | Gets stuck on ordering, completion, or submit mechanics after one level. | Palette-slot extractor plus explicit finish/submit probe. |
| `tu93-0768757b` | Movement/path-style interaction. | Solved two levels with action sequencing. | Uses many zero-token repeated actions and does not package discovered route logic. | Replay-derived route macro and early dead-loop detector. |
| `vc33-5430563c` | Click interaction with visible target structure. | Improved to two levels in the controlled run. | Still token-heavy; likely repeats local visual reasoning. | Click-target probe with compact state carryover. |
| `lp85-305b61c3` | Fast early progress in baseline. | Level progress happened with few actions. | Controlled full run changed behavior and spent more actions. | Keep as observational until replay confirms the mechanic. |

## Common Failure Patterns

1. `board_changed=True` is too weak as success evidence. It often means "something changed", not "the level progressed".
2. Duck can infer the puzzle family, but does not reliably turn the inference into a reusable, deterministic policy.
3. The solver repeats low-value actions after the current level stops improving.
4. Token use is dominated by re-analysis of visual state that should be compacted into a small mechanic hypothesis.
5. Submit/completion mechanics are underspecified for some click/fill games.

## Recommended Next Experiments

1. Re-run the corrected controlled stall notebook on only `ft09`, `tn36`, `sc25`, and `tr87`.
2. Accept the stall policy only if `ft09` keeps at least two level transitions and the three stall games spend fewer tokens/actions than baseline.
3. Implement the first deterministic helper for `ft09`, because it has the clearest evidence of reusable logic.
4. Add a similar helper only after replay confirms the exact mechanic for `sb26` or `vc33`.
