# Duck Reki and tn36 Helper Results - 2026-07-21

## Decision summary

- Reject EXP-DUCK-011 as a scoring mechanism.
- Promote EXP-DUCK-013 into the EXP-DUCK-014 full evaluation.
- Keep EXP-DUCK-012 running as an independent Forge-style feedback test.

## EXP-DUCK-011: fallback-only Reki saliency

Kaggle kernel: `jatalepawan/arc-agi-3-duck-fallback-only-reki-saliency`

Result:

| game | levels | actions | tokens | fallback actions | effective fallback actions | fallback level progress |
|---|---:|---:|---:|---:|---:|---:|
| `tn36-ef4dde99` | 0/7 | 120 | 54,048 | 24 | 5 | 0 |
| `sc25-635fd71a` | 0/6 | 114 | 33,618 | 24 | 1 | 0 |

The fallback changed pixels six times, but none of its 48 clicks advanced a
level. Saliency is therefore insufficient: visually distinctive objects are
not necessarily the correct mechanic targets. Do not add this fallback to the
submission notebook.

## EXP-DUCK-013: signature-gated tn36 level 1

Kaggle kernel: `jatalepawan/arc-agi-3-duck-tn36-level-1-helper`

Observed action sequence:

```text
1. MOUSE(row=42, col=26)
2. MOUSE(row=42, col=36)
3. MOUSE(row=42, col=41)
4. MOUSE(row=45, col=26)
5. MOUSE(row=45, col=36)
6. MOUSE(row=45, col=41)
7. MOUSE(row=55, col=36)
```

The first six actions changed the board without completing the level. Action 7
changed the board, advanced to level 2, and produced reward `1/7`. The benchmark
recorded:

```text
levels_completed: 1/7
actions_per_level: [7, 0, 0, 0, 0, 0, 0]
generated_tokens: 0
final_score: 3.571428571428571
solver_note: tn36_level1_helper=success; helper_actions=7
```

This satisfies the exact promotion gate. Unlike the generic fallback, it is a
mechanic derived from a successful trace and protected by a board signature.

### Level-2 follow-up

The level-2 board produced by EXP-DUCK-013 is byte-identical to the level-2
board reached by EXP-DUCK-009. It contains 44 three-pixel blue toggle objects,
two separate panels, selector-like bottom icons, two clue shapes, and a submit
object. EXP-DUCK-009 clicked all 44 toggles and later tried panel-specific
patterns, selectors, resets, and repeated submit clicks without advancing.

This rejects the simple "clear every block" interpretation. Level 2 appears to
require a panel transformation or selection rule. No level-2 helper should be
added until a successful trace or a discriminating isolated experiment reveals
that rule. EXP-DUCK-014 therefore uses only the validated level-1 prefix and
returns level 2 to normal Duck reasoning.

## EXP-DUCK-012: exact-no-change batch feedback

Kaggle kernel: `jatalepawan/arc-agi-3-duck-exact-no-change-batch-feedback`

The four-game targeted run completed 2 of 28 levels with score sum `0.6022`,
1,282 actions, and 760,038 generated tokens. The live policy interrupted 55
exact-no-change batches and cancelled 180 queued actions. `g50t` and `ka59`
each completed one level; `sk48` and `dc22` completed none.

This proves that immediate feedback can invalidate a queued plan, but it is not
ready for promotion. Total spend remained high, and one interruption coincided
with a terminal transition. Keep the event instrumentation, add a terminal
guard before any retest, and do not merge this policy into the submission.

## EXP-DUCK-014 full-evaluation result

Kaggle kernel: `jatalepawan/arc-agi-3-duck-full-eval-ft09-tn36`

The candidate preserved EXP-DUCK-009's validated ft09 policies and all-game
settings. It applied the seven-action prefix only to tn36 level 1, then resumed
normal Duck reasoning on level 2.

| metric | EXP-DUCK-009 | EXP-DUCK-014 | change |
|---|---:|---:|---:|
| levels completed | 18/183 | 22/183 | +4 |
| score sum | 65.6878 | 92.7582 | +27.0704 |
| ft09 levels | 4/6 | 4/6 | 0 |
| tn36 levels | 0/7 | 1/7 | +1 |

`ft09` reproduced its exact 69-action, zero-token 4/6 result. `tn36` began
with the exact seven-action, zero-token helper; action 7 completed level 1, and
normal Duck continued on level 2 through action 64. The helper did not appear
in any non-target game. Every check in `validate_exp_duck_014.py` passed.

The all-game gate therefore passed, and the exact generated
`submission.parquet` is the leaderboard candidate. The local four-level gain
includes stochastic non-target differences, so the official public score is
still the final promotion test; it must exceed EXP-DUCK-009's `0.92`.

Submission reference `54880404` was created from kernel Version 1 and was
observed as `PENDING` on 2026-07-21. The submitted artifact SHA-256 is
`71bfd543030e339d87bd9ff744d466218398a1259650b2c255626d27049c88bb`.
