# 2026-06-06 — NVIDIA Nemotron Bit Reweight v2 and Discussion Notes

## Context

Competition: NVIDIA Nemotron Model Reasoning Challenge.

Session objective: analyze the completed bit reweight v1 result, incorporate new discussion-post evidence, and decide the next controlled notebook experiment.

Current competition timing and GPU budget noted by user:

```text
9 days until competition close
29h53m GPU compute available
~150h until quota refresh
```

## Score update

The clean public-data bit reweight experiment improved the score:

| Run | Data/source | Change | Public score | Status |
|---|---|---|---:|---|
| Hui Kang public V1 baseline | Hui Kang public repository snapshot | no patch | 0.82 | old clean baseline |
| Bit reweight v1 | Hui Kang public repository snapshot | duplicate 200 bit examples | 0.83 | new clean best |
| Taha copied notebook | Taha copied notebook/private dataset input | different corpus | 0.86 | reference only, not independent baseline |

Interpretation:

- The +200 bit duplicate patch worked.
- The improvement from 0.82 to 0.83 is a positive signal that bit manipulation was underweighted or underlearned in the public baseline.
- The clean independent path remains Hui Kang public baseline + our own data reweight patch. The Taha 0.86 run remains a reference ceiling due to private copied data dependency.

## v1 log details

The user attached the v1 score/log. Key confirmed lines from the completed run:

```text
BIT_REWEIGHT=True: found 1602 bit ids in train.csv; 1354 matching examples in loaded corpus
BIT_REWEIGHT=True: duplicated 200 bit examples; examples 7830 → 8030
Loaded 8030 examples, 29,230,248 tokens
Training: 250 steps, batch_size=32, micro_batch_size=4, lr=0.0002
Wrote submission.zip
```

This confirms the patch ran correctly and preserved the expected public Hui Kang data path and model configuration.

## Discussion evidence incorporated

Two Kaggle discussion posts were reviewed.

### 1. Taha: cryptarithm improvements but LB stuck at 0.86

Taha reported that improving hard categories such as cryptarithm and equation locally did not necessarily improve leaderboard score because easier/saturated categories regressed.

Important takeaways:

- Multi-task balancing and forgetting are now central risks.
- More data in one category can weaken another category.
- Bit manipulation is noisy and can swing several problems between runs.
- 0.84 vs 0.86 can be partly run-to-run/category variance.
- Avoid LoRA-maxing/router/embedding LoRA changes because they may increase parameter drift and catastrophic forgetting.

Relevant table excerpt from Taha's discussion:

```text
Before additional cryptarithm data:
bit_manipulation: 46/49 = 93.9%
TOTAL: 288/300 = 96.0%
Approx LB: ~0.81

After additional cryptarithm data:
bit_manipulation: 40/49 = 81.6%
TOTAL: 280/300 = 93.3%
Approx LB: ~0.83
```

Key interpretation:

- Local category accuracy and public LB can move differently.
- Category mixture and hidden/public split effects matter.
- We should not blindly increase one category forever.

### 2. Donald Galliano: 100% solve-rate methodology / bit template

Donald’s writeup reinforces why bit traces matter:

- Binary/bit tasks should be solved as per-bit Boolean decomposition.
- The model must spell out bit operations serially instead of doing multi-bit operations in parallel.
- Candidate transformations should be verified against the target input to avoid plausible-but-wrong matches.
- The final answer must be boxed.

This aligns with our earlier validation result where the 0.82 adapter failed bit manipulation due to long outputs and missing boxed binary answers.

## Updated interpretation of v1

The 0.83 v1 result means:

```text
Bit exposure helps, but further bit exposure could plateau or cause regression.
```

It does not prove that aggressively adding all bit traces is safe. Based on discussion evidence, excessive category reweighting may cause forgetting in gravity, numeral, unit conversion, cipher, or equation tasks.

## Next experiment selected: v2 400

The user updated:

```python
N_EXTRA_BIT_EXAMPLES = 400
```

and launched Save & Run.

Notebook name / expected label:

```text
End-to-end finetuning LB083 - bit reweight v2 400
```

Expected changes only:

```python
BIT_REWEIGHT = True
N_EXTRA_BIT_EXAMPLES = 400
```

Everything else should remain unchanged:

```python
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

Expected log lines:

```text
BIT_REWEIGHT=True: duplicated 400 bit examples; examples 7830 → 8230
SHUFFLE_DATASET=False: keeping corpus order (8230 examples)
NUM_STEPS=1000 exceeds max_steps≈257; clamped
Training: ~257 steps, batch_size=32, micro_batch_size=4, lr=0.0002
```

## Updated decision rule after v2

| v2 public score | Interpretation | Next action |
|---:|---|---|
| >=0.84 | 400 helps; consider v3 with 600 bit examples |
| 0.83 | Bit-only dose plateau; stop bit-only escalation |
| <0.83 | 400 overweights bit; keep v1 200 as clean best |
| >=0.85 | Strong independent signal; validate and protect |

Do not jump directly to all 1354 matching bit examples. The discussion evidence suggests category forgetting is a serious risk.

## Proposed experiment queue after v2 score

1. Submit v2 output from the competition submissions page once the run completes.
2. Compare score to 0.83 v1.
3. If v2 >= 0.84:
   - Run v3 with `N_EXTRA_BIT_EXAMPLES = 600`, no other changes.
4. If v2 = 0.83 or worse:
   - Stop bit-only scaling.
   - Consider a small validation-driven patch such as:

```text
bit 200 + equation/symbolic final-answer formatting 100
```

5. Preserve at least 10 hours GPU for final packaging, validation, reruns, and emergency fixes.

## What not to do

Do not:

- Claim Taha 0.86 as independent.
- Switch to Taha private dataset paths.
- Continue training from an adapter.
- Add LoRA to routers or embeddings.
- Change rank/alpha/dropout/target modules.
- Add cryptarithm/equation data before seeing the bit v2 result.
- Run multiple full SFT experiments before submitting/scoring v2.

## Current state at note time

User has:

```text
updated N_EXTRA_BIT_EXAMPLES to 400
started Save & Run
plans to submit after completion
```

Current clean selected baseline should be:

```text
0.83 bit reweight v1, unless v2 beats it
```

## Bottom line

The +200 bit experiment validated the bit-exposure hypothesis. The current v2 run tests whether the gain scales to +400 examples. The main risk is category forgetting, so the next decision should be based strictly on v2 score and, if possible, a small category-level validation check before further escalation.
