# EXP-DUCK-038: Public AGI_9 Reproduction

## Decision

Use the Apache-2.0 Kaggle notebook `[LB 1.17] ARC-AGI-3 Qwen3.6 Duck | Full Code`
as the exact offline-reproduction starting point. It is the runnable predecessor of the
current `ARC3 Qwen3.6 Duck LB117 Safety V1`, which Kaggle showed at public score `1.33`
on 2026-09-03. The two notebooks contain the same AGI_8/AGI_9 solver changes; the newer
notebook mainly skips model setup and public-game evaluation during an ordinary save so
it can register a code-submission artifact in about 14 seconds.

The selected 1.17 notebook retains the full public/offline run path, so a private Kaggle
run can test the public 25 games without making a competition submission.

## Immutable upstream evidence

- Kaggle notebook: `yw8837/lb-1-17-arc-agi-3-qwen3-6-duck-full-code`
- Kaggle notebook numeric id: `128806172`
- Public notebook status observed 2026-09-03: `COMPLETE`
- Notebook SHA-256: `015443fd998f5bac097211fcd8372a30c1ae3abdc4883b11be3535301a42d870`
- Notebook license shown by Kaggle: Apache-2.0
- Source bundle: `jeroencottaar/taaf-kaggle-source`, Kaggle dataset id `10571350`
- Source bundle license shown by Kaggle: MIT
- Source bundle recorded state: ARC3-Inference `e442e01` dirty,
  tufa-arc-agi-framework `030ac6f` dirty, re-arc-3 `0056955095` pinned
- Downloaded source-bundle tree digest (sorted per-file SHA-256 list):
  `715faba23ea0b928aafc92af886ad9ff520df11b5a17b035bed81e4dc7e7ac45`
- Runtime wheelhouse: `driessmit1/arc3-vllm-h100-wheelhouse-v3`, dataset id `10283361`
- Model snapshot: `driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot`, dataset id `10453841`
- Kaggle labels the wheelhouse and model datasets as license `other`; their downstream
  license chain therefore remains unresolved and must be checked before redistribution.
- Model served as `vrfai/Qwen3.6-27B-FP8`; vLLM setup pins `vllm==0.19.0`,
  `torch==2.10.0`, and `flashinfer==0.6.6` through the attached wheelhouse.
- Kaggle container digest from upstream metadata:
  `gcr.io/kaggle-private-byod/python@sha256:57e612b484cf3df5026ee4dcc3cb176974b22b2bc0937fb1e16132a8be4cb13c`

The Kaggle metadata names datasets by mutable slug rather than immutable dataset version.
The hashes and copied metadata here record what was inspected, but a future rerun can still
drift if an owner updates an attached dataset.

## Candidate mechanism

The model and sampling configuration are still the stock Qwen3.6-27B-FP8 Duck stack:
temperature `0.6`, top-p `0.95`, top-k `20`, thinking enabled, current-grid multimodal
context, concurrency `28`, and per-game runtime `7920` seconds.

The notebook adds only two generic runtime changes:

1. AGI_8 stops a repeated `UP`, `DOWN`, `LEFT`, or `RIGHT` inside a single requested batch
   when the preceding identical direction caused no visible board change. It returns control
   to the model for a new observation.
2. AGI_9 increases the local analyzer yield interval from 60 to 90 seconds, allowing an
   inspection-heavy turn one more model/tool cycle before the solver resumes scheduling.

## Comparison with EXP-DUCK-024 (public 1.11)

| Dimension | EXP-DUCK-024 | Public AGI_9 candidate |
|---|---|---|
| Model | Qwen3.6-27B-FP8 | Same model snapshot slug |
| Base source | `taaf-kaggle-source-share` (`aa69123`) | `taaf-kaggle-source` (`e442e01`) |
| Main gain mechanism | Exact ft09 replay plus signature-gated tn36 postlude | Game-agnostic repeated-no-effect batch guard |
| Scheduling | Stock 60-second analyzer yield | 90-second analyzer yield |
| Game-specific code | Yes (`ft09`, `tn36`) | None in notebook patch |
| Public score | 1.11 | 1.17 in selected notebook; same patch later shown at 1.33 |

This is not a clean one-variable comparison. Besides the two notebook patches, the attached
source bundle differs materially from the `-share` bundle used by EXP-DUCK-024 (runtime-state
caching, history eviction controls, transcript handling, and provider plumbing). A reproduced
score therefore tests the whole public artifact, not AGI_8 or AGI_9 causally.

## Other candidates rejected as the first reproduction

- `iamjasonfeng/sandwich` is genuine code, not only a score wrapper: it adds six sequential
  advisory proposals and an Explore-to-Stable RPS mode. Its own note says the 1.22 result has
  too few runs and may suffer from overthinking/timeouts. This is a larger, costlier first step.
- `saurabhkumar234/tough-guard-v2` mainly adds Blackwell/CUDA and FlashInfer fallback handling,
  uses an additional 7B model input, took about 8h50m for its successful scored version, and
  its current Kaggle status was `ERROR` on 2026-09-03.
- `obirdy/arc3-duck-verified-world-model-gpu-v1` is a small prompt-guidance modification with
  public score 1.10, below EXP-DUCK-024.
- `iamjasonfeng/sandwich` and the world-model notebook use the `-share` source bundle; neither
  is self-contained. All inspected notebooks rely on attached datasets.

## Safe run boundary

`kernel-metadata.json` creates a new private Kaggle notebook. Running it performs an offline
public-game evaluation and writes a dummy `submission.parquet`; it does not call the Kaggle
competition submission API. Do not use `kaggle competitions submit`, do not convert it into a
code-competition submission, and do not promote it based on one noisy run.

## Next controlled ablations

After the exact artifact completes, build separate private copies from this frozen notebook:

1. AGI_8 on / AGI_9 off (60-second yield).
2. AGI_8 off / AGI_9 on (90-second yield).
3. Stock artifact (both off), if the exact source bundle can expose the original method safely.
4. Only after replicated public-set evidence, add EXP-DUCK-024's tn36 postlude as a separate,
   signature-gated arm. Keep ft09 helper work isolated until its complete-board objective is solved.

Because fixed-config Duck runs are highly variable, compare at least 2-3 runs per promising arm,
report ex-ft09 as well as all-25, and treat the public leaderboard score as confirmation rather
than attribution.
