# 2026-07-23 Duck tn36 Level-3 True-Name Program

## What EXP-DUCK-019 showed

The corrected continuation run solved tn36 levels 1-2 with the validated
16-action deterministic prefix, then gave unchanged Duck 104 actions on level
3.

```text
levels:            2 / 7
actions:           120 total
actions per level: 7, 9, 104, 0, 0, 0, 0
generated tokens:  102,899
```

Duck noticed several real visual features, but it mixed together the command
editor, program selector, and target geometry. It sent large speculative click
batches, reached `GAME_OVER`, reset, and never advanced level 3.

This is evidence against simply adding more thinking time. The limiting factor
was the world model: the solver did not understand what the controls meant.

## EXP-DUCK-021 result

The copied demonstration hypothesis failed cleanly:

```text
levels:            2 / 7
actions:           25 total
actions per level: 7, 9, 9, 0, 0, 0, 0
generated tokens:  0
level-3 result:    no progress
```

The selected left-side program is a demonstration, not an answer to copy.
The right-side robot has a different starting point and must reach its own
target.

## Exact switching-wall route

The local official engine exposes the right-side start and goal:

```text
start: (37, 20)
goal:  (53, 12)
```

A direct route fails because a wall blocks the robot. Some walls change
visibility after every third command. Exhaustive search over the legal
six-command programs found:

```text
[2, 33, 2, 2, 2, 33]
right, up, right, right, right, up
```

The official local engine reaches the target with this program.

## K-12 explanation

The robot is walking through a hallway with doors that switch after its third
step. Walking all the way right first does not work because a door is closed.
The working dance is:

```text
right, up, right, right, right, up
```

The important discovery is not just the destination. The order of the steps
changes the hallway.

## EXP-DUCK-022 gate

The targeted Kaggle notebook must reproduce the local engine:

```text
levels completed:  at least 3
total actions:     exactly 25
generated tokens:  exactly 0
level-3 note:      tn36_level3_program=success
```

Only after this isolated gate passes should the helper enter a full 25-game
evaluation. EXP-DUCK-009, public score `0.92`, remains the active submission
baseline until a new full evaluation also passes the leaderboard gate.

## EXP-DUCK-022 result

Kaggle reproduced the local engine exactly:

```text
levels:            3 / 7
score:             21.4286
actions:           25 total
actions per level: 7, 9, 9, 0, 0, 0, 0
generated tokens:  0
validator:         PASS
```

The deterministic path is now validated through level 3. Compared with
EXP-DUCK-019, it replaces 104 unsuccessful level-3 actions and 102,899 total
tokens with nine successful level-3 clicks and no tokens.

## Full-evaluation plan

EXP-DUCK-023 runs all 25 games with:

- the validated EXP-DUCK-009 ft09 path unchanged;
- tn36 levels 1-3 solved in 25 deterministic actions;
- unchanged Duck resuming on tn36 level 4;
- no helper behavior on the other 23 games.

The competition submission gate requires structural validation plus aggregate
score and level totals that are not weaker than EXP-DUCK-009. A local pass is
necessary but not enough: EXP-DUCK-009 at public score `0.92` remains active
until an official leaderboard score improves it.

## EXP-DUCK-023 full-evaluation result

The all-game evaluation passed every prepared gate:

| metric | stored EXP-DUCK-009 benchmark | EXP-DUCK-023 | change |
|---|---:|---:|---:|
| levels completed | 14/183 | 19/183 | +5 |
| score sum | 21.2453 | 88.3263 | +67.0810 |
| ft09 levels | 4/6 | 4/6 | 0 |
| tn36 levels | 0/7 | 3/7 | +3 |

Additional totals:

```text
actions: 5,427
tokens:  1,602,534
```

Structural validation confirmed:

- all 25 expected games ran;
- ft09 reproduced its 69-action, zero-token 4/6 path;
- tn36 actions 7, 16, and 25 completed levels 1, 2, and 3;
- the first 25 tn36 actions generated zero tokens;
- normal Duck continued on tn36 level 4;
- none of the tn36 helper notes appeared on another game.

The exact kernel Version 1 artifact was submitted through Kaggle's
code-competition workflow:

```text
submission reference: 54930218
description: EXP-DUCK-023 full eval ft09 plus tn36 level 3 wall route
status: pending
```

Kaggle completed submission `54930218` with public score `0.90`. This is `0.02`
below EXP-DUCK-009's `0.92`, so EXP-DUCK-023 is rejected as the active
leaderboard baseline.

## K-12 interpretation

We definitely taught the robot how to solve the first three tn36 rooms. But the
other games still use an unpredictable LLM, so this particular full run was a
slightly weaker lottery ticket overall. The new tn36 skill is worth keeping;
the complete notebook result is not.

The next integration should control or average the non-target LLM randomness
before paying for another official submission. EXP-DUCK-009 remains the active
baseline at `0.92`.
