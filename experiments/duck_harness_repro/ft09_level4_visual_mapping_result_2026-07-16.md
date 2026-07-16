# ft09 Level-4 Visual Mapping Result

Date: 2026-07-16

Experiment: `EXP-DUCK-007`

Source:

```text
artifacts/kaggle/duck_ft09_level4_exhaustive/latest/artifacts/ft09-0d8bbf25_p0_events.jsonl
```

Reproducible inspector:

```text
experiments/duck_harness_repro/ft09_level4_visual_mapping.py
```

## Result

The level-4 board contains 18 editable color blocks and three fixed clue cells.
The missing invariant is **overlap consistency**: two clues that describe the
same editable block must assign it the same color.

The earlier candidates guessed a global vote rule such as majority, parity, or
"orange wins." That is the wrong model. The overlapping clue windows determine
the gray mapping before any voting is needed.

## How the Mapping Is Forced

Prior levels establish that a white mask position uses its clue's center color.
Gray must represent a different color from that center.

Level 4 uses the palette `b -> R -> O -> b` and has clue centers `O`, `b`, `O`:

| Clue center | Possible gray colors |
|---|---|
| `O` at `(24,22)` | `b` or `R` |
| `b` at `(24,38)` | `R` or `O` |
| `O` at `(40,30)` | `b` or `R` |

Their neighborhoods overlap at gray positions. Those shared blocks must have
one color, and the only color present in all three possibility sets is `R`.

Therefore the unique conflict-free interpretation is:

```text
white -> that clue's center color
gray  -> red
```

The script enumerated all allowed gray assignments and found exactly one
conflict-free solution. All 18 editable blocks are covered; none are left
unknown.

## Proposed Target

`C` marks a fixed clue cell and `.` marks no block.

```text
R O R b R
R C R C R
R O R R b
. R C R .
. O O O .
```

In the truth-table center order:

```text
RORbRRRRRORRbRROOO
```

Starting from all blue, this target needs 21 clicks:

```text
blue -> red:    11 blocks x 1 click
blue -> orange:  5 blocks x 2 clicks
blue stays blue: 2 blocks x 0 clicks
```

## Why the Exhaustive Run Missed It

None of the five completed/partial candidates represented this rule. The
closest attempted candidate was candidate 5, but it still differed at seven
editable blocks and triggered `GAME_OVER` before completion.

The current helper mixes per-clue guesses with majority/parity/color-wins
reducers. It never asks the simpler constraint question: "Which gray color
makes every overlap agree?"

## K-12 Explanation

Imagine three small transparent clue cards placed over one larger board. Some
squares are covered by two cards. If one card says a shared square is red and
the other says it is blue, that interpretation cannot be right.

For each clue, white copies the color in the clue's middle. Gray must be one of
the other colors. When we line up all three cards, only **red** makes every
shared square agree. That gives one complete answer board, with no guessing and
no voting contest.

## Next Experiment

Create `EXP-DUCK-008`: replay the known 48-action prefix, apply only the 21-click
overlap-consistent target, and stop immediately.

Acceptance gate:

```text
ft09 improves from 3/6 to at least 4/6
no blind candidate cycling
no LLM tokens needed for the isolated test
```

Do not run the full evaluation notebook until this targeted candidate is
confirmed or rejected.
