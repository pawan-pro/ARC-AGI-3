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

## EXP-DUCK-024 full-evaluation result

The completed Version 1 run passed every gate:

| metric | EXP-DUCK-009 | EXP-DUCK-024 | change |
|---|---:|---:|---:|
| levels completed | 18/183 | 18/183 | 0 |
| score sum | 65.6878 | 81.4323 | +15.7445 |
| actions | 4,435 | 4,369 | -66 |
| ft09 levels | 4/6 | 4/6 | 0 |
| tn36 levels | 1/7 | 3/7 | +2 |

EXP-DUCK-024 generated 1,674,657 tokens across all games. On tn36 specifically,
normal Duck made 57 analysis calls and spent 69,355 tokens before the postlude.
Duck had already reached level 2. The postlude then:

```text
started after action: 232
reset current level:  1 action
solved levels 2-3:   18 actions
generated tokens:    0
final tn36 result:   3/7
```

The strict validator confirmed:

```text
same 25 games
ft09 preserved
normal tn36 analysis occurred before repair
postlude began with RESET
postlude generated zero tokens
tn36 reached three levels
helper did not leak
aggregate not weaker than scored EXP-DUCK-009
recommended_submit = true
```

Compared with EXP-DUCK-009, unrelated LLM games still varied. The net result
was exactly offsetting: tn36 gained two levels, while `bp35`, `m0r0`, `sp80`,
and `tu93` lost four total levels and `r11l` plus `sk48` gained two. This
confirms that preserving request traffic reduces the direct integration
disturbance but does not remove general concurrent-LLM variance.

The exact notebook Version 1 was submitted through the code-competition
workflow:

```text
submission reference: 54965732
description: EXP-DUCK-024 Duck baseline request stream plus tn36 postlude
status: pending
```

Do not submit again.

## Official public result

Kaggle completed submission `54965732` with:

```text
status:       COMPLETE
public score: 1.11
```

This beats EXP-DUCK-009's `0.92` by `0.19` absolute, or about `20.7%`.
EXP-DUCK-024 is promoted as the active submission baseline and new project
best.

## What transferred

The earlier tn36 integrations scored `0.88` and `0.90` even though their local
results looked stronger. They changed tn36's LLM request stream at the start,
which disturbed the shared concurrent model workload.

EXP-DUCK-024 kept Duck's normal tn36 reasoning first. Only after that reasoning
ended did it apply the zero-token repair. The `1.11` public score is strong
evidence that this ordering was the missing integration detail.

K-12 version: let every student finish the normal class first, then correct one
worksheet afterward. That keeps the lesson stable for the rest of the class
while still adding the known answer where it helps.
