# Qwen runs side by side

## Executive Summary

The corrected run finished cleanly and was submitted, but performed worse offline: **5.88 versus 7.29**, a 19.3% decline. It completed 32 rather than 37 levels while taking 3,731 rather than 3,179 actions. No new official submission is recommended until the existing submission finishes scoring.

## What is comparable

Both snapshots cover the same 25 public games. Score is the unweighted mean of final game scores; levels and actions are totals across games. These are offline results, not public leaderboard scores. The corrected notebook changes shutdown handling and cell order; it is not an intentional gameplay ablation.

| Measure | Original run | Corrected run |
|---|---:|---:|
| Offline mean | 7.2913 | 5.8809 |
| Levels completed | 37 | 32 |
| Actions | 3,179 | 3,731 |
| Shutdown check | Failed | Passed |
| Official submission | Not submitted | Submitted; last checked pending |

## Regressions and gains are mixed

Twelve games regressed, eight improved, and five were unchanged in score. The two biggest losses, ft09 and re86, contributed about -1.26 points to the mean, against a net decline of -1.41. Gains elsewhere offset additional losses. This pattern motivates trajectory inspection, not a claim that shutdown changes caused poorer decisions.

| Game | Original score | Corrected score | Original levels | Corrected levels | Original actions | Corrected actions |
|---|---:|---:|---:|---:|---:|---:|
| ft09 | 36.08 | 18.39 | 4 | 3 | 129 | 136 |
| re86 | 27.78 | 13.84 | 4 | 3 | 340 | 196 |
| ka59 | 21.27 | 10.71 | 3 | 2 | 159 | 235 |
| lp85 | 12.92 | 2.78 | 3 | 1 | 98 | 101 |
| tu93 | 11.45 | 3.78 | 3 | 2 | 84 | 63 |
| s5i5 | 8.33 | 1.78 | 2 | 1 | 95 | 178 |
| g50t | 3.57 | 0.00 | 1 | 0 | 64 | 61 |
| ls20 | 3.57 | 0.00 | 1 | 0 | 200 | 69 |
| su15 | 4.81 | 1.37 | 2 | 1 | 83 | 261 |
| wa30 | 2.22 | 0.00 | 1 | 0 | 186 | 315 |
| cd82 | 5.88 | 4.68 | 2 | 2 | 109 | 147 |
| sp80 | 0.67 | 0.00 | 1 | 0 | 207 | 396 |
| r11l | 4.76 | 4.76 | 1 | 1 | 37 | 37 |
| m0r0 | 0.00 | 0.00 | 0 | 0 | 70 | 74 |
| sk48 | 0.00 | 0.00 | 0 | 0 | 76 | 89 |
| sb26 | 2.78 | 2.78 | 1 | 1 | 148 | 177 |
| tr87 | 0.00 | 0.00 | 0 | 0 | 70 | 25 |
| ar25 | 7.96 | 8.33 | 2 | 2 | 115 | 229 |
| lf52 | 0.64 | 1.82 | 1 | 1 | 75 | 83 |
| bp35 | 0.00 | 1.70 | 0 | 1 | 16 | 63 |
| vc33 | 18.92 | 21.43 | 3 | 3 | 87 | 96 |
| dc22 | 4.76 | 13.90 | 1 | 2 | 92 | 187 |
| cn04 | 3.91 | 13.22 | 1 | 2 | 38 | 79 |
| tn36 | 0.00 | 10.71 | 0 | 2 | 416 | 128 |
| sc25 | 0.00 | 11.03 | 0 | 2 | 185 | 306 |

## Recommended next steps

1. Await the already-submitted corrected run's official score; do not submit a duplicate.
2. Compare ft09 and re86 replays to identify the first materially different choices.
3. Run an unchanged private repeat after access approval to estimate stability. It has not been launched.
4. Only then test speculative decoding, memory settings, and compatible quantization variants separately.

## Questions and limitations

Did early exploratory choices, scheduling, or response variation alter progress? Two observations cannot establish a variance distribution or causal attribution. More actions did not imply more completed levels. Token counts are not compared because instrumentation differs. The corrected ft09 and re86 replay download subsequently succeeded. The trajectory findings below compare those saved event files; this is not an interactive synchronized replay player.

## The runs diverge immediately, but early speed does not predict final success

Both games start from identical recorded boards, yet their first actions differ. In ft09 the original first clicks row 4, column 6; the corrected run clicks row 38, column 38. In re86 the original starts LEFT, the corrected run UP.

For ft09, the original completes its first three levels at cumulative actions 28, 40 and 101; the corrected run does so at 4, 11 and 73. Despite faster early progress, the corrected run stops after three completed levels, whereas the original completes a fourth at action 129. For re86, the first level finishes at 23 versus 21 actions, but the third finishes at 107 versus 167: the later corrected trajectory is less action-efficient.

These observations rule out identical action sequences and a simple uniform slowdown explanation. They do not identify sampling seeds or prove a model-quality change. Next inspect the fourth-level choices in ft09 and the second-level search in re86. Logged board-change flags are not used as causal evidence because instrumentation comparability is unverified.

## Source and delivery status

Sources: EXP-DUCK-039 output_v1/benchmark.json and output_v3/benchmark.json; ft09 and re86 event JSONL files in both artifacts folders. Offline arithmetic was checked against all 25 games. No seed or timing attribution is established. This Markdown is the supporting comparison note; portable HTML rendering is incomplete because the report packager requires a native chart block. No official submission or private repeat was created as part of this comparison.

