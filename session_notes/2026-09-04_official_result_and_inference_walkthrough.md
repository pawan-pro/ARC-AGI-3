# 2026-09-04 — Official result and inference walkthrough

## Verified competition result

Kaggle submission history was queried live on September 4:

- Submission: `55990103`.
- Experiment: `EXP-DUCK-038 exact public AGI9 frozen reproduction`.
- Status: `COMPLETE`.
- Official public score: **1.12**.
- Previous best: `EXP-DUCK-024`, submission `54965732`, **1.11**.
- Observed leaderboard improvement: **0.01**; one run does not establish a reliable advantage.

Important correction to the September 3 discussion: **1.306 (rounded 1.31) was
the offline 25-game mean, not a leaderboard score**. Comparing that number with
the official 1.11 and calling it a 17.7% improvement was invalid. Keep offline
and competition evaluations separate. The completed offline run recorded 15
levels across 13 scoring games, with no complete game wins; ft09 and tn36 were zero.

## Notebook logic explained

The frozen reproduction uses `vrfai/Qwen3.6-27B-FP8`, approximately 27 billion
parameters. Weights are supplied by an attached Kaggle dataset, loaded into GPU
memory, and served locally through vLLM; there is no live Hugging Face inference
call or model training in this workflow.

The harness repeatedly:

1. Supplies available controls, the current board image, structured object data,
   prior observations, and a compact working theory.
2. Asks the model to infer game rules and goals and choose a useful action.
3. Lets the model use Python to inspect objects, compare frames, calculate, or search.
4. Executes the chosen game action.
5. Returns updated evidence so the model can check and revise its theory.

The model knows the available command names, not necessarily their puzzle-specific
effects. Object movement is generally inferred by comparing observations, rather
than supplied as a complete semantic explanation.

The same Qwen model serves concurrent games; this is not a multi-model ensemble.
It is multimodal because the inputs include images alongside textual/structured
information. Its weights stay fixed; adaptation within a game comes through context.

Compared with EXP-DUCK-024, the public notebook adds AGI_8 (interrupt immediately
repeated no-effect directional moves within a batch) and AGI_9 (90-second instead
of 60-second analyzer yield), and omits the notebook-level ft09/tn36 helpers.
The base framework also differs, preventing attribution of the score change to
either patch alone.

## Training, inference, and interfaces

- Weights are learned numbers, not forward/backward passes themselves.
- Training uses forward passes, a loss, backpropagation, and an optimizer to update weights.
- Inference loads saved weights and uses forward computation to generate output tokens.
- Text is tokenized first, then represented as embeddings.
- A web page or terminal is the interface, not the inference engine.
- The harness automates message preparation, response handling, and tool/action execution
  through the server API; it does not require an HTML interface.
- **Prefill** is processing the input prompt; **decoding** generates output tokens.

## Model size and infrastructure discussion — estimates, not deployment evidence

For 27 billion parameters, ideal weight-only storage is approximately 54 GB at
16 bits, 27 GB at 8 bits, or 13.5 GB at 4 bits. Actual storage and inference memory
include overhead, caches, and temporary workspaces. Two GPUs are not inherently
required for the Qwen model; a sufficiently large single GPU can host it.

Official GPT-5.6 Sol documentation did not provide a parameter count or weight
storage size, so none was asserted.

As a frontier open-weight example, the inspected Kimi K3 model card lists 2.8T
total parameters, 104B active per token, and MXFP4 weights. Open-weight does not
automatically mean fully open-source; the repository uses a custom Kimi K3 license.
The ideal four-bit weight calculation gives approximately 1.4 TB, not a measured
checkpoint size. Mixed precision and quantization metadata add overhead.

NVIDIA specifications inspected in this session list 1,440 GB across eight B200
GPUs and approximately 2.1 TB across eight B300 GPUs. Based only on memory arithmetic,
16 B200 GPUs or eight B300 GPUs were discussed as possible planning configurations.
**Neither configuration was validated for Kimi K3, and neither is a purchasing recommendation.**
Software support, actual checkpoint memory, interconnects, context length, latency,
prefill load, and concurrency must be benchmarked.

The user narrowed the serving example to **1,000 simultaneous users**. At an assumed
30 output tokens/second/user, demand is 30,000 output tokens/second. An explicitly
hypothetical server throughput of 1,000 output tokens/second on eight B300 GPUs
would imply 30 servers / 240 GPUs, or about 38 servers / 304 GPUs with 25% headroom.
**The 1,000-token server throughput was invented for arithmetic illustration, not
measured or sourced; consequently the roughly 300-GPU figure is not a capacity estimate.**
No hardware budget, procurement, new deployment, or additional model run was authorized.

Sources inspected:

- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://huggingface.co/moonshotai/Kimi-K3/blob/main/README.md
- https://www.nvidia.com/en-us/data-center/dgx-b200/
- https://www.nvidia.com/en-us/data-center/dgx-b300/

## Tomorrow's handoff

Resume from the distinction between harness orchestration, model prefill, decoding,
and game actions. If continuing infrastructure sizing, use a real deployment benchmark
and explicit latency/context/concurrency targets rather than the illustrative figures.

For ARC experiments, preserve the frozen 1.12 submission and the prior 1.11 baseline.
The proposed next research steps remain repeated offline evaluation and controlled
AGI_8/AGI_9 ablations, followed by a small controlled model comparison if desired.
No additional run or competition submission was launched in this session.

This session-note commit intentionally excludes existing modifications to
`docs/experiment_tracker.md` and `scripts/kaggle_kernel_run.py`.
