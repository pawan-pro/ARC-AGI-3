# 2026-07-24 Duck tn36 Postlude Integration

## Why EXP-DUCK-023 scored 0.90

EXP-DUCK-023 improved tn36 locally, but its early deterministic helper removed
tn36 model requests from the shared 28-game vLLM batch. That changed the timing
and stochastic trajectories of unrelated games.

Compared with the scored EXP-DUCK-009 run, the non-target games had both gains
and losses:

```text
gains:  r11l +1, dc22 +1, cd82 +1, ls20 +1
losses: tu93 -2, m0r0 -1, re86 -1, sp80 -1
net non-target change: -1 level
```

The deterministic tn36 path is valid. Its integration changed the shared model
workload too early.

## Parquet constraint

The generated `submission.parquet` is a one-row placeholder. Kaggle reruns the
notebook on hidden games and scores that interactive execution. We therefore
cannot splice the strong tn36 row into the 0.92 submission offline.

## EXP-DUCK-024 controlled change

The new notebook keeps normal Duck behavior first, including all ordinary tn36
model calls. When Duck's tn36 analysis loop ends, but before `finish_game()`,
the postlude:

1. records Duck's action and token totals;
2. resets only the current tn36 level to a clean board;
3. applies the signature-gated level 1, 2, and 3 programs as needed;
4. records postlude actions and verifies that postlude token use is zero.

The repair is not called inside the normal reasoning loop. It therefore does
not remove tn36 requests from the concurrent vLLM batch.

## K-12 explanation

The previous notebook gave one student the answer before the class started.
That changed the order in which the teacher helped all the other students.

This notebook lets the whole class follow the original lesson first. After the
lesson ends, it quietly corrects only tn36's worksheet. The correction uses
fixed clicks and does not ask the LLM teacher another question.

## Gate

Kernel Version 1:

```text
jatalepawan/arc-agi-3-duck-full-eval-tn36-postlude
```

Expected runtime is about 2-3 hours. Do not create a competition submission
unless all of these pass:

```text
25 games exactly once
ft09 >= 4/6
tn36 >= 3/7
normal tn36 analysis observed before the postlude
postlude generated tokens = 0
no helper notes on non-tn36 games
aggregate levels and score >= scored EXP-DUCK-009 artifact
```

EXP-DUCK-009 remains the active public baseline at `0.92`.
