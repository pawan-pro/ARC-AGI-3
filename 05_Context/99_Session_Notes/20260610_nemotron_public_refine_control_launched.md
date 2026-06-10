# 2026-06-10 — NVIDIA Nemotron Public Refine Control Launched

## Context

Competition: NVIDIA Nemotron Model Reasoning Challenge.

Session date: 2026-06-10.

Current competition status reported by user:

```text
Current best clean score: 0.84
Current approximate position: ~2124
Bronze / silver cluster: ~0.86
Gold cluster: ~0.87
Top scores: ~0.89 / 0.88 / 0.88
Competition closes: 2026-06-15
Compute before this session: ~17h50m, with one likely ~30h refresh before deadline
Compute after Refine run: ~17h51m reported by user
```

Note: The public leaderboard uses approximately 50% of test data; final ranking is on the other 50%, so public-score selection is noisy and can overfit.

## Prior experiment state

| Run | Strategy | Public score | Decision |
|---|---|---:|---|
| V1 | bit reweight +200 | 0.83 | improved over baseline |
| V2 | bit reweight +400 | 0.84 | current best clean path |
| V3 | bit reweight +600 | 0.84 | plateau |
| V4 | bit400 + equation200 long-CoT replay | 0.67 | reject |
| V5 | V2 warmstart + concise alignment, 28 steps | 0.84 | safe but neutral |

Interpretation:

```text
Bit reweighting worked up to 400 examples.
Bit-only scaling plateaued at 600.
Broad equation/symbol-transform long-CoT duplication collapsed.
Tiny concise alignment was safe but did not improve public LB.
```

## Discussion review highlights

Latest Kaggle discussions reviewed during the session:

1. Routed MoE expert LoRA keys
   - Competitors noted that Huikang-style adapters appear to include routed expert LoRA keys.
   - This supports avoiding small attention-only adapter formats.
   - No late adapter-key surgery recommended because submission compatibility risk is high.

2. Training within 12-hour limit
   - Competitors recommend one epoch / step-limited training / checkpoint continuation.
   - Confirms our plan to use step-limited runs rather than multi-epoch experiments.

3. GRPO speed issue
   - GRPO generation can be extremely slow unless using a transformers fix and avoiding old `trust_remote_code` cache handling.
   - GRPO remains out of scope for final push because we do not already have a reliable GRPO pipeline.

4. Symbol transform / cryptarithm discussion
   - Symbol-transform and cryptarithm remain major unsolved areas.
   - However, broad long-CoT category reweighting already failed for us.
   - Cryptarithm-heavy long-CoT approaches are complex and can regress saturated categories.

5. Taha / non-determinism discussion
   - Public LB and training can swing materially.
   - Repeating promising configs may be worthwhile near 0.85–0.86, but not for failed configs.

6. CPMP / overfitting comment
   - Local validation is recommended because the test set is small.
   - Public LB should not be the only guide, though it remains critical for competition selection.

## Public Huikang adapter discovery

User inspected Huikang's public `nemotron-adapter` model and related code notebooks.

Important artifacts reviewed:

```text
Model: huikang/nemotron-adapter
Version: 20
Files: adapter_config.json, adapter_model.safetensors, README.md
Model size: ~1.54 GB
```

Adapter config highlights:

```json
{
  "peft_type": "LORA",
  "r": 32,
  "lora_alpha": 32,
  "lora_dropout": 0,
  "target_modules": "all-linear",
  "task_type": "CAUSAL_LM"
}
```

Interpretation:

```text
This is a full all-linear LoRA, consistent with a richer adapter than our small experimental changes.
It likely includes the high-value MoE / expert-path LoRA behavior discussed publicly.
```

Public notebook observations from Huikang adapter Code tab:

