# 2026-09-21 — Kaggle / Desktop / Web Reconciliation

## Outcome

The project state has been reconciled through the official Kaggle submission
history and the private Qwen3.8 notebook artifacts. The active validated public
baseline is now **EXP-DUCK-039 at 2.89**, not EXP-DUCK-038 at 1.12.

## What was done

- Installed Kaggle CLI `2.2.4` and configured a new account API token with
  owner-only local permissions.
- Verified authenticated, read-only access to Pawan's private Kaggle kernels.
- Pulled the exact current source and metadata for
  `jatalepawan/arc3-qwen38-anim-repro-20260908`.
- Downloaded the complete current output bundle and preserved it as a verified
  compressed archive with a file-by-file SHA-256 manifest.
- Recovered the official ARC-AGI-3 submission ledger through Kaggle CLI.
- Generated a readable per-game result table and preserved the frozen scorer
  output.
- Updated the experiment tracker and session-note index.
- Did **not** launch, rerun, edit, or submit any Kaggle notebook.

## Official score progression recovered from Kaggle

| Experiment | Submission ID | Date (UTC) | Public score |
|---|---:|---|---:|
| Original Duck reproduction | `54339875` | 2026-07-04 | 0.84 |
| EXP-DUCK-009 | `54851402` | 2026-07-20 | 0.92 |
| EXP-DUCK-024 | `54965732` | 2026-07-25 | 1.11 |
| EXP-DUCK-026 | `55001932` | 2026-07-26 | 0.86 |
| EXP-DUCK-038 | `55990103` | 2026-09-03 | 1.12 |
| **EXP-DUCK-039** | **`56228748`** | **2026-09-14** | **2.89** |

## EXP-DUCK-039 configuration recovered

- Notebook: `ARC3 Qwen38 Anim Repro 20260908`, Version 3.
- Kaggle script version ID: `349010440`.
- Model: `RadixArk/Qwen3.8-Flash-Next-NVFP4`.
- Accelerator: `NvidiaRtxPro6000`.
- Duck game concurrency: `28`.
- Per-game budget: `7,920` seconds.
- Analyzer timeout: `900` seconds.
- Action cap: none.
- Context: 32K, ModelOpt NVFP4 weights, BF16 KV compute, three-token NEXTN MTP,
  8,192 batched-token cap, eight vLLM sequences, CUDA graph capture size 32,
  prefix caching disabled.
- Reliability additions: owned-server watchdog, at most two restarts, bounded
  teardown GPU-drain wait, and explicit 25-public-game validation.

Notebook SHA-256:
`7043af480da256c60e619e95f619d9e660765ed0363ca68e906f439c725a9c88`.

## Recovered offline Version 3 run

The current Kaggle output corresponds to a full public-25 run from September 11:

- frozen scorer mean: `5.8808820058`;
- 25/25 game records present;
- 3,731 total actions;
- 1,868,372 generated tokens;
- runtime approximately 2h12m;
- all game records terminated cleanly as `gave_up`;
- strongest public-game scores included `vc33` 21.4286, `ft09` 18.3945,
  `dc22` 13.8993, `re86` 13.8411, and `cn04` 13.2227;
- seven public games scored zero: `wa30`, `sp80`, `m0r0`, `sk48`, `g50t`, `ls20`,
  and `tr87`.

The `5.8809` offline public-game mean and `2.89` hidden leaderboard result use
different evaluation sets and must not be compared as if they were repeated
measurements of the same score.

## What worked

- Kaggle CLI provided exact, reproducible current source, metadata, outputs, and
  submission history.
- The complete output compressed from roughly 109 MB to about 3.8 MB, allowing
  the replay evidence to be preserved without bloating the repository.
- The repository-to-Kaggle gap is now bounded: GitHub stopped at September 7 / 
  EXP-DUCK-038, while Kaggle records EXP-DUCK-039 on September 14.

## What failed or remains uncertain

- Kaggle's API returned `403 Forbidden` for explicit historical pulls of Versions
  1 and 2. The exact older `.ipynb` files were therefore not recovered.
- Browser download of Version 2 failed at Kaggle's download layer.
- Version 2 is identified as script version `348201106`, but without its exact
  source artifact we cannot make a trustworthy line-by-line Versions 2–3 diff.
- Consequently, the 2.89 improvement cannot yet be attributed causally to a
  particular code change. It may include material run variance.
- Files that existed only in the disconnected Codex Desktop workspace remain
  outside this reconciliation unless later pushed or uploaded.

## Current best result

- Official public baseline: **2.89**.
- Experiment: `EXP-DUCK-039`.
- Submission: `56228748`.
- Status: `COMPLETE`.
- Preserve unchanged as the always-submittable reference; do not overwrite or
  rerun it while investigating improvements.

## Files changed

- `artifacts/kaggle/exp-duck-039-qwen38/README.md`
- `artifacts/kaggle/exp-duck-039-qwen38/v3/arc3-qwen38-anim-repro-20260908.ipynb`
- `artifacts/kaggle/exp-duck-039-qwen38/v3/kernel-metadata.json`
- `artifacts/kaggle/exp-duck-039-qwen38/version-3-output.tar.zst`
- `artifacts/kaggle/exp-duck-039-qwen38/output_manifest.json`
- `artifacts/kaggle/exp-duck-039-qwen38/score.json`
- `artifacts/kaggle/exp-duck-039-qwen38/per_game_summary.csv`
- `docs/experiment_tracker.md`
- `session_notes/index.md`
- this session note

## Next session plan

1. Recover the exact Version 2 notebook from the Desktop workspace or a manual
   Kaggle export, then perform a cell-level semantic diff against Version 3.
2. Build the replay dashboard from the recovered event JSONL, viewer data, and
   prompt logs, starting with `vc33`, `ft09`, `dc22`, and the zero-score games.
3. Separate infrastructure gains from solver gains: serving throughput,
   watchdog/teardown reliability, token budget, and Qwen3.8 reasoning quality.
4. Run no new competition submission until a controlled, locally auditable
   candidate has a clear causal hypothesis and rollback path.
5. Continue using EXP-DUCK-039 unchanged as the P1 robust baseline while P2/P3
   work focuses on cross-game world-model reuse and action efficiency.
