# ARC-AGI-3 Durable Context Overview

> Project-local counterpart to the Linear document **“ARC-AGI-3 — Durable Context Memory”** in the Linear project **“ARC-AGI-3 Kaggle 2026.”**

**Context date:** 7 August 2026  
**Competition:** ARC Prize 2026 — ARC-AGI-3  
**Primary research focus:** Duck `ft09`, level five  
**Status:** Active investigation; terminal state and a complete terminal plan remain unknown

## Authority and evidence boundary

This file is a durable research index, not authorization to change Kaggle or repository state. This project-context chat may preserve context, propose hypotheses, design guarded experiments, and interpret audits. It must not launch Kaggle kernels, submit entries, commit, push, or otherwise modify competition state unless Pawan explicitly authorizes the specific action through a coordinator chat.

Use this evidence order when facts conflict:

1. Raw saved grids, transition traces, terminal flags, and immutable artifact hashes.
2. Deterministic full-board comparisons generated from those artifacts.
3. Official Kaggle competition pages for rules, timeline, scoring, and leaderboard state.
4. Dated coordinator/Linear records that identify their underlying evidence.
5. Interpretations and hypotheses, which must remain labelled as such.

A plan, notebook package, kernel status, visible page, or summary is not proof of a gameplay result. A competition fact is not current merely because it appears in this file; recheck drift-prone external state before acting.

## Official competition facts

Facts in this section were checked against the official Kaggle competition pages on 7 August 2026. Kaggle may amend the timeline or rules, so recheck the official pages before any deadline-sensitive action.

### Timeline

| Event | Deadline |
|---|---:|
| Entry deadline | 26 October 2026, 23:59 UTC |
| Team-merger deadline | 26 October 2026, 23:59 UTC |
| Final submission deadline | 2 November 2026, 23:59 UTC |

### Submission and team constraints

- Submission format: Kaggle notebook only.
- Internet: disabled for the submitted notebook.
- Runtime: CPU or GPU runtime must be no more than 9 hours.
- Maximum team size: 8.
- Maximum submissions: 1 per day.
- Final judging selections: up to 2 final submissions.

These current limits supersede older local notes where they conflict.

### Evaluation set and leaderboard split

- The competition evaluates on **110 unseen private games**.
- Approximately half determine the public leaderboard score.
- The other half determine the private leaderboard score and final standing.
- Public-leaderboard movement is therefore iteration evidence, not proof of final generalization.

### Scoring

For a completed level, let `H` be the human first-attempt action count and `A` the agent action count:

```text
level_score = min(H / A, 1)^2
```

An uncompleted level receives no completion credit. Level scores are weighted by their 1-indexed level number within a game; the weighted level scores form the per-game score. The competition score is the average of the per-game scores across the evaluation games.

This rewards both completion and action efficiency, with later levels carrying more weight inside each game.

## Account snapshot — 7 August 2026

| Field | Point-in-time value |
|---|---:|
| Public rank | 290 |
| Public score | 1.11 |
| Submissions | 31 |

This is a dated snapshot, not a claim about the account after 7 August 2026. Before using it in a decision, refresh the live leaderboard and submissions list. The local Kaggle CLI was not authenticated during creation of this file, so the snapshot is recorded from the verified coordinator handoff rather than re-fetched here.

## Duck `ft09` level-five mechanics

### Known controls

The clean level-five board has three magenta controls at the following recorded click coordinates:

| Control label | Coordinate | Verified local effect |
|---|---:|---|
| Top | `(14,24)` | Reversible, control-specific regional change |
| Middle | `(30,24)` | Reversible, control-specific regional change |
| Bottom-right | `(46,40)` | Reversible, control-specific regional change |

The regional effects behave as deterministic XOR-like toggles on the boards tested so far. The controls are not the whole objective:

- No single-control probe completed the level.
- No tested control-only pair completed the level.
- No tested three-control order completed the level.
- Exhausting the eight nominal control states did not establish a terminal state.
- Feedback cells form an additional state channel and can change when ordinary cells are corrected; feedback is not a fixed function of the currently active controls alone under the evidence observed so far.

Do not silently reinterpret the coordinate pairs as `(row,column)` or `(x,y)`. Every executable audit must record the action API’s coordinate convention explicitly.

### Historical evidence — 31 July and 2–6 August 2026

The following claims are bounded to the saved `ft09` level-five starts and traces used in those experiments:

- Multiple two-action control sequences matched their complete-board predictions for both actions. Exact early-step matches support the regional control model, but do not identify the objective.
- The all-three control completion hypothesis was rejected as pre-registered: in `top → middle → bottom-right`, actions one and two matched, but the third click introduced an unmodelled feedback change at `(63,62)` (`12 → 11`). The guard stopped immediately; there was no level transition.
- A later conjunction plan activated all three controls and then began restoring ordinary cells to a calibrated target. The three control actions and first two normal corrections matched. The third normal correction produced an extra feedback change at `(63,61)` (`12 → 11`), causing the first complete-board mismatch. The run stopped at that point, before the conjunction could complete.
- These mismatches falsified the relevant complete-board predictions. They did not reveal the terminal state and do not justify an adaptive continuation.

