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

## Live Result

The private Kaggle kernel completed successfully.

```text
levels completed: 4/6
actions per level: [9, 7, 32, 21, 18, 0]
total actions: 87
tokens: 0
level-5 helper actions: 18
correct observed effects: 18/18
final target mismatches: 0
level-5 progress: 0
```

The validated 69-action prefix reached level 5. The prospective helper then
activated and made exactly its 18 frozen clicks. Every selected cell changed
from the observed starting color to the predicted target color. After the
last click, all 27 editable cells matched the inferred target.

The game nevertheless remained on level 5.

## K-12 Interpretation

The helper had good hands but the wrong answer sheet.

- It found every square it intended to change.
- Every click did exactly what it expected.
- It finished the exact picture it had planned.
- The game said that picture was not the solution.

This rejects the objective hypothesis, not the mouse-control mechanism.
Level 5 needs more than the simple rule that each mark means either "copy the
clue center" or "flip the clue center."

## Decision

```text
structural validation: PASS
prospective level-gain gate: FAIL
build full evaluation: NO
competition submission: NO
```

EXP-DUCK-031 is a useful prospective falsification. It prevents us from
shipping a confidently executed but incorrect objective into all 25 games.

## Next Gate

The next experiment should learn richer operator meanings from solved ft09
levels 1-4:

1. Reconstruct each solved level's initial board and accepted final target.
2. Fit mark-specific operators across levels rather than one global
   same-or-flip table.
3. Hold out one solved level and require exact target prediction.
4. Revisit level 5 only if the calibrated model produces one unique target
   that differs from the rejected EXP-DUCK-031 target.

No full evaluation or competition scoring run should be launched before that
calibration gate passes.
