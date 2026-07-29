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

## Final Live Result

The corrected bottom-right Version 4 completed. All three arms passed:

| Arm | Logical cells toggled | Changed pixels | Level gain |
|---|---:|---:|---:|
| top | 4 | 164 | 0 |
| middle | 3 | 128 | 0 |
| bottom-right | 4 | 164 | 0 |

Every run:

```text
validated prefix: 69 actions
probe actions: 1
total actions: 70
tokens: 0
game over: false
structural gate: PASS
```

The logical masks are:

```text
top:
  (6,24), (14,16), (14,32), (22,24)

middle:
  (22,24), (30,16), (30,32)

bottom-right:
  (38,40), (46,32), (46,48), (54,40)
```

Top and middle overlap at `(22,24)`. This establishes that the three magenta
cells are deterministic regional toggle operators. None of the three single
operator states is the answer.

## Decision

EXP-DUCK-033 passes as a mechanic-identification experiment. It does not add a
level and is not eligible for a full evaluation or competition submission.

## Next Gate: EXP-DUCK-034

Three binary operators create only eight states. Starting from the untouched
state, use a seven-step Gray-code route that visits every non-empty combination
while changing only one operator at each step:

```text
1. top          -> top
2. middle       -> top + middle
3. top          -> middle
4. bottom-right -> middle + bottom-right
5. top          -> top + middle + bottom-right
6. middle       -> top + bottom-right
7. top          -> bottom-right
```

After each click, compare the complete observed board with the XOR prediction.
Stop immediately on level completion. Abort on any prediction mismatch or game
over. This is exhaustive search over a measured three-bit control space, not an
open-ended action guess.

Visual audit:

```text
artifacts/kaggle/duck_ft09_magenta_probe_audit/index.html
```

Competition submission: **NO**.