### Fresh results — 7 August 2026

| Authorized order | Full-board result through three clicks | Transition or terminal result | Current status |
|---|---|---|---|
| `bottom-right → middle → top` | All three complete 64×64 predictions matched | No completion, `GAME_OVER`, run completion, or level transition | Completed exact match; stopped at three-click cap |
| `bottom-right → top → middle` | All three complete 64×64 predictions matched | No completion, `GAME_OVER`, run completion, or level transition | Completed exact match; stopped at three-click cap |
| `middle (30,24) → bottom-right (46,40) → top (14,24)` | All three complete 64×64 predictions matched; changed-cell counts were `128`, `165`, and `165` | No completion, `GAME_OVER`, run completion, or level transition | Completed exact match; stopped at three-click cap; no fourth click |

Across the three fresh orders completed on 7 August, the final observed 64×64 board was identical. This is verified evidence for **those three pre-registered orders only**. It is not a general order-independence rule, a solved end state, a decoded feedback/clue rule, or authorization for any downstream experiment, kernel, evaluation, submission, or repository action. The raw run artifacts should be ingested into the project source trail before the results are promoted beyond the coordinator’s dated handoff.

## Current unknowns

1. The true terminal state of Duck `ft09` level five.
2. The semantics of the clue tiles on level five.
3. The semantics of the feedback strip, including its relationship to local constraints and action history.
4. Whether feedback encodes satisfied constraints, action-order state, error count, staged progress, or another latent variable.
5. A valid, complete terminal plan that can be predicted before execution.
6. The repository locations and immutable hashes for all three fresh raw trace packages.

## Hypothesis discipline

Maintain each hypothesis with an ID, its exact predicted observations, its disconfirming observation, and its current status:

- **Proposed:** explains some observations but has not passed a discriminating test.
- **Supported:** passed a pre-registered discriminating test within a stated scope.
- **Rejected:** a complete pre-registered prediction mismatched.
- **Unresolved:** available evidence does not distinguish it from alternatives.

Never convert “regional effects matched” into “objective identified.” Never treat “no transition” as evidence that no longer plan could work. Never repair a live prediction after seeing the result.

## Strict experiment gate

Every live click must satisfy all of the following:

1. Start from an exact, saved initial board or fail closed.
2. State one falsifiable hypothesis and the alternatives the experiment distinguishes.
3. Pre-register the exact ordered action list and declared action budget.
4. Pre-register the **complete 64×64 board after every click**, including ordinary cells, control regions, feedback cells, and all unchanged cells.
5. Hash or otherwise freeze the package before execution.
6. Obtain specific coordinator authorization for that package and live action scope.
7. After each click, compare all 4,096 cells and inspect environment flags.
8. Stop immediately at the first of:
   - any cell mismatch;
   - `WIN`;
   - `GAME_OVER`;
   - level completion or any other level transition;
   - run completion;
   - declared action-budget exhaustion.
9. Preserve the prediction, observed board, diff, action result, and stop reason without post-hoc repair.

No blind permutations, adaptive live continuation, broad search, or “one more click” is permitted. Offline analysis may rank hypotheses, but a new live branch requires a new complete prediction and new authorization.

## Decision tree

```text
Saved exact board and evidence
└── Can one or more falsifiable hypotheses make complete next-board predictions?
    ├── No → remain offline; collect or reconcile existing evidence only.
    └── Yes
        └── Is there a smallest discriminating, budgeted experiment?
            ├── No → do not run a permutation or broad search.
            └── Yes
                └── Freeze boards, actions, hashes, stop rules, and audit fields.
                    └── Is specific coordinator authorization recorded?
                        ├── No → stop at the proposal.
                        └── Yes → execute one pre-registered click.
                            ├── Full-board mismatch → hard stop; reject/revise offline.
                            ├── WIN/GAME_OVER/transition/run complete → hard stop; audit outcome.
                            ├── Exact match and budget remains → execute next registered click.
                            └── Exact match and budget exhausted → stop; mark unresolved or supported only within scope.
```

Promotion beyond an isolated result requires a reproducible artifact, an independent audit of the trace, and an explicit integration decision. A competition submission requires separate, specific authorization.

## Research metrics

| Metric | Definition | Gate or interpretation |
|---|---|---|
| Prediction coverage | Predicted cells / 4,096 after each action | Must equal 100% before a click |
| Full-board exactness | Matching cells / 4,096 | Must equal 4,096/4,096 to continue |
| First mismatch | Earliest action and lexicographically first differing coordinate | Mandatory hard stop |
| Effect precision | Predicted changed cells that changed as predicted / predicted changed cells | Diagnostic; cannot replace exactness |
| Unexpected-change count | Changed cells absent from the prediction | Must equal 0 to continue |
| Expected-change miss count | Predicted changes not observed | Must equal 0 to continue |
| Terminal outcome | `WIN`, `GAME_OVER`, level transition, run completion, or none | Record after every action |
| Probe actions | Actions after the clean level-five start | Compare with declared budget |
| Total actions | Full run actions including the validated prefix | Needed for efficiency and reproduction |
| Hypothesis reduction | Alternatives ruled out by the observed exact trace | Report without overstating uniqueness |
| Reproducibility | Frozen package + hashes + raw trace + deterministic comparator | Required for promotion |
| External-state preservation | Kernels/submissions/commits/pushes launched by this context chat | Must remain zero absent specific authorization |

