# Tufa Public Audit and Seeded Pair Plan - 2026-07-22

## K-12 summary

Our Duck is using the same schoolbag as the winning public Duck: it sees the image,
gets a simplified object map, can use Python as scratch paper, writes short memory
notes, and forgets old chat turns when its notebook becomes too full.

The problem is the measuring ruler. Duck makes sampled choices, and 16 games ask the
same model for answers at the same time. Adding a helper to one game changes when the
other games ask their questions. They can then receive different random answers even
though their code did not change.

## Public-source audit

Reviewed:

- Kaggle discussion `717133`, the Milestone #1 Duck write-up.
- Public notebook `jeroencottaar/tufa-labs-duck-harness-june-30-milestone-winner`.
- Dataset `jeroencottaar/taaf-kaggle-source-share`.
- Tufa repository `Tufalabs/duck-harness` as linked by the write-up.

Our source matches the public base harness. The only source differences in the latest
candidate are our `ft09`/`tn36` helper additions and their solver integration. We are
not missing a hidden public prompt, segmentation system, Python REPL, world-model
note, multimodal frame, or context-eviction mechanism.

Important published limits and choices also match: one current frame enlarged 4x,
ASCII plus segmentation, 30-second Python calls, compact tool output, batched actions,
and oldest-turn eviction. Tufa explicitly reports high run-to-run variance and says
that stronger models and multimodality helped more reliably than specific handcrafted
tools.

## Why EXP-DUCK-014 looked better locally but scored worse

- Intended target result: `ft09` stayed at 4 levels; `tn36` stayed at 1 level but used
  fewer actions.
- All extra local levels came from unrelated games.
- Public score fell from EXP-DUCK-009 `0.92` to EXP-DUCK-014 `0.88`.
- The public setup uses temperature `0.6`, top-p `0.95`, top-k `20`, and no request
  seed. Concurrent request order therefore changes sampled answers.

Conclusion: EXP-DUCK-014 did not demonstrate a scoring gain from the tn36 helper.
It demonstrated an efficiency gain on tn36 plus unrelated sampling luck.

## EXP-DUCK-015 paired test

Run two matched eight-game notebooks:

1. **015A control:** EXP-DUCK-009 behavior with stable per-game request seeds.
2. **015B candidate:** identical seeds and games, plus the tn36 level-1 helper.

Each request seed is derived from `game_id + request_index + experiment salt`, so one
game's extra or missing LLM calls cannot shift another game's random sequence.

Promotion gate:

- Every non-tn36 action/token trajectory must match between the pair.
- tn36 must preserve or improve level progress and use fewer resources.
- No leaderboard submission follows from efficiency alone; a scoring helper must add
  a level under the paired test before a new full evaluation is justified.

Both Version 1 kernels were launched on 2026-07-22 and entered `RUNNING` state:

- `jatalepawan/arc-agi-3-duck-seeded-pair-control`
- `jatalepawan/arc-agi-3-duck-seeded-pair-tn36`

Expected monitoring cadence: roughly every three hours, matching the historical Duck
runtime instead of repeatedly polling.

## EXP-DUCK-015 result

Both kernels completed successfully in about 2 hours 12 minutes. Kaggle's downloaded
package omitted `benchmark.json`, but it included complete per-game event streams;
the final Kaggle logs also printed the complete benchmark summaries.

| Metric | 015A control | 015B tn36 candidate |
|---|---:|---:|
| Levels across eight games | 9 | 11 |
| Mean score | 6.71 | 7.15 |
| Actions | 2,501 | 3,061 |
| Generated tokens | 1,134,698 | 1,148,936 |
| tn36 levels | 0 | 1 |
| tn36 actions | 428 | 263 |
| tn36 tokens | 171,229 | 146,565 |

The tn36 helper worked as designed: it added level 1 and reduced tn36 resource use.
The isolation gate nevertheless failed. Every one of the six LLM-driven non-target
games eventually followed a different action path, and four already differed on the
first action. Only ft09 matched exactly because its 69 actions are deterministic.

This shows that request seeds alone do not make separate concurrent vLLM GPU runs
reproducible. Batch scheduling and GPU/model execution still change sampled outputs.
Therefore the aggregate `9 -> 11` level result cannot be attributed solely to tn36.
No competition submission was made, and EXP-DUCK-009 remains the active `0.92`
baseline.

Next measurement design: run control and candidate sequentially inside the same
kernel with concurrency 1, preferably in both A/B and B/A order over several seeds.
That separates the helper effect from cross-run batching variance. Do not spend a
full submission until the target improvement survives that gate.

## What the public winner suggests next

After the paired ruler is validated, the strongest general research directions are:

- compact older observations into curated memory instead of merely deleting them;
- turn segmentation into shorter abstract object/relationship descriptions;
- evaluate promising changes over repeated matched seeds;
- prefer generic perception and memory improvements over game-specific prompt hints.