| Notebook | Reported public score | Relevance |
|---|---:|---|
| Tinker submission notebook | 0.85 | fast public adapter submit path |
| Tinker Adapter to Ready To Submit Adapter | 0.86 | cheap conversion control |
| Refine | 0.86 | stronger conversion/compression path |
| NVIDIA Nemotron | 0.85 | additional reference |

## Refine notebook analysis

The uploaded/refined public notebook is not a training notebook. It is a conversion / packaging notebook.

Core behavior:

```python
path_model = "/kaggle/input/models/huikang/nemotron-adapter/transformers/default/20"
output_zip_dir = "/kaggle/working/nemotron-adapter-ready-to-submit"

weights.build_lora_adapter(
    base_model="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
    adapter_path=path_model,
    output_path=output_zip_dir,
)

os.system(f"zip -r submission.zip {output_zip_dir}")
```

Refine-specific behavior noted:

```text
FORCED_FUSED_RANK = 32
SVD-style compression / conversion of fused projections
custom weighting with higher v_proj priority and later-layer boosting
q_proj / k_proj mild amplification
```

Inference:

```text
Refine likely improves over direct adapter submission by converting/compressing the Tinker/Unsloth-style adapter into a Kaggle-ready standard LoRA package while preserving high-value directions.
```

## Action taken

User ran the Refine notebook and submitted it for scoring.

Run status reported by user:

```text
Refine notebook: ran successfully
Submission: submitted for scoring
Compute remaining after run: ~17h51m
```

## Why this run is high ROI

This was prioritized before V6 because:

1. Runtime is very low relative to SFT runs.
2. Public notebook reports 0.86.
3. A 0.86 score would move the user from the 0.84 cluster toward bronze/silver boundary.
4. It uses a public Huikang adapter/control path, avoiding additional long-CoT reweighting risk.
5. It provides an immediate stronger fallback if reproduced.

## Decision rule after Refine score

| Refine score | Interpretation | Next action |
|---:|---|---|
| >=0.86 | Medal-boundary public control reproduced | Select/protect immediately; next run should be low-LR concise alignment from Refine adapter |
| 0.85 | Better than current clean 0.84 | Select as fallback; try Refine warmstart concise/answer-only |
| 0.84 | Neutral vs V2 | Keep V2 clean best; proceed to V6 from V2 |
| <0.84 | Public conversion not robust in our environment | Reject; return to V2 clean path |
| error / invalid package | Fix only if obvious; otherwise abandon to preserve compute |

## Updated next experiment tree

### If Refine scores 0.86+

Goal shifts from reaching 0.86 to protecting it and testing a small push to 0.87.

Candidate next runs:

```text
R1: Refine warmstart + concise alignment, 28 steps, LR 7e-7 or 1e-6
R2: Refine warmstart + answer-only alignment, 28 or 56 steps, LR 7e-7 or 1e-6
```

Strict constraints:

```text
RESET_WEIGHTS = False
no long-CoT replay
no broad equation reweight
no cryptarithm-heavy run
no adapter-key surgery
```

### If Refine scores 0.85

Keep Refine as best fallback and test one low-risk alignment run from it.

### If Refine scores 0.84 or below

Return to original clean path:

```text
V6: V2 warmstart concise alignment, 56 steps, LR 1.4e-6
V7: V2 warmstart answer-only alignment, 56 steps, LR 1e-6
```

## What not to do now

Do not spend compute on:

```text
GRPO setup
cryptarithm-heavy 500-line CoT traces
broad equation/cryptarithm long-CoT reweighting
bit800 / all bit examples
router/embedding LoRA changes
Unsloth fused-expert key conversion from scratch
2-epoch SFT
high-LR continuation
```

## Bottom line

The session identified a cheap public adapter-control path with reported 0.86 score. The Refine notebook ran and is now submitted for scoring. Until its result is known, hold off on V6 training. If Refine scores 0.86, protect it and use remaining compute only for very low-LR, short-answer alignment variants from the Refine adapter. If it fails or ties 0.84, resume the V2-based concise alignment plan.
