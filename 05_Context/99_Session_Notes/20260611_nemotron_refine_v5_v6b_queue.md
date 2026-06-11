# 2026-06-11 — NVIDIA Nemotron Refine V5 Retry and V6B Queue Notes

## Context

Competition: NVIDIA Nemotron Model Reasoning Challenge.

Session date: 2026-06-11.

Current scoreboard state reported by user:

```text
Refine - Version 1: 0.84
V6-End-to-end finetuning LB084 - concise alignment - Version 1: 0.84
V4-End-to-end finetuning LB084 - bit400 equation r - Version 2: 0.67
V3-End-to-end finetuning LB082 - bit rewei - Version 1: 0.84
V2-End-to-end finetuning LB082 - bit reweight - Version 1: 0.84
```

Current selected / protected score remains:

```text
0.84
```

## Existing experiment state

| Run | Strategy | Public score | Decision |
|---|---|---:|---|
| V2 | bit reweight +400 | 0.84 | current clean best / protected |
| V3 | bit reweight +600 | 0.84 | plateau |
| V4 | bit400 + equation200 long-CoT replay | 0.67 | reject |
| V5/V6 concise 28-step | V2 warmstart + concise alignment | 0.84 | safe but neutral |
| Refine latest/current | Huikang adapter conversion | 0.84 | valid but no uplift |

Interpretation:

```text
Bit reweighting improved score to 0.84 but plateaued.
Broad equation long-CoT replay caused severe forgetting/collapse.
28-step concise alignment was safe but did not improve.
Latest/current Refine conversion was valid but did not reproduce public 0.86.
```

## Refine notebook distinction clarified

Two Refine notebooks were discussed:

```text
refine (2): yesterday's latest/current Refine run; completed; scored 0.84
refine v-5: today's older public V5 notebook; historically showed 0.86; initially failed in RTX competition environment
```

Important conclusion:

```text
refine (2) is not useful as an uplift because it already scored 0.84.
refine v-5 may still be worth one retry only if run with internet enabled and no accelerator/CPU mode.
```

## Refine V5 failure diagnosis

The older public Refine V5 notebook failed in the RTX Pro 6000 competition environment because its first cell requires GitHub access:

```python
!pip install --no-cache-dir --force-reinstall "tinker-cookbook @ git+https://github.com/thinking-machines-lab/tinker-cookbook.git@nightly"
```

Observed error:

```text
fatal: unable to access 'https://github.com/thinking-machines-lab/tinker-cookbook.git/': Could not resolve host: github.com
ModuleNotFoundError: No module named 'tinker_cookbook'
```

Diagnosis:

```text
The failure is an offline dependency issue, not a model/input issue.
RTX Pro 6000 competition notebooks cannot enable internet in this setup.
```

Potential workaround:

```text
Run Refine V5 with no accelerator / CPU and internet enabled, because the notebook is mainly adapter conversion/packaging rather than training.
```

Decision rule for Refine V5 retry:

| Refine V5 score | Action |
|---:|---|
| 0.86 | select/protect immediately; use as best medal-boundary candidate |
| 0.85 | select as better fallback than 0.84 |
| 0.84 | no improvement; continue V2-based path |
| fail/error | abandon Refine V5; do not spend more time on dependency packaging unless trivial |

## V6B notebook created

A corrected V6B notebook was created from the existing concise-alignment notebook.

Notebook file delivered to user:

```text
v6b-end-to-end-finetuning-lb084-concise-alignment-56steps.ipynb
```

Purpose:

```text
Test whether the previous 28-step concise alignment was undertrained.
```

Key config:

```python
NUM_STEPS = 56
LEARNING_RATE = 1.4e-6
RESET_WEIGHTS = False
CONCISE_ALIGNMENT = True
BIT_REWEIGHT = False
```

Warmstart path:

```python
WARMSTART_ADAPTER_ZIP = "/kaggle/input/notebooks/jatalepawan/v2-end-to-end-finetuning-lb082-bit-reweight/submission.zip"
```

No internet or Refine dependency is required.

Expected log:

```text
Using warmstart adapter zip: ...v2-end-to-end-finetuning-lb082-bit-reweight/submission.zip
Loaded 9500 train.csv rows for concise alignment
Training: 56 steps, batch_size=32, micro_batch_size=4, lr=1.4e-06
Wrote submission.zip
```

## Execution plan agreed

Because Refine V5 scoring may take time and V6B is independent of Refine, the recommended action was:

```text
Run V6B on RTX Pro 6000 now.
Do not submit V6B for scoring until Refine V5 result is known.
```

Rationale:

```text
V6B uses V2 0.84 adapter as warmstart and does not conflict with Refine.
Running it now avoids idle waiting time.
If Refine V5 is bad/neutral, V6B output will already be ready to submit.
If Refine V5 scores 0.85/0.86, V6B may be deprioritized or used only as an additional data point.
```

Decision table:

| Refine V5 score | V6B status | Action |
|---:|---|---|
| >=0.85 | V6B complete | select Refine V5; submit V6B only if useful as extra data point |
| 0.84 | V6B complete | submit V6B for scoring |
| <0.84 / failed | V6B complete | submit V6B for scoring |
| Refine pending too long | V6B complete | wait if close; otherwise submit V6B to avoid idle time |

## V6B decision rule after scoring

| V6B public score | Action |
|---:|---|
| >=0.85 | select; try 84-step variant if compute allows |
| 0.84 | move to V7 answer-only alignment |
| <0.84 | reject; keep V2 selected |

## V7 placeholder if needed

If V6B stays 0.84, next low-risk experiment:

```text
V7 answer-only alignment, V2 warmstart
```

Candidate target format:

```text
Final answer: \boxed{ANSWER}
```

or stronger answer-only format:

```text
\boxed{ANSWER}
```

Candidate config:

```python
NUM_STEPS = 56
LEARNING_RATE = 1.0e-6
RESET_WEIGHTS = False
CONCISE_ALIGNMENT = True
BIT_REWEIGHT = False
```

## What not to do now

Do not spend immediate compute on:

```text
GRPO setup
cryptarithm-heavy long-CoT traces
broad equation/cryptarithm replay
bit800 / all bit examples
adapter key surgery
Unsloth fused expert conversion
2-epoch training
high-LR continuation
```

## Bottom line

Refine latest/current scored 0.84 and did not improve. Older Refine V5 may still be tested only through a CPU/no-accelerator internet-enabled workaround. In parallel, V6B 56-step concise alignment has been created and should be run on RTX now, but held from scoring until Refine V5 result is known. The protected fallback remains V2 0.84.
