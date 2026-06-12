# 2026-06-12 — NVIDIA Nemotron V9 Safe Synthetic Experiment Plan

## Context

Competition: NVIDIA Nemotron Model Reasoning Challenge.

Session date: 2026-06-12.

Current state reported by user:

```text
refine v-5 - Version 2: 0.85
V8 — V2 warmstart answer-only alignment (28 steps): 0.84
```

Competition timeline:

```text
~3 days to competition end
~1h GPU remaining before reset
~30h GPU expected after reset
```

Current best submission:

```text
refine v-5 - Version 2 = 0.85
```

This should remain selected/protected unless another submission scores >=0.86.

## Result interpretation so far

| Submission | Score | Decision |
|---|---:|---|
| refine v-5 Version 2 | 0.85 | selected/protected best |
| V8 V2 warmstart answer-only 28 steps | 0.84 | no uplift |
| V6B V2 warmstart concise 56 steps | 0.83 | reject |
| V5/V6 V2 warmstart concise 28 steps | 0.84 | neutral |
| V2 bit400 | 0.84 | clean fallback |
| V4 bit400 + equation200 long-CoT replay | 0.67 | reject |

Interpretation:

```text
V2 alignment-only path is exhausted.
Answer-format tuning alone does not move score above 0.84.
56-step concise alignment hurt, suggesting over-alignment / forgetting.
Refine V5 conversion remains the best public score at 0.85.
```

## Refine warmstart branch status

Attempted to use Refine V5 0.85 as a warmstart for answer-format alignment.

Outcome:

```text
The notebook correctly resolved the nested adapter directory:
/kaggle/tmp/pretrained_adapter/kaggle/working/nemotron-adapter-ready-to-submit

But only 2/12010 adapter weights loaded into the Unsloth training model.
```

Diagnosis:

```text
Refine V5 is PEFT/vLLM-ready converted adapter format.
The Unsloth training notebook expects the original training adapter key layout.
Direct Refine warmstart training is not compatible without deliberate key remapping.
```

Decision:

```text
Do not continue Refine-warmstart training unless a key-remapping loader is built and validated first.
Current best remains raw Refine V5 = 0.85.
```

## New main attempt: V9 safe synthetic short-answer training

Because pure format alignment has plateaued, the next experiment is a new-data experiment:

```text
V9 = V2 warmstart + train.csv short answers + safe deterministic synthetic examples
```

The target remains answer-only:

```text
\boxed{ANSWER}
```

The experiment avoids:

```text
equation
cryptarithm
long CoT
Refine warmstart
internet dependency
GRPO
adapter key surgery
```

## V9 baseline notebook created

Notebook delivered:

```text
v9-v2-warmstart-safe-synthetic-answer-only-56steps.ipynb
```

Key config:

```python
RESET_WEIGHTS = False
WARMSTART_ADAPTER_ZIP = "/kaggle/input/notebooks/jatalepawan/v2-end-to-end-finetuning-lb082-bit-reweight/submission.zip"

NUM_STEPS = 56
LEARNING_RATE = 7e-7
SHORT_RESPONSE_TEMPLATE = "\\boxed{{{answer}}}"

USE_SAFE_SYNTHETIC = True
N_SYNTH_PER_CATEGORY = 300
SYNTHETIC_CATEGORIES = [
    "bit_manipulation",
    "unit_conversion",
    "numeral",
    "cipher",
    "gravity",
]
```

Synthetic dose:

```text
300 examples/category × 5 categories = 1,500 synthetic examples
9,500 train.csv rows + 1,500 synthetic rows = 11,000 total rows
```

Expected log:

```text
Original train.csv rows: 9500
Synthetic rows: 1500
Total rows for V9: 11000
Synthetic by category: {'bit_manipulation': 300, 'cipher': 300, 'gravity': 300, 'numeral': 300, 'unit_conversion': 300}
Training: 56 steps, batch_size=32, micro_batch_size=4, lr=7e-07
```

