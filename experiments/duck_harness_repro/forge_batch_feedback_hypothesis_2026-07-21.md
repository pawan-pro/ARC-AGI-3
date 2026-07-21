# Forge Notebook Analysis and EXP-DUCK-012 Hypothesis

Date: 2026-07-21

## What the Scored Forge Profile Actually Used

The linked 0.86 Forge notebook used one action candidate, four context frames, a maximum four-action plan, and reflection every ten transitions. Its scored profile disabled the candidate arbiter, confidence prompt, frame descriptor, and multiple-candidate generation.

The useful transferable behavior is plan invalidation: after observing an exact no-change or a recently repeated state, Forge clears the remaining queued plan and asks the model to reason again.

## Duck Translation

Duck executes short action batches inside one tool call. EXP-DUCK-012 does not reject any chosen action. It stops only the unexecuted remainder of a batch when the just-executed action leaves the board exactly unchanged.

Repeated-state interruption is excluded because replay found a non-ft09 batch where later progress followed the repeated state.

## Offline Replay

| Stored run | ft09 exempt | No-change triggered batches | Trailing actions | Later progress behind trigger |
|---|---:|---:|---:|---:|
| Duck baseline | Yes | 51 | 182 | 0 |
| EXP-DUCK-009 | Yes | 62 | 231 | 0 |

Without the exemption, `ft09` has one unsafe trigger hiding 47 actions and later level progress. The deterministic ft09 path must therefore remain exempt.

Highest-signal EXP-DUCK-009 games:

```text
sk48: 68 trailing actions
g50t: 59 trailing actions
ka59: 31 trailing actions
dc22: 24 trailing actions
```

## K-12 Explanation

Suppose Duck writes: "press A, then B, then C." If A does absolutely nothing, EXP-DUCK-012 pauses before B and C and lets Duck look again. It does not ban A, and it does not claim the whole idea is wrong. It simply avoids finishing an old plan after the first step supplied contrary evidence.

## Gate

Run the four named games after EXP-DUCK-011 releases the Kaggle GPU slot. Promote only if known progress is preserved and the shorter batches lead to better progress or clearly better traces.
