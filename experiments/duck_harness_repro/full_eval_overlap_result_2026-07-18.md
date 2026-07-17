# EXP-DUCK-009 Full Evaluation Result

Analysis date: 2026-07-18

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-full-eval-ft09-overlap
```

## Decision

The full-evaluation gate passed. Keep the deterministic `ft09` overlap helper
in the next submission candidate.

The helper reproduced the isolated EXP-DUCK-008 result exactly while the other
24 games continued through the original LLM solver path. No leaderboard
submission was made, so `2.63` is the complete evaluation mean, not a newly
observed public leaderboard score.

## Verified Results

| Metric | Stored baseline | EXP-DUCK-009 | Change |
|---|---:|---:|---:|
| Games | 25 | 25 | 0 |
| Levels completed | 14 / 183 | 18 / 183 | +4 |
| Score sum | 21.2453 | 65.6878 | +44.4425 |
| Mean score | 0.8498 | 2.6275 | +1.7777 |
| Actions | 3,535 | 4,435 | +900 |
| Tokens | 1,713,136 | 1,619,696 | -93,440 |
| Runtime | 2h 12m 34s | 2h 12m 35s | effectively unchanged |

The comparison baseline is
`artifacts/kaggle/duck_public_repro_terminal_run/latest/benchmark.json`.

## ft09 Controlled Check

`ft09-0d8bbf25` matched the isolated overlap run exactly:

```text
levels:             4 / 6
score:              45.713355654761905
actions_per_level:  [9, 7, 32, 21, 0, 0]
total actions:      69
model tokens:       0
target:             RORbRRRRRORRbRROOO
```

Compared with the stored baseline, `ft09` moved from 2/6 to 4/6, used 13 fewer
actions, and removed 70,043 model tokens. This is the causal result of the
controlled code change.

## Non-ft09 Check

The other 24 games used the baseline model, prompt, limits, concurrency, and
one-pass configuration. Their total levels changed from 12 to 14:

```text
m0r0: 0 -> 1
re86: 0 -> 1
tn36: 0 -> 1
r11l: 1 -> 0
```

These mixed changes are normal one-run LLM variance. They do not show that the
ft09 helper improved or harmed other games. In particular, the `r11l` loss is
not evidence of a regression because the ft09-only branch cannot alter its
solver logic.

## Evidence Quality

Assessment: **Ready to share with one caveat.**

The downloaded `benchmark.json` contains all 25 game runs. Its levels, scores,
and actions match the Kaggle execution log, and its `ft09` record matches the
isolated EXP-DUCK-008 benchmark exactly. The run lasted 2h 12m 35s and completed
normally.

Token totals in the table use the runner's reproducible solver-note convention
for both benchmark files. Kaggle's run-level diagnostic used a different token
aggregation and reported 1,584,186 for EXP-DUCK-009, so token comparisons with
older tracker prose should not mix the two definitions.

The caveat is that this was a single stochastic pass. The deterministic ft09
effect is verified, but non-ft09 differences should not be promoted as solver
improvements without repeated controlled runs.

## Next Step

Build the next submission candidate with the confirmed ft09 helper unchanged.
Then either submit it to obtain the actual public score or first add another
deterministic mechanic helper supported by replay evidence. Do not tune the
global prompt from this one-run comparison.
