# EXP-DUCK-039 — Qwen3.8 Version 3 recovery

Recovered from the private Kaggle kernel
`jatalepawan/arc3-qwen38-anim-repro-20260908` on 2026-09-21.

## Official result

- Submission ID: `56228748`
- Submitted: `2026-09-14 10:31:34 UTC`
- Description: `EXP-DUCK-039 Qwen38 Version 3 validated shutdown and public25`
- Status: `COMPLETE`
- Public score: **2.89**

## Recovered files

- `v3/arc3-qwen38-anim-repro-20260908.ipynb`: exact current Kaggle source.
- `v3/kernel-metadata.json`: inputs, model, image, and accelerator metadata.
- `version-3-output.tar.zst`: lossless archive of the full 25-game output bundle.
- `output_manifest.json`: path, size, and SHA-256 for every archived file.
- `score.json`: readable copy of the frozen offline scorer output.
- `per_game_summary.csv`: compact per-game score/action/token/runtime table.

The output archive contains `benchmark.json`, 25 event JSONL files, 25 viewer-data
files, 25 prompt logs, three solver-analysis HTML files, `score.json`, the patched
teardown helper, and run bookkeeping. Extract with:

```bash
tar --zstd -xf version-3-output.tar.zst
```

Archive integrity was verified with `zstd -t`. The exact notebook SHA-256 is:

```text
7043af480da256c60e619e95f619d9e660765ed0363ca68e906f439c725a9c88
```

## Offline run represented by the output bundle

- Run window: `2026-09-11T10:47:37` to `2026-09-11T12:59:38`
- Public games: `25`
- Frozen scorer mean: `5.8808820058`
- Actions: `3,731`
- Generated tokens: `1,868,372`
- Terminal state: all 25 runs finalized as `gave_up`

This offline public-game score is not directly comparable with the hidden Kaggle
leaderboard score of `2.89`.

## Historical-version limitation

Kaggle CLI 2.2.4 successfully pulled the current source and current output, but
`kernels pull .../1` and `.../2` are forbidden by Kaggle's API for this private
kernel. Version 2 remains visibly accessible at script version ID `348201106`, and
Version 3 is script version ID `349010440`, but older exact `.ipynb` files were not
fabricated or represented as recovered. A browser download attempt also failed.

The evidence supports treating Version 3 as the clean reproducible baseline. It
does not establish that a source-code change between Versions 2 and 3 caused the
2.89 score; run variance and/or submission-run state remain plausible until the
exact older notebook is recovered.