Decision rule:

| V9 score | Action |
|---:|---|
| >=0.86 | select/protect; medal-boundary candidate |
| 0.85 | keep as candidate; compare with Refine V5 |
| 0.84 | reject; synthetic did not help |
| <0.84 | reject; synthetic hurt |

## Additional variants created for remaining GPU capacity

User indicated enough GPU capacity to try approximately three more variants and submit for scoring.

Three additional notebooks were created from the V9 notebook.

### V10 — conservative synthetic dose

Notebook:

```text
v10-v2-warmstart-safe-synthetic-conservative-150each-56steps.ipynb
```

Purpose:

```text
Test smaller synthetic dose to reduce over-alignment/forgetting risk.
```

Key changes vs V9:

```python
N_SYNTH_PER_CATEGORY = 150
SYNTHETIC_SEED = 20260613
SYNTHETIC_CATEGORIES = [
    "bit_manipulation",
    "unit_conversion",
    "numeral",
    "cipher",
    "gravity",
]
```

Synthetic dose:

```text
150/category × 5 = 750 synthetic examples
```

### V11 — no-bit safe synthetic

Notebook:

```text
v11-v2-warmstart-safe-synthetic-no-bit-300each-56steps.ipynb
```

Purpose:

```text
Test whether non-bit safe-category coverage helps without disturbing the already-improved bit behavior from V2 bit400.
```

Key changes vs V9:

```python
N_SYNTH_PER_CATEGORY = 300
SYNTHETIC_SEED = 20260614
SYNTHETIC_CATEGORIES = [
    "unit_conversion",
    "numeral",
    "cipher",
    "gravity",
]
```

Synthetic dose:

```text
300/category × 4 = 1,200 synthetic examples
```

### V12 — stronger synthetic dose

Notebook:

```text
v12-v2-warmstart-safe-synthetic-strong-500each-56steps.ipynb
```

Purpose:

```text
Test stronger synthetic exposure after the moderate/conservative runs. Higher-risk, higher-coverage variant.
```

Key changes vs V9:

```python
N_SYNTH_PER_CATEGORY = 500
SYNTHETIC_SEED = 20260615
SYNTHETIC_CATEGORIES = [
    "bit_manipulation",
    "unit_conversion",
    "numeral",
    "cipher",
    "gravity",
]
```

Synthetic dose:

```text
500/category × 5 = 2,500 synthetic examples
```

## Recommended run order

Given compute and deadline pressure:

```text
1. V9  — moderate baseline, 300 each, all safe categories
2. V10 — conservative dose, 150 each, all safe categories
3. V11 — no-bit dose, 300 each, non-bit safe categories
4. V12 — stronger dose, 500 each, only if compute remains or earlier runs are promising
```

If V9 scores >=0.86, select it and deprioritize extra risk.

If V9 scores 0.85, keep it as a candidate and run V10/V11 for comparison.

If V9 scores <=0.84, V10 is still worth one attempt because lower synthetic dose may be safer.

## Final selection policy

Current selected fallback:

```text
refine v-5 Version 2 = 0.85
```

New submissions should only replace it if:

```text
score >=0.86
```

If another run scores 0.85, keep both as candidates, but Refine V5 remains a strong fallback because it is already validated and did not require additional training risk.

## What not to run now

Avoid:

```text
More V2 answer-format-only alignment
V2 concise 84 steps
Refine warmstart without key remapping
Broad equation replay
Cryptarithm-heavy 500-line CoT replay
GRPO setup
Bit800 / all-bit duplication
High-LR continuation
Adapter-key surgery without validation
```

## Bottom line

The final medal push shifts from answer-format-only tuning to short-answer synthetic coverage. V9 and the V10/V11/V12 variants are controlled attempts to add deterministic safe-category coverage while preserving the V2 bit400 reasoning base. Refine V5 0.85 remains selected/protected unless a new run reaches 0.86+.
