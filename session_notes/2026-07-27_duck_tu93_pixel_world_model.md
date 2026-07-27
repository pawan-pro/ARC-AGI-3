# EXP-DUCK-029: tu93 Pixel-Derived World Model

## Goal

Close the main limitation of EXP-DUCK-028: plan a held-out level without giving
the learner the official game source or a transition simulator.

## Data Boundary

The learner received:

- 28 recorded action frames covering successful tu93 levels 1 and 2.
- The last level-2 frame, which is the initial picture of held-out level 3.

The learner did not receive:

- `tu93.py`.
- Any level-3 action.
- The stored level-3 route.
- The level-3 outcome until after its plan was complete.

## K-12 Explanation

The system watched the player move in two earlier mazes and learned:

1. Which colored piece was moving.
2. Which button meant Up, Down, Left, and Right.
3. That movement happens in six-pixel steps.
4. That all red switches must be collected before reaching the green target.
5. That the small purple mark inside a red switch points to a neighboring cell
   that remains dangerous until the switch is collected.

It then turned the level-3 picture into a map. Each possible situation was:

```text
where the blue piece is + which red switches remain
```

Breadth-first search tested those situations on the learned map, not in the
official engine.

## Learned Model

```text
Blue / color 9: moving agent
Green / color 14: target
Red / color 8: collectible switch
Purple / color 15: lock direction marker
Black / color 5: background
White / color 0: ordinary node
Grid step: 6 pixels
```

Controls:

```text
UP    = (-6,  0)
DOWN  = ( 6,  0)
LEFT  = ( 0, -6)
RIGHT = ( 0,  6)
```

Held-out level 3:

```text
Agent: (43, 43)
Target: (43, 25)
Red switches: (25,25), (25,31), (37,13)
Graph nodes: 23
Abstract states explored: 50
```

## Generated Plan

```text
UP, UP, RIGHT, UP, LEFT, LEFT, UP, LEFT, LEFT,
DOWN, RIGHT, DOWN, LEFT, LEFT, LEFT, DOWN, RIGHT, DOWN, RIGHT
```

The generated 19 actions exactly match the already successful live Kaggle
level-3 replay. The learner saw zero level-3 actions before producing the plan.

## Falsification

A simpler model ignored the purple lock markers. It found a shorter 15-action
route, but entered a still-locked cell at step 4 and produced GAME_OVER in a
black-box check.

This failure is preserved as evidence:

```text
Visible corridor alone is not enough.
Switch dependency model is necessary.
```

## Gates

Passed:

- Source hidden from learner.
- Zero held-out actions available during planning.
- Four controls learned.
- Visual roles learned.
- Three lock dependencies parsed.
- Held-out plan found.
- Generated plan exactly matches successful replay.
- Replay advances the level.
- Naive model rejected.
- Four focused code tests passed.

No competition submission or full notebook evaluation was created.

## Interpretation

Accepted:

```text
Pixel-only transfer across levels of the same game
Learned controls and visual object roles
Explicit hidden-state model
Planning over position and remaining objectives
Prediction failure as a rejection signal
```

Not yet proven:

```text
Transfer to a different game family
Role learning without earlier solved levels
Robustness to changed colors or sprite sizes
Public-score improvement
```

## Next Gate

Choose a second game with:

- At least one solved training level and one unsolved later level.
- Repeated visual mechanics.
- A small, auditable action space.
- No source access for the learner.

Run the same pipeline:

```text
frames -> controls -> roles -> dependencies -> world model -> plan -> prediction audit
```

Reject if controls are inconsistent, role confidence is low, predicted effects
do not match observed frames, or the helper cannot add a level in an activated
test. A new 25-game evaluation is justified only after that cross-game gate.

Visual audit:

```text
artifacts/kaggle/duck_tu93_pixel_learning_audit/index.html
```
