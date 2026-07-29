# EXP-DUCK-033: ft09 Level-5 Magenta Mechanic Probes

## Question

EXP-DUCK-031 and EXP-DUCK-032 tested both complementary colorings of all
ordinary level-5 cells. Both targets were executed exactly, but neither advanced
the level. The remaining unexplained objects are three magenta cells.

Do those cells act as controls, locks, clues, or ordinary fixed obstacles?

## Controlled Design

Run three independent private Kaggle notebooks. Every arm:

1. Replays the validated 69-action prefix to reach untouched level 5.
2. Clicks exactly one magenta-cell center.
3. Records the clicked cell before and after, every changed pixel, level
   transition, game-over state, and run-complete state.
4. Stops immediately.

| Arm | Probe center |
|---|---|
| top | `(row=14, col=24)` |
| middle | `(row=30, col=24)` |
| bottom-right | `(row=46, col=40)` |

## Safety Gates

- Private diagnostic kernels only.
- No LLM fallback and zero generated tokens.
- Exactly 70 actions per arm: 69 validated prefix actions plus one probe.
- No full evaluation.
- No competition submission.
- Reject the experiment if any arm does not begin from the same untouched
  level-5 state or performs more than one probe.

## Decision Rule

A magenta mechanic is identified only if a probe has an observable effect
different from an ordinary one-cell color cycle, changes other cells, advances
the level, or causes game over. If all three probes are inert or ordinary local
cycles, return to the visual clue model rather than guessing more targets.

## Launch Status

Static validation passed. Commit `5ab9039` contains the reproducible package.

Kaggle accepted Version 1 of:

- `jatalepawan/arc-agi-3-duck-ft09-level-5-probe-top`
- `jatalepawan/arc-agi-3-duck-ft09-level-5-probe-middle`

Both kernels were confirmed `RUNNING`. Kaggle rejected the simultaneous
bottom-right launch because the account's maximum of two batch GPU sessions was
already in use. The bottom-right notebook remains unchanged and will be pushed
as soon as either active arm releases a slot.

No competition submission was made.

## Partial Live Result

The top and middle arms completed with the exact 69-action prefix plus one
probe, zero tokens, no game over, and no level transition.

```text
top probe:    color 14 -> 15; 164 pixels changed
middle probe: color 14 -> 15; 128 pixels changed
```

These are not ordinary one-cell color cycles. Each magenta cell is a regional
operator that changes a structured group of cells.

The first two bottom-right launch attempts failed before gameplay because
Kaggle mounted the competition at `/kaggle/input/arc-prize-2026-arc-agi-3`
but the inherited notebook expected
`/kaggle/input/competitions/arc-prize-2026-arc-agi-3`. Both failures occurred
while installing `arc-agi`; neither reached the validated prefix or probe.

The bottom-right notebook now resolves either Kaggle mount layout. The probe
coordinate and all game logic remain unchanged.
