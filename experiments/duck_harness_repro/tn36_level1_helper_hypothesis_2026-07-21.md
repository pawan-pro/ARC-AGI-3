# tn36 Level-1 Deterministic Helper Hypothesis

Date: 2026-07-21

The EXP-DUCK-009 trace solved `tn36` level 1 in eight actions:

1. one unnecessary click on the clue;
2. click each of six blue three-pixel bars exactly once;
3. click the large yellow submit object.

The final submit advanced to level 2 and changed 2,428 visible cells. The baseline trace used the same initial board but repeatedly clicked partial subsets, revisited toggles, and reset without completing the six-object pattern.

The proposed helper removes the unnecessary clue click and plans seven actions. It activates only when all of these structural guards match:

- game `tn36-ef4dde99`, level 1;
- exactly six blue rectangular components of three pixels;
- centers at the observed two-row layout;
- exactly one non-rectangular yellow component of 69 pixels;
- the two clue components have sizes 14 and 16.

Both stored initial boards produce the same seven-action plan. A one-cell signature mutation is rejected.

## K-12 Explanation

The top picture is the instruction card. The six tiny blue bars are the answer switches. The successful solver turned on every answer switch once and then pressed the big yellow check button. The failed solver kept changing only some switches and starting over.

Next gate: inject this helper into an isolated `tn36` run and require level 1 to advance in exactly seven actions before adding it to a full submission candidate.
