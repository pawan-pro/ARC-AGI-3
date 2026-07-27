# EXP-DUCK-030: ft09 Cross-Game Objective Learning

## Goal

Test whether the model-based workflow from tu93 transfers to a different game
family without storing the winning coordinates, named color meanings, game
source, or held-out successful actions.

## Data Boundary

The learner received:

- 47 action frames from solved ft09 levels 1-3.
- The untouched initial picture of held-out level 4.
- One new board observation after each action chosen by its own policy.

The objective model did not receive:

- The 21 successful level-4 actions.
- The stored `NORMAL_CELLS` or `SPECIAL_CELLS` lists.
- Named blue, red, orange, white, or gray constants.
- The official game source.

## K-12 Explanation

This puzzle is like three small instruction cards placed over one large answer
sheet.

The learner first found:

1. Eighteen large blocks that can be changed.
2. Three smaller patterned clue blocks.
3. Three possible block states learned from earlier levels.
4. Two types of tiny marks inside each clue.

It considered both possible meanings for the tiny marks:

```text
Idea A: mark 0 means "copy the clue center"
Idea B: mark 2 means "copy the clue center"
```

Then it checked shared cells. If two clue cards cover the same answer block,
both must request the same color.

Results:

```text
Idea A: exactly 1 conflict-free target
Idea B: 0 conflict-free targets
```

Without the overlap check, the three clues leave eight possible assignments.
The shared-cell constraint reduces those eight guesses to one answer before
the first held-out click.

## Closed-Loop Control

The target was frozen before validation. The policy repeatedly:

```text
look at the current board
find the first block that differs from the target
click it once
observe the new board
repeat
```

This means the controller did not need to assume how many clicks change one
color into another. It learned from each observed effect while moving toward a
pre-declared objective.

## Result

```text
Geometry: 18 editable cells, 3 clue cells, spacing 8
Held-out actions available to objective model: 0
Policy actions: 21
Actions matching successful replay: 21/21
Final result: advanced from level 4 to level 5
Focused tests: 4/4 passed
Structural gates: 10/10 passed
Competition submission: no
```

## Interpretation

Accepted:

```text
The hypothesis-first architecture transfers to a second game family.
The objective can be inferred from pixels and cross-clue constraints.
Wrong explanations can be rejected before acting.
Online feedback can control execution without replaying a stored route.
```

Not yet proven:

```text
Prospective success on a level with no known winning replay.
Automatic selection of the correct game-specific model class.
Public-score improvement.
Robustness across all 25 games.
```

## Next Gate

Choose an unsolved level with repeated mechanics and run prospectively:

```text
pixels -> candidate objectives -> consistency score -> confidence gate
       -> closed-loop action -> predicted/observed effect check
```

Reject the helper if:

- More than one objective remains.
- No objective is internally consistent.
- An action effect contradicts the learned model.
- It consumes the action budget without level progress.

Do not pay for another full 25-game evaluation until an activated prospective
helper adds at least one level.

Visual audit:

```text
artifacts/kaggle/duck_ft09_cross_game_learning_audit/index.html
```
