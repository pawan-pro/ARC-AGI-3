# ft09 Level-4 Overlap-Consistent Test Result

Date: 2026-07-17

Experiment: `EXP-DUCK-008`

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-ft09-level4-overlap
```

Artifacts:

```text
artifacts/kaggle/duck_ft09_level4_overlap/latest/
```

## Result

The overlap-consistent target solved ft09 level 4.

```text
game: ft09-0d8bbf25
levels: 4 / 6
actions_per_level: [9, 7, 32, 21, 0, 0]
total actions: 69
generated tokens: 0
final benchmark score: 45.713355654761905
```

Solver note:

```text
ft09_overlap_target=RORbRRRRRORRbRROOO;
planned=21;
executed=21;
solved=True;
stop=level_completed;
ft09_prefix_replay_actions=48;
reached_level=4;
target_level=4
```

## Independent Validation

The downloaded event stream confirms:

```text
level 4 started after action 48
actions 49-69 exactly matched the 21-click derived sequence
action 69 advanced the game to level 5
level_completed: true
game_over: false
all 69 actions generated zero model tokens
```

The result is not inferred from the solver note alone. The benchmark, action
history, and event transition all agree.

## Comparison

| Experiment | Levels | Level-4 actions | Tokens | Outcome |
|---|---:|---:|---:|---|
| EXP-DUCK-005 isolated candidate set | 3/6 | 72 | 0 | Did not solve |
| EXP-DUCK-006 exhaustive candidates | 3/6 | 142 | 126,904 | Candidate 5 caused game over |
| EXP-DUCK-008 overlap-consistent target | 4/6 | 21 | 0 | Solved level 4 |

## K-12 Explanation

We treated the three clue cards like overlapping transparencies. Only red made
every shared square agree. We colored the board using that one consistent
answer, and the door to room 5 opened after exactly 21 clicks.

This confirms the important idea: when clues overlap, first solve their shared
constraints. Do not make the clues vote by majority or try random color rules.

## Decision

`EXP-DUCK-008` is positive and the targeted evaluation gate is passed.

The next controlled experiment is `EXP-DUCK-009`: integrate the confirmed ft09
prefix plus overlap helper into the full Duck evaluation notebook, preserve all
other baseline behavior, run all games once, and compare against the 0.84
public baseline.

This is still a game-specific proof. For top-10 work, the follow-up engineering
goal is to generalize overlap-consistency detection so the solver can recognize
the same mechanic without hardcoded coordinates or a hardcoded target string.
