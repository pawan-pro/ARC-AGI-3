# EXP-DUCK-034: Bounded Mechanics Reasoning Loop

## Purpose

Turn the project workflow into an in-harness controller:

```text
observe -> represent -> hypothesize -> probe -> predict -> verify -> remember
```

The first prospective target remains ft09 level 5. This package does not claim
that level 5 is solved and does not claim autonomous cross-game discovery.

## Implemented

`bounded_reasoning_loop.py` provides:

1. A compact board observation with palette counts and small connected regions.
2. A versioned, machine-readable action-effect memory.
3. Exact-board rule retrieval for unvalidated mechanics.
4. Anchor-signature retrieval for later levels, but only after a rule has
   earned `validated_bidirectional` status.
5. A small hypothesis set: one-way set effects versus reversible binary XOR.
6. Deterministic Gray-code probe generation under a hard action budget.
7. Complete-board prediction checks after every non-terminal action.
8. Immediate stop on prediction mismatch, level gain, game over, run
   completion, changed pre-action state, or exhausted budget.
9. A JSON evidence trace containing candidates, hypotheses, predictions,
   mismatches, action count, and stop reason.
10. A second machine-readable memory snapshot with per-rule forward/reverse
    pixel coverage and successful-probe counts.

The rule-memory generator converts only validated EXP-DUCK-033 evidence. Each
ft09 rule remains `observed_forward_only`, has one observation, and applies only
to the exact untouched level-5 board. A later-level transfer match is therefore
not yet allowed.

Runtime evidence may mark a rule `validated_bidirectional_current_board`, but
that still retains `exact_board` scope. Expanding it to anchor-based later-level
retrieval requires an explicit reviewed promotion call; the notebook does not
promote rules automatically.

## Runtime LLM Boundary

No runtime LLM is integrated in this first version. Candidate controls come
from deterministic region observation plus the three previously validated
EXP-DUCK-033 rules. The controller proposes two deterministic causal models and
prospectively selects the reversible-XOR model for the recorded Gray-code gate.

An LLM may later propose regions or hypotheses, but it must not execute an
action directly. Every proposal must still pass the deterministic applicability
check, action budget, predicted-versus-observed check, and stop rules.

## Immediate Prospective Gate

The unlaunched private notebook is:

```text
arc3_20260730_duck_ft09_bounded_gray_reasoner.ipynb
```

It preserves:

- the validated 69-action ft09 levels 1-4 prefix;
- all EXP-DUCK-033 evidence;
- the dual Kaggle competition-mount resolver;
- the exact seven-action Gray-code order.

It disables the old one-click diagnostic helper and runs at most:

```text
top, middle, top, bottom-right, top, middle, top
```

The first click rechecks a known forward effect. The second click is the first
strong test separating one-way set behavior from reversible XOR because the top
and middle masks overlap. Any full-board mismatch rejects the selected model
and prevents the next click.

## Promotion Rule

Do not promote a rule to later-level retrieval unless:

1. both forward and reverse effects are observed without mismatch;
2. the same local anchor signature identifies exactly one control;
3. the causal mask remains stable;
4. the run does not game over;
5. the evidence trace is complete.

Do not build a full evaluation or competition submission unless the prospective
gate adds a level. A seven-state traversal with no level gain is useful causal
evidence, not a scoring improvement.

## Deferred

- LLM-generated candidate regions or causal programs.
- Automatic invention of new model classes.
- Cross-game retrieval of ft09 rules.
- Automatic promotion from one experiment to a trusted memory rule.
- Full evaluation and competition submission.

These remain deferred because the present evidence supports only three
forward-only regional effects on one exact board.

## Live Private Result

Kaggle private Version 1 completed. No competition submission was made.

```text
levels: 4/6
actions per level: [9, 7, 32, 21, 2, 0]
tokens: 0
planned helper actions: 7
executed helper actions: 2
stop: prediction_mismatch
game over: false
level gain: false
```

Action 1, `top`, reproduced the known EXP-DUCK-033 effect exactly across the
complete 64x64 board.

Action 2, `middle`, confirmed the regional XOR behavior, including reversing
the 36-pixel overlap with `top`. The selected XOR prediction differed from the
observed board at exactly one additional pixel:

```text
(row=63, col=63): expected 12, observed 11
```

The one-way set hypothesis was independently rejected with 37 mismatches. The
strict full-board guard correctly stopped before action 3.

The bottom row is otherwise color 12, so the isolated corner change may be a
combination-dependent feedback indicator. That interpretation is not yet
validated. It is not safe to classify the pixel as ignorable UI noise.

The updated memory retained every rule as `observed_forward_only` with
`exact_board` scope. No automatic promotion occurred.

## Next Safe Gate

Repeat only `top -> middle` from a clean level-5 start and stop after the second
action. Require:

1. exact reproduction of both regional XOR masks;
2. exact reproduction of `(63,63): 12 -> 11`;
3. no other changed pixel;
4. no game over or unexpected level transition.

Only after that replication should a separate reverse-order arm test
`middle -> top`. Do not resume the remaining Gray-code traversal yet.
