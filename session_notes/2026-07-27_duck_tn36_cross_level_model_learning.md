# EXP-DUCK-028: tn36 Cross-Level Model Learning

## Question

Can Duck remember what controls did in an earlier level, state a goal, and use
those controls to solve a later level by planning instead of random trial and
error?

## K-12 Explanation

Imagine a small robot and a row of instruction boxes.

1. Earlier levels teach the meanings of four instruction codes: left, right,
   down, and up.
2. On a new level, first say the goal: move the editable robot onto its target.
3. Look at where the target is. If it is above and right, test up and right
   instructions before directions that move away.
4. Try complete instruction lists in a safe local copy of the game.
5. Keep a list only when the game confirms success by opening the next level.

This is planning. Blind trial and error clicks buttons without a stated goal or
a prediction. EXP-DUCK-028 records the goal first and uses level advancement as
the pass/fail test.

## Implementation

Added:

- `experiments/duck_harness_repro/tn36_cross_level_planner.py`
- `experiments/duck_harness_repro/run_exp_duck_028_model_gate.py`
- `experiments/duck_harness_repro/test_tn36_cross_level_planner.py`
- `experiments/duck_harness_repro/build_tn36_model_learning_audit.py`
- `experiments/duck_harness_repro/exp_duck_028_model_gate.json`
- `artifacts/kaggle/duck_tn36_model_learning_audit/index.html`

The reusable planner contains control facts, an explicit objective, command
ranking, candidate generation, result logging, and click encoding. It does not
contain the known six-command level-3 answer.

The local gate loads the public `tn36.py` implementation with
`arcengine==0.9.3`. The exact source SHA-256 is:

```text
ef4dde99174ca5d753809f6f193177d8e25762b5fa58c9919df8458d8b69ff23
```

## Results

Level 2:

```text
Objective: move the right robot upward onto its target
Command order: Up, Left, Right, Down
Candidates tested: 1
Discovered program: [33, 33, 33, 33]
Result: advanced to level 3
```

Level 3:

```text
Objective: move the right robot right and upward onto its target
New mechanic: walls switch after every third command
Command order: Right, Up, Left, Down
Candidates tested: 258
Discovered program: [2, 33, 2, 2, 2, 33]
Result: advanced to level 4
```

Ablation:

```text
Copied visible demonstration: [3, 3, 3, 3, 0, 0]
Result: failed to advance
```

Four focused planner tests passed. The research gate passed. No competition
submission was created.

## Interpretation

Accepted:

- Remember control meanings across levels.
- Write the objective before acting.
- Rank hypotheses by visible target direction.
- Use a simulator to test full plans.
- Treat level advancement, not pixel movement, as success.

Rejected:

- Copying the demonstration without checking its role.
- Treating any board change as puzzle progress.
- Claiming general autonomous learning from this result.

## Important Limitation

This is a source-assisted planning proof. The official local engine supplies a
correct transition model, including collision and switching-wall behavior. The
solver did not yet infer that full model from screenshots and action effects.

Therefore:

```text
Planning scaffold: proven
Cross-level memory on tn36: useful
Pixel-only learning: not proven
Cross-game scaling: not proven
Leaderboard submission: not justified
```

## Next Gate

Use a held-out game whose source is hidden from the learner.

1. Observe a small number of safe action probes.
2. Build a control-effect ledger from before/after frames.
3. State one or more objective hypotheses and predicted success conditions.
4. Learn a compact transition model from those observations.
5. Plan actions in the learned model.
6. Reject the approach if predictions repeatedly disagree with real frames, if
   the helper requires exact answer coordinates, or if it cannot add a level in
   an activated paired test.
7. Only after that isolated causal gate should we build another 25-game
   evaluation notebook.

The visual audit is:

```text
artifacts/kaggle/duck_tn36_model_learning_audit/index.html
```
