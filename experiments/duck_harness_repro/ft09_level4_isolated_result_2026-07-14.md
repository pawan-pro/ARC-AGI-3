# ft09 Level-4 Isolated Diagnostic Result

Date: 2026-07-14

Experiment: `EXP-DUCK-005`

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-ft09-level4-isolated
```

Artifacts:

```text
artifacts/kaggle/duck_ft09_level4_isolated/latest/
```

## Result

The diagnostic run succeeded as an isolation test, but the level-4 mask-cycle helper did not solve level 4.

```text
label: duck-harness-kaggle-duck-ft09-level4-isolated-20260713
game: ft09-0d8bbf25
score: 23.80859375
levels: 3 / 6
actions_per_level: [9, 7, 32, 72, 0, 0]
total actions: 120
tokens: 0
solver_note: ft09_prefix_replay_actions=48; reached_level=4; target_level=4
```

## What It Proved

The replay prefix is portable enough for this diagnostic:

```text
action 9  -> level 2
action 16 -> level 3
action 48 -> level 4
```

After reaching level 4, the mask-cycle helper executed 72 additional zero-token actions. The board changed on those clicks, but the level score did not advance beyond 3.

K-12 version: we successfully carried the player to room 4, then tried the color-wheel tool. The tool changed tiles, but it did not unlock the room.

## Comparison

| Run | ft09 levels | actions_per_level | tokens | Meaning |
|---|---:|---|---:|---|
| EXP-DUCK-003 level-3 helper | 3 / 6 | `[9, 7, 32, 172, 0, 0]` | 100,578 | Solved level 3, then LLM wandered on level 4 |
| EXP-DUCK-004 mask-cycle alpha | 0 / 6 | `[180, 0, 0, 0, 0, 0]` | 57,143 | Invalid level-4 test because solver stalled on level 1 |
| EXP-DUCK-005 isolated level 4 | 3 / 6 | `[9, 7, 32, 72, 0, 0]` | 0 | Valid level-4 test; helper did not solve level 4 |

The helper reduced level-4 waste from 172 actions to 72 actions by stopping after candidate exhaustion, but it did not improve score.

## Diagnosis

The broad family assumption was useful: level 4 is clickable and the color cycle exists. The failed part is likely the clue-to-target mapping, not the action executor.

Most likely issues:

1. The hardcoded level-4 cell centers or special cells are incomplete.
2. The rule that maps white/gray/orange mask pixels to target colors is wrong.
3. Level 4 may require an ordering or multi-step transformation, not a single final target layout.
4. Some visible colored pieces may be hints rather than cells to set.

## Next Step

Inspect the isolated level-4 replay frame-by-frame and build a small level-4 truth table:

```text
for each helper candidate:
  candidate name
  clicked cells
  before center colors
  after center colors
  changed pixels
  whether any special mask changed
```

Then either:

- add a level-4-specific candidate generator with the corrected clue mapping, or
- build a generic mask/toggle search that learns the mapping from probe clicks instead of guessing it.