## Audit requirements

Every experiment record must include:

- Experiment ID, date/time in UTC, operator/coordinator, and authorization text or reference.
- Game ID, level, clean-start provenance, prefix version, environment/toolkit version, notebook/package version, and source commit where applicable.
- Initial 64×64 board and cryptographic hash.
- Exact actions, coordinate convention, action budget, and complete predicted board plus hash after every action.
- Hypothesis, alternatives, predicted terminal flags, and disconfirmation rule.
- Deterministic comparator version and a guarantee that it checks all 4,096 cells.
- For every action: observed board/hash, changed-cell summary, full diff, action result, level, reward/score fields, and terminal flags.
- Stop reason, first mismatch coordinate and values if any, executed versus planned action count, and confirmation that no further action ran.
- Raw event trace, notebook/kernel metadata, logs, audit visualization, and immutable source paths/hashes.
- Negative state statement: whether any full evaluation, competition submission, commit, push, or other external mutation occurred.
- Reviewer conclusion separated into verified evidence, inference, rejected claims, open questions, and next permitted action.

An HTML image or narrative audit is useful for review, but the raw numeric grid and deterministic comparator remain authoritative.

## Source trail

### Official, drift-prone external sources

- [Kaggle competition rules](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/rules) — team, submission, notebook, internet, runtime, and final-selection constraints.
- [Kaggle evaluation page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/evaluation) — scoring method.
- [Kaggle data page](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/data) — 110 unseen games and public/private split.
- [Kaggle timeline](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/overview/timeline) — entry, merger, and final deadlines.
- [Kaggle leaderboard](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/leaderboard) — refresh rank and public score before use.

### Durable project and experiment sources

- `docs/experiment_tracker.md` — experiment ledger through the locally recorded Duck series; it currently has unrelated uncommitted changes, so cite a commit/hash when using it as immutable evidence.
- `experiments/duck_harness_repro/exp_duck_033_operator_model.json` — control effects and bounded mechanics record.
- `experiments/duck_harness_repro/exp_duck_034_mechanics_memory.json` — bounded reasoning memory and feedback-model boundary.
- `experiments/duck_harness_repro/build_exp_duck_036_visual_audits.py` — pair-sequence visual-audit builder.
- `experiments/duck_harness_repro/build_exp_duck_037_visual_audit.py` — all-three visual-audit builder.
- `artifacts/kaggle/duck_ft09_all_three_objective/latest/` — saved all-three/conjunction run artifacts.
- `/Users/pawan/Documents/Voice Chats/arc_level5_labelled_audit.html` — labelled controls, normal cells, and feedback strip used in the 2–6 August review.
- `/Users/pawan/Documents/Codex/2026-08-07/realtime-voice-chat/outputs/ARC_Level_5_Sequence_Status_Audit.html` — pre-fresh-run sequence-status baseline. Its unrun/pending statements for the three fresh orders are superseded by the final dated 7 August coordinator handoff.
- Final coordinator handoff dated 7 August 2026 — source for all three fresh exact three-click results, the third order’s `128`, `165`, `165` changed-cell counts, their identical final board, the no-terminal outcome, and the dated account snapshot. Raw fresh-run trace paths remain to be ingested.
- Linear project **“ARC-AGI-3 Kaggle 2026”**, document **“ARC-AGI-3 — Durable Context Memory”** — cross-session continuity record; reconcile material updates in both directions.

## Concise daily update template

~~~markdown
## ARC-AGI-3 daily update — YYYY-MM-DD

**Scope:**
**Authority received:** none / exact coordinator authorization reference
**Competition state changed:** no / exact authorized change

### Verified today
- Rule/account snapshot refreshed from:
- New raw artifact(s) and hashes:
- Experiment result: exact match / mismatch at action N coordinate `(…)` / terminal flag / unresolved
- Actions executed versus budget:

### Hypotheses
- Supported within scope:
- Rejected by exact evidence:
- Still unresolved:

### Decision
- Stop / remain offline / prepare one guarded proposal / authorized next action
- Why this is the smallest discriminating next step:

### Open items
- Fresh-order trace-ingestion status:
- Terminal-state, clue-tile, and feedback semantics:
- Required audit/reviewer:

### Source trail
- Official page(s), local paths, hashes, Linear/coordinator reference:
~~~

## Current handoff

All three fresh authorized orders are resolved as exact three-click prediction matches with no terminal or level-transition outcome, and all ended on the same observed board. Reconcile and ingest their raw traces and immutable hashes before promoting the finding. The next research decision should remain offline and target clue-tile or feedback/local-constraint semantics. The result is not a solved state, a general order rule, or authorization for a new live permutation or any downstream action.
