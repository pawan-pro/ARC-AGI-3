# EXP-DUCK-031: ft09 Level-5 Prospective Gate

## Goal

Test the hypothesis-first learner on an ft09 level for which we have no known
successful actions.

## Prospective Boundary

The learner receives:

- The validated levels 1-4 replay path.
- The untouched level-5 board shown after level 4 completes.

The learner does not receive:

- Any level-5 action.
- Any level-5 success trace.
- The ft09 game source.
- A stored level-5 target or coordinate list.

## Frozen Hypothesis

The pixel learner found:

```text
27 editable cells
11 clue cells
2 state colors
4 mark colors
8-pixel spacing
```

Two semantic descriptions survive because one gray mark never changes the
answer of an editable cell. Both descriptions produce the same actionable
target:

```text
18 cells should change
9 cells are already correct
1 unique target signature
```

This is acceptable action-level certainty. The uncertain mark cannot alter any
planned click.

## Guarded Execution

The isolated notebook will:

1. Replay the already validated 48-action prefix through level 3.
2. Apply the validated 21-click level-4 overlap solution.
3. Recompute the level-5 target from the live board.
4. Click only the 18 cells that differ from the frozen target.
5. After every click, require the observed cell to equal the predicted state.
6. Stop immediately on a prediction mismatch, game over, ambiguity, or level
   completion.
7. Stop after the helper; do not call the LLM on level 5.

## Pre-Run Gates

Passed:

- Four focused learner tests.
- Zero known level-5 actions.
- No stored level-5 coordinates.
- Binary state palette discovered.
- Geometry discovered from pixels.
- One actionable target signature.
- Two equivalent semantic models.
- Eighteen guarded clicks.
- Nine cells already correct.
- Notebook code compiles and contains the guarded play hook.

## Kaggle

Private kernel:

```text
jatalepawan/arc-agi-3-duck-ft09-level-5-prospective
```

Competition submission:

```text
No
```

Promotion rule:

```text
Build a full evaluation only if the isolated run advances from level 5 to
level 6 with all predicted effects intact.
```
