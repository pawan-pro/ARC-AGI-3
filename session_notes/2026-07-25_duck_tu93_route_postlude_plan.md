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
