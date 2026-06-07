# 2026-06-06 — NVIDIA Nemotron Bit Reweight v3 600 Launch Notes

## Context

Competition: NVIDIA Nemotron Model Reasoning Challenge.

Session objective: analyze the completed v2 bit reweight result and launch the next controlled dose experiment.

Leaderboard context reported by user:

```text
Current clean score: 0.84
Approx rank: 2055
Silver medal boundary: ~0.86
Top score last checked: ~0.89
```

## Result: bit reweight v2 worked

Submission:

```text
V2-End-to-end finetuning LB082 - bit reweight - Version 1
Public score: 0.84
```

This improves the clean public-data path:

| Run | Change | Public score | Interpretation |
|---|---:|---:|---|
| Hui Kang public baseline | no reweight | 0.82 | Original clean baseline |
| Bit reweight v1 | +200 bit examples | 0.83 | Bit exposure helps |
| Bit reweight v2 | +400 bit examples | 0.84 | Bit exposure still scales |
| Taha copied/private reference | different copied private dataset corpus | 0.86 | Reference only, not independent baseline |

## v2 log confirmation

The v2 log confirmed that the intended patch executed exactly:

```text
Loaded 7830 problem_ids in training order from /kaggle/input/datasets/huikang/huikang-nemotron-repository-snapshot/nemotron-master/training/sft/04-08-16-14/logprobs/index.jsonl
BIT_REWEIGHT=True: found 1602 bit ids in train.csv; 1354 matching examples in loaded corpus
BIT_REWEIGHT=True: duplicated 400 bit examples; examples 7830 → 8230
Loaded 8230 examples, 30,627,184 tokens (unmasked=29,245,662)
RESET_WEIGHTS=True — skipping pretrained adapter load; using fresh LoRA init
SHUFFLE_DATASET=False: keeping corpus order (8230 examples)
WARNING: NUM_STEPS=1000 exceeds max_steps=257 (8230 examples // 32 batch). Clamping to 257.
Training: 257 steps, batch_size=32, micro_batch_size=4, lr=0.0002
```

Important configuration remained unchanged:

```text
RESET_WEIGHTS=True
LEARNING_RATE=2e-4
BATCH_SIZE=32
MICRO_BATCH_SIZE=4
SHUFFLE_DATASET=False
LORA_RANK=32
LORA_ALPHA=32
LORA_DROPOUT=0.0
MOE_TIE_WEIGHTS=True
```

## Interpretation

The v2 score is a strong positive signal because:

1. The only intentional change from v1 was increasing duplicated bit examples from 200 to 400.
2. The public score improved again, from 0.83 to 0.84.
3. This makes the bit-reweight path a controlled experiment ladder rather than a random rerun.
4. The clean score is now only about +0.02 away from the reported silver boundary.

Working hypothesis:

```text
The Hui Kang public baseline underlearned bit manipulation.
More bit trace exposure improves long binary reasoning / final boxed answer behavior.
```

Risk remains:

```text
Too much bit reweighting may cause category forgetting in gravity, numeral, unit conversion, cipher, or equation categories.
```

This risk was reinforced by the prior discussion evidence from Taha about category-level regressions and multi-task balancing.

## Next experiment launched: v3 600

Based on the successful 200 → 400 ladder, user launched the next controlled dose experiment via Save & Run.

Notebook/run label:

```text
End-to-end finetuning LB084 - bit reweight v3 600
```

Only intended update:

```python
N_EXTRA_BIT_EXAMPLES = 600
```

Everything else should remain identical:

```python
BIT_REWEIGHT = True
RESET_WEIGHTS = True
LEARNING_RATE = 2e-4
BATCH_SIZE = 32
MICRO_BATCH_SIZE = 4
SHUFFLE_DATASET = False
LORA_RANK = 32
LORA_ALPHA = 32
LORA_DROPOUT = 0.0
MOE_TIE_WEIGHTS = True
```

Expected v3 log:

```text
BIT_REWEIGHT=True: found 1602 bit ids in train.csv; 1354 matching examples in loaded corpus
BIT_REWEIGHT=True: duplicated 600 bit examples; examples 7830 → 8430
SHUFFLE_DATASET=False: keeping corpus order (8430 examples)
WARNING: NUM_STEPS=1000 exceeds max_steps≈263 (8430 examples // 32 batch). Clamping to ~263.
Training: ~263 steps, batch_size=32, micro_batch_size=4, lr=0.0002
```

## Decision rule after v3 score

| v3 public score | Interpretation | Next action |
|---:|---|---|
| >=0.85 | Bit scaling still works | Select v3; consider v4 800 only if compute reserve is safe |
| 0.84 | Bit-only plateau | Keep v2 selected; pivot to equation/symbolic or validation-driven patch |
| <0.84 | Too much bit exposure | Keep v2 selected; do not scale bit further |
| >=0.86 | Silver-boundary result | Protect, validate, and avoid risky changes unless enough compute remains |

## What not to do yet

Do not:

- jump directly to all 1354 matching bit examples;
- change LoRA rank/alpha/dropout/target modules;
- continue training from an existing adapter;
- use Taha private dataset paths;
- add cryptarithm/equation data before v3 score is known;
- use notebook-page submit button if it reruns the notebook unnecessarily.

## Current best selected submission

Until v3 beats it, select/protect:

```text
V2-End-to-end finetuning LB082 - bit reweight - Version 1
Public score: 0.84
```

## Bottom line

The bit-reweight experiment has produced two consecutive clean gains: 0.82 → 0.83 → 0.84. The v3 600 run is justified as the next minimal dose-response test. After v3, the strategy should depend strictly on score: continue bit scaling only if it improves, otherwise pivot to balancing/equation-symbolic improvements while protecting the 0.84 clean submission.
