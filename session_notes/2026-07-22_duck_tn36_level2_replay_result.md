# 2026-07-22 Duck tn36 Level-2 Replay Result

## Question

Can the successful `tn36` level-2 behavior from the original July 4 Duck run be
reused after our shorter, deterministic seven-action level-1 helper?

## Evidence recovered

The original July 4 `benchmark.json` in Downloads contains the full action history
for `tn36-ef4dde99`:

- level 1 completed after 13 actions;
- level 2 completed after the next 26 actions;
- the run therefore reached level 3 after action 39;
- final `tn36` result was 2/7 levels, score `10.7143`, 45 total actions, and
  66,681 generated tokens.

This corrected EXP-DUCK-016's visual-only hypothesis. Making the two visible
matrices equal and clicking `(58,46)` was not enough to solve level 2.

## EXP-DUCK-017

The new helper:

1. uses the validated seven-action, zero-token level-1 helper;
2. checks that the initial level-2 board matches the observed `tn36` layout;
3. replays exactly actions 14-39 from the successful July 4 trace;
4. stops before the LLM can run.

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-tn36-level-2-proven-replay
```

## Live result

```text
levels completed: 2 / 7
score:            10.7143
actions:          33
actions/level:    7, 26, 0, 0, 0, 0, 0
generated tokens: 0
solver note:      tn36_level2_replay=success; helper_actions=26;
                  tn36_level1_helper=success; helper_actions=7
```

The strict validator passed.

## K-12 explanation

Imagine a player once solved two rooms while a camera recorded every button they
pressed. We already found a shorter seven-button solution for room 1. For room 2,
we replayed the old player's 26 recorded button presses. The door opened exactly
as before, without asking the AI to think or spend any tokens.

This proves the recorded sequence works. It does not yet prove that every one of
the 26 presses is necessary or that it will help hidden leaderboard games.

## Decision and next step

Promote EXP-DUCK-017 as a validated `tn36` mechanic, but do not replace the active
EXP-DUCK-009 public-score baseline yet.

Next controlled work:

1. inspect the 26 level-2 transitions and identify redundant probes;
2. test a shorter sequence in an isolated, zero-token run;
3. let unchanged Duck continue from level 3 in a targeted run;
4. run the full 25-game notebook only after the isolated evidence is stronger.
