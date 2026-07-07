# 2026-07-07 Session Notes - Duck Terminal Run Package

## Session context

The user asked for a notebook/package that can be run from the terminal so future Kaggle runs can be monitored and downloaded for analysis.

Created Kaggle package:

```text
notebooks/04_submission_builds/duck_public_repro_terminal_run/
```

Package files:

```text
arc3_20260704_duck_public_repro_workbench.ipynb
kernel-metadata.json
README.md
```

Created CLI helper:

```text
scripts/kaggle_kernel_run.py
```

Artifact output folder:

```text
artifacts/kaggle/duck_public_repro_terminal_run/latest/
```

## Kaggle package inputs

```text
Competition:
- arc-prize-2026-arc-agi-3

Datasets:
- driessmit1/arc3-vllm-h100-wheelhouse-v3
- jeroencottaar/taaf-kaggle-source-share
- driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot
```

Kaggle kernel id:

```text
jatalepawan/arc-agi-3-duck-public-repro-terminal-run
```

## Terminal workflow

Show package metadata:

```bash
python scripts/kaggle_kernel_run.py info
```

Push to Kaggle and start a run:

```bash
python scripts/kaggle_kernel_run.py push
```

Watch until terminal state:

```bash
python scripts/kaggle_kernel_run.py watch
```

Print logs:

```bash
python scripts/kaggle_kernel_run.py logs
```

Download latest output:

```bash
python scripts/kaggle_kernel_run.py output
```

Summarize downloaded benchmark:

```bash
python scripts/kaggle_kernel_run.py summarize
```

Summarize an existing benchmark file:

```bash
python scripts/kaggle_kernel_run.py summarize --benchmark ~/Downloads/benchmark.json
```

## Validation performed

The helper successfully parsed the package metadata and summarized the existing downloaded benchmark:

```text
games: 25
score_sum: 42.1215
levels: 18 / 183
actions: 3545
tokens: 1636915
zero_token_actions: 2438
```

No Kaggle run was started during this commit.

