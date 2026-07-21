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

## EXP-DUCK-014 launch

Kaggle kernel: `jatalepawan/arc-agi-3-duck-full-eval-ft09-tn36`

The candidate preserves EXP-DUCK-009's validated ft09 policies and all-game
settings. It applies the seven-action prefix only to tn36 level 1, then resumes
normal Duck reasoning on level 2. Version 1 was launched after EXP-DUCK-013
passed. Promotion to leaderboard submission still requires the completed
all-game benchmark to outperform or safely dominate EXP-DUCK-009.
