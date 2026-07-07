# Duck Public Reproduction - Terminal-Run Kaggle Package

This folder packages the 2026-07-04 Duck public reproduction workbench so it can be pushed and monitored from the terminal with the Kaggle CLI.

Files:

```text
arc3_20260704_duck_public_repro_workbench.ipynb
kernel-metadata.json
```

Kaggle inputs:

```text
Competition:
- arc-prize-2026-arc-agi-3

Datasets:
- driessmit1/arc3-vllm-h100-wheelhouse-v3
- jeroencottaar/taaf-kaggle-source-share
- driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot
```

Terminal workflow:

```bash
python scripts/kaggle_kernel_run.py info
python scripts/kaggle_kernel_run.py push
python scripts/kaggle_kernel_run.py watch
python scripts/kaggle_kernel_run.py output
python scripts/kaggle_kernel_run.py summarize
```

Notes:

```text
- `push` starts a Kaggle kernel run.
- The run can take hours.
- `output` downloads the latest kernel output into artifacts/kaggle/duck_public_repro_terminal_run/latest/.
- `summarize` reads benchmark.json from that output folder when available.
```

