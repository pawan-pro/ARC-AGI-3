# ft09 Mask-Cycle Helper Plan

Date: 2026-07-10

Experiment: `EXP-DUCK-004`

Notebook variant:

```text
notebooks/04_submission_builds/duck_public_repro_terminal_run/arc3_20260704_duck_public_repro_ft09_mask_cycle.ipynb
```

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-ft09-mask-cycle
```

## Why this experiment exists

The `ft09` level-3 helper proved that some ARC-AGI-3 games can benefit from small deterministic tools that translate visual clues into low-level actions. It raised `ft09` from 2/6 levels to 3/6 levels, but then the solver spent 172 actions on level 4 without completing it.

Level-4 inspection showed the same broad family:

- grid cells with colored centers
- nearby mask or clue pixels
- a click cycle where normal cells rotate through colors
- progress likely requires choosing which cells to toggle, not inventing a new prompt

K-12 version: level 3 was like reading a tiny secret map and flipping the right squares. Level 4 looks like the same kind of puzzle, except each square can cycle through more than two colors. So this experiment gives the solver a small "color wheel helper" instead of asking the language model to spend many guesses.

## Change

This variant keeps the successful level-3 helper and adds a gated level-4 mask-cycle helper for `ft09-0d8bbf25`.

The helper:

1. Runs only on `ft09`.
2. Runs only on level 4.
3. Reads sampled board-cell center colors.
4. Builds compact candidate target color layouts from the observed white/gray/orange clue masks.
5. Converts each target layout into the shortest click sequence using the observed cycle:

```text
b -> R -> O -> b
```

6. Stops immediately if the level score advances.
7. Falls back to the original LLM loop if the helper does not solve the level.

## Guardrails

- No global prompt change.
- No model change.
- No broad solver behavior change.
- Max actions increased from 220 to 260 so level 4 has room to try a compact candidate set.
- This is an alpha helper, not the final generalized mask parser. It still uses the observed level-4 board layout as a controlled test before we generalize.

## Acceptance Criteria

Positive result:

- keep `ft09` level 3 solved, and
- either solve level 4, or
- reduce level-4 waste below the prior 172 actions while preserving progress.

Negative result:

- level 3 regresses, or
- level 4 still consumes most of the budget without progress.

## Next Decision

If this helps, generalize the helper into a reusable mask/toggle kernel:

- detect board cell centers instead of listing them
- infer the color cycle from clicks
- extract clue masks automatically
- expose a small trace table so the LLM can choose among candidates

If this does not help, inspect the level-4 replay to decide whether the missing piece is object grouping, parity, or a different clue-to-cell mapping.
