# 2026-07-25 Duck tu93 Route Postlude Plan

## Current baseline

EXP-DUCK-024 is the active notebook and public-score baseline:

```text
public score: 1.11
integration: normal Duck first, deterministic tn36 repair afterward
```

The improvement supports the integration pattern, not the assumption that one
game's calculator automatically solves every other game.

## Generalization rule

Each game needs its own small, verified calculator:

1. find a repeated clean board signature;
2. recover or derive a route that succeeds more than once;
3. test that route alone with zero LLM tokens;
4. attach it only after normal Duck stops;
5. require an exact game ID and board-signature match.

K-12 version: we can reuse the idea of a calculator, but each worksheet may
need different buttons. We first prove the buttons on one worksheet, then add
them to the shared calculator box.

## Why tu93 is next

Across stored Duck runs, tu93 has stable starts and repeated successful routes:

```text
level 1 board CRC32: 0xf888b0bd
level 1 route:       18 movement actions
level 2 board CRC32: 0x984223a4
level 2 route:       10 movement actions
```

The level-1 route succeeded from a clean reset in three independent stored
runs. The level-2 route also succeeded repeatedly from its clean reset board.
In EXP-DUCK-024, normal Duck used 222 actions to finish level 1 and did not
finish level 2, so a postlude has room to add one level efficiently.

## EXP-DUCK-025 gate

The isolated Kaggle notebook targets only `tu93-0768757b`. It makes no model
requests and must pass all of these checks:

```text
one target game only
two levels completed
exact 28-action route
zero analysis events
level 1 success note reports 18 actions
level 2 success note reports 10 actions
```

If this test passes, the next experiment will keep EXP-DUCK-024 unchanged
during normal play and run the tu93 route only as a postlude. A full evaluation
and official submission remain gated on preserving ft09, tn36, all 25 games,
and no helper leakage.

## EXP-DUCK-025 result

The isolated Kaggle Version 1 passed every strict gate:

```text
levels completed: 2/9
score:            6.6667
actions:          28
tokens:           0
analysis events:  0
level 1 route:    exact 18 actions
level 2 route:    exact 10 actions
```

The solver note independently confirms both successes:

```text
tu93_route=success; level=1; helper_actions=18
tu93_route=success; level=2; helper_actions=10
```

This proves the tu93 calculator itself works. It does not yet prove that a new
25-game run will beat the `1.11` public baseline, because the LLM-driven games
still vary between full runs.

## EXP-DUCK-026

The next notebook starts from the exact EXP-DUCK-024 notebook. It preserves:

```text
normal Duck on every game
the validated ft09 path
the existing post-Duck tn36 repair
the model, prompt, batching, and action budgets
```

It adds only one behavior: after normal Duck stops on tu93, reset the current
level and apply the exact-board routes until two levels are complete. The full
run remains a gate, not an automatic competition submission.

## EXP-DUCK-026 full-evaluation result

The completed 25-game run passed every structural and aggregate gate:

| metric | EXP-DUCK-024 | EXP-DUCK-026 | change |
|---|---:|---:|---:|
| levels completed | 18/183 | 21/183 | +3 |
| score sum | 81.4323 | 98.3785 | +16.9462 |
| actions | 4,369 | 5,131 | +762 |
| ft09 levels | 4/6 | 4/6 | 0 |
| tn36 levels | 3/7 | 3/7 | 0 |
| tu93 levels | 1/9 | 2/9 | +1 |

The run used 1,633,141 generated tokens. The existing tn36 postlude remained
healthy: normal Duck ran first, then the postlude used 26 actions and zero
tokens to reach level 3. No tn36 or tu93 helper note leaked to another game.

Normal Duck independently solved both tu93 levels before stopping:

```text
tu93 levels:          2/9
tu93 actions:         65
tu93 analysis events: 38
solver note:          tu93_postlude=already_complete; levels=2
```

Therefore, this full run proves that the tu93 postlude integrates safely, but
it does not measure an additional level caused by the postlude. The aggregate
gain also contains ordinary LLM-run variance: `cd82`, `ls20`, and `sp80`
improved, while `sk48` and `vc33` lost one level each.

Both validators returned:

```text
structural_pass = true
recommended_submit = true
```

The exact Version 1 notebook was submitted through Kaggle's code-competition
workflow:

```text
submission reference: 55001932
description: EXP-DUCK-026 Duck baseline plus tn36 and tu93 postludes
status: pending
```

Do not submit again. Promote EXP-DUCK-026 only if its official public score is
above the active EXP-DUCK-024 score of `1.11`.

## Official public result

Kaggle completed submission `55001932` with:

```text
status:       COMPLETE
public score: 0.86
```

This is `0.25` below EXP-DUCK-024's public score of `1.11`. EXP-DUCK-026 is
rejected, and EXP-DUCK-024 remains the active baseline.

The isolated tu93 calculator is still valid: it solved two levels in exactly
28 zero-token actions. The failed promotion is an integration-evidence issue,
not a route failure. In the full run, normal Duck reached two tu93 levels
before the postlude, so the new helper never activated. The apparently stronger
21-level local aggregate came partly from unrelated stochastic gains and did
not transfer to the hidden scoring run.

Next experiments should not be submitted merely because one stochastic full
run has a stronger aggregate. Require at least one of:

```text
the target postlude actually activates and adds a level
a paired in-kernel control isolates the helper's effect
repeated full runs show a stable aggregate advantage
```

The practical next target remains another game with a repeatable mechanic, but
its isolated helper should be integrated only after this stronger causal gate.
