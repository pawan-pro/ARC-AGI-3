# ft09 Mask-Cycle Helper Result

Date: 2026-07-11

Experiment: `EXP-DUCK-004`

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-ft09-mask-cycle
```

Artifacts:

```text
artifacts/kaggle/duck_ft09_mask_cycle/latest/
```

## Result

The run completed, but it was not a valid test of the level-4 mask-cycle helper.

```text
label: duck-harness-kaggle-duck-ft09-mask-cycle-20260710
game: ft09-0d8bbf25
score: 0.00
levels: 0 / 6
actions_per_level: [180, 0, 0, 0, 0, 0]
tokens: 57,143
solver_note: controlled_stall=no_level_progress_actions>=180; tokens=57143
```

The solver never reached level 3 or level 4. The new level-4 helper only activates on level 4, so it did not run. The successful level-3 helper also did not run, because the solver stalled on level 1.

## Comparison

| Run | ft09 levels | actions_per_level | tokens | Meaning |
|---|---:|---|---:|---|
| Baseline Duck | 2 / 6 | `[42, 21, 19, 0, 0, 0]` | 70,043 | LLM solved early levels, then stopped before level 3 completion |
| Stall policy | 2 / 6 | `[29, 7, 90, 0, 0, 0]` | 71,628 | Preserved early progress, reduced some waste elsewhere |
| Level-3 helper | 3 / 6 | `[9, 7, 32, 172, 0, 0]` | 100,578 | Positive result; helper solved level 3 |
| Mask-cycle alpha | 0 / 6 | `[180, 0, 0, 0, 0, 0]` | 57,143 | Invalid level-4 test; early stochastic failure |

## Diagnosis

K-12 version: we built a tool for the fourth room, but the player got stuck in the first room, so the tool never got a chance to help.

The notebook patch did not intentionally change early-level logic. The diff from the previous successful helper variant only:

- added the level-4 helper methods,
- added a level-4 play-loop hook after the level-3 helper hook,
- set `ft09_mask_cycle_helper_policy`,
- raised the safety action cap from 220 to 260.

Because the helper is gated to level 4, the 0/6 result is best treated as run variance or early policy instability, not as evidence against the mask-cycle idea.

## Next Experiment

To test level 4 cleanly, isolate it:

1. Replay the known successful `ft09` prefix from the positive helper run through level 3.
2. Stop after reaching level 4.
3. Run the mask-cycle helper on level 4.
4. Compare only level-4 actions and outcome.

This should be recorded as a diagnostic experiment, not as a leaderboard candidate, because replaying a known prefix is for understanding the mechanic rather than proving generalization.
