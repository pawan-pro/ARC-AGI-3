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

Pending static validation and private kernel launch.
