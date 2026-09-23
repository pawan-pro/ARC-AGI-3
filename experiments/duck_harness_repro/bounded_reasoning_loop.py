"""Bounded observe-hypothesize-probe loop for deterministic ARC mechanics.

This module does not call an LLM. It turns prior transition evidence into a
small rule memory, retrieves only narrowly applicable rules, predicts each
probe's complete board effect, and stops as soon as evidence disagrees.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import asdict, dataclass, field, replace
import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence


Board = Sequence[Sequence[int]]
Point = tuple[int, int]


def freeze_board(board: Board) -> tuple[tuple[int, ...], ...]:
    if not board or not board[0]:
        raise ValueError("Board must be non-empty.")
    width = len(board[0])
    frozen = tuple(tuple(int(value) for value in row) for row in board)
    if any(len(row) != width for row in frozen):
        raise ValueError("Board rows must have equal width.")
    return frozen


def board_sha256(board: Board) -> str:
    payload = json.dumps(freeze_board(board), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def patch_values(board: Board, center: Point, radius: int) -> tuple[int, ...]:
    frozen = freeze_board(board)
    row, col = center
    values: list[int] = []
    for current_row in range(row - radius, row + radius + 1):
        for current_col in range(col - radius, col + radius + 1):
            if 0 <= current_row < len(frozen) and 0 <= current_col < len(frozen[0]):
                values.append(frozen[current_row][current_col])
            else:
                values.append(-1)
    return tuple(values)


@dataclass(frozen=True)
class RegionCandidate:
    center: Point
    color: int
    area: int
    bbox: tuple[int, int, int, int]
    patch_radius: int
    patch: tuple[int, ...]

    def compact_dict(self) -> dict[str, object]:
        return {
            "center": list(self.center),
            "color": self.color,
            "area": self.area,
            "bbox": list(self.bbox),
            "patch_radius": self.patch_radius,
            "patch_sha256": hashlib.sha256(bytes(value + 1 for value in self.patch)).hexdigest(),
        }


@dataclass(frozen=True)
class BoardObservation:
    shape: tuple[int, int]
    sha256: str
    palette_counts: tuple[tuple[int, int], ...]
    candidate_regions: tuple[RegionCandidate, ...]

    def compact_dict(self) -> dict[str, object]:
        return {
            "shape": list(self.shape),
            "sha256": self.sha256,
            "palette_counts": [list(item) for item in self.palette_counts],
            "candidate_regions": [
                candidate.compact_dict() for candidate in self.candidate_regions
            ],
        }


def _components(board: Board, color: int) -> list[list[Point]]:
    frozen = freeze_board(board)
    remaining = {
        (row, col)
        for row, values in enumerate(frozen)
        for col, value in enumerate(values)
        if value == color
    }
    components: list[list[Point]] = []
    while remaining:
        seed = remaining.pop()
        queue = deque([seed])
        component = [seed]
        while queue:
            row, col = queue.popleft()
            for drow, dcol in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                neighbor = (row + drow, col + dcol)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
                    component.append(neighbor)
        components.append(component)
    return components


def observe_board(
    board: Board,
    *,
    max_candidate_area: int = 24,
    patch_radius: int = 4,
) -> BoardObservation:
    """Create a compact, game-agnostic description of small visual regions."""
    frozen = freeze_board(board)
    counts = Counter(value for row in frozen for value in row)
    candidates: list[RegionCandidate] = []
    for color in sorted(counts):
        for component in _components(frozen, color):
            if not 1 <= len(component) <= max_candidate_area:
                continue
            rows = [point[0] for point in component]
            cols = [point[1] for point in component]
            center = ((min(rows) + max(rows)) // 2, (min(cols) + max(cols)) // 2)
            candidates.append(
                RegionCandidate(
                    center=center,
                    color=color,
                    area=len(component),
                    bbox=(min(rows), min(cols), max(rows), max(cols)),
                    patch_radius=patch_radius,
                    patch=patch_values(frozen, center, patch_radius),
                )
            )
    candidates.sort(key=lambda item: (item.area, item.color, item.center))
    return BoardObservation(
        shape=(len(frozen), len(frozen[0])),
        sha256=board_sha256(frozen),
        palette_counts=tuple(sorted(counts.items())),
        candidate_regions=tuple(candidates),
    )


@dataclass(frozen=True)
class RelativeTransition:
    drow: int
    dcol: int
    before: int
    after: int


@dataclass(frozen=True)
class ActionEffectRule:
    rule_id: str
    mechanic: str
    action_kind: str
    observed_center: Point
    anchor_color: int
    anchor_area: int
    anchor_patch_radius: int
    anchor_patch: tuple[int, ...]
    relative_transitions: tuple[RelativeTransition, ...]
    status: str
    evidence_experiment: str
    observations: int
    forward_verified_pixels: int
    reverse_verified_pixels: int
    game_family: str
    game_id: str
    level: int
    board_shape: tuple[int, int]
    initial_board_sha256: str
    transfer_scope: str = "exact_board"

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["observed_center"] = list(self.observed_center)
        payload["anchor_patch"] = list(self.anchor_patch)
        payload["board_shape"] = list(self.board_shape)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ActionEffectRule":
        transitions = tuple(
            RelativeTransition(**item)
            for item in payload["relative_transitions"]  # type: ignore[index]
        )
        return cls(
            rule_id=str(payload["rule_id"]),
            mechanic=str(payload["mechanic"]),
            action_kind=str(payload["action_kind"]),
            observed_center=tuple(payload["observed_center"]),  # type: ignore[arg-type]
            anchor_color=int(payload["anchor_color"]),
            anchor_area=int(payload["anchor_area"]),
            anchor_patch_radius=int(payload["anchor_patch_radius"]),
            anchor_patch=tuple(payload["anchor_patch"]),  # type: ignore[arg-type]
            relative_transitions=transitions,
            status=str(payload["status"]),
            evidence_experiment=str(payload["evidence_experiment"]),
            observations=int(payload["observations"]),
            forward_verified_pixels=int(
                payload.get("forward_verified_pixels", 0)
            ),
            reverse_verified_pixels=int(
                payload.get("reverse_verified_pixels", 0)
            ),
            game_family=str(payload["game_family"]),
            game_id=str(payload["game_id"]),
            level=int(payload["level"]),
            board_shape=tuple(payload["board_shape"]),  # type: ignore[arg-type]
            initial_board_sha256=str(payload["initial_board_sha256"]),
            transfer_scope=str(payload.get("transfer_scope", "exact_board")),
        )


@dataclass(frozen=True)
class ReasoningContext:
    game_family: str
    game_id: str
    level: int


@dataclass(frozen=True)
class RuleMatch:
    rule: ActionEffectRule
    action_center: Point
    match_mode: str

    def compact_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule.rule_id,
            "action_center": list(self.action_center),
            "match_mode": self.match_mode,
            "status": self.rule.status,
            "effect_pixels": len(self.rule.relative_transitions),
        }


@dataclass
class MechanicsMemory:
    rules: list[ActionEffectRule] = field(default_factory=list)
    schema_version: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "rules": [rule.to_dict() for rule in self.rules],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "MechanicsMemory":
        return cls(
            schema_version=int(payload.get("schema_version", 1)),
            rules=[
                ActionEffectRule.from_dict(item)
                for item in payload.get("rules", [])  # type: ignore[arg-type]
            ],
        )

    @classmethod
    def load(cls, path: Path) -> "MechanicsMemory":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")

    def promote_for_anchor_transfer(self, rule_id: str) -> "MechanicsMemory":
        """Explicitly promote a reviewed current-board rule for later levels."""
        promoted: list[ActionEffectRule] = []
        found = False
        for rule in self.rules:
            if rule.rule_id != rule_id:
                promoted.append(rule)
                continue
            found = True
            if rule.status != "validated_bidirectional_current_board":
                raise ValueError(
                    f"{rule_id} is not bidirectionally validated on its source board."
                )
            promoted.append(
                replace(
                    rule,
                    status="validated_bidirectional",
                    transfer_scope="anchor_signature",
                )
            )
        if not found:
            raise KeyError(rule_id)
        return MechanicsMemory(rules=promoted, schema_version=self.schema_version)

    def retrieve(
        self,
        context: ReasoningContext,
        board: Board,
    ) -> tuple[RuleMatch, ...]:
        """Retrieve exact rules, or promoted anchor rules for a later level."""
        observation = observe_board(board)
        exact: list[RuleMatch] = []
        transferable: list[RuleMatch] = []
        for rule in self.rules:
            if tuple(rule.board_shape) != observation.shape:
                continue
            if (
                rule.game_id == context.game_id
                and rule.level == context.level
                and rule.initial_board_sha256 == observation.sha256
            ):
                exact.append(
                    RuleMatch(
                        rule=rule,
                        action_center=rule.observed_center,
                        match_mode="exact_board",
                    )
                )
                continue
            if (
                rule.transfer_scope != "anchor_signature"
                or rule.status != "validated_bidirectional"
                or rule.game_family != context.game_family
            ):
                continue
            matches = [
                candidate
                for candidate in observation.candidate_regions
                if candidate.color == rule.anchor_color
                and candidate.area == rule.anchor_area
                and patch_values(
                    board,
                    candidate.center,
                    rule.anchor_patch_radius,
                )
                == rule.anchor_patch
            ]
            if len(matches) == 1:
                transferable.append(
                    RuleMatch(
                        rule=rule,
                        action_center=matches[0].center,
                        match_mode="anchor_signature",
                    )
                )
        return tuple(exact or transferable)


@dataclass
class HypothesisState:
    hypothesis_id: str
    description: str
    status: str = "consistent"
    verified_steps: int = 0
    rejected_step: int | None = None


def propose_hypotheses(
    matches: Sequence[RuleMatch],
) -> tuple[HypothesisState, ...]:
    if not matches:
        return ()
    pairs = {
        (transition.before, transition.after)
        for match in matches
        for transition in match.rule.relative_transitions
    }
    if len(pairs) != 1:
        return (
            HypothesisState(
                "sparse-observed-effect",
                "Repeat only the observed sparse transition; reversibility unknown.",
            ),
        )
    before, after = next(iter(pairs))
    return (
        HypothesisState(
            "monotone-set",
            f"Each operator sets affected pixels from {before} to {after}.",
        ),
        HypothesisState(
            "binary-xor",
            f"Each operator swaps affected pixels between {before} and {after}.",
        ),
    )


def gray_code_clicks(rule_ids: Sequence[str], max_actions: int) -> tuple[str, ...]:
    """Return the one-bit changes that visit every non-empty Gray-code state."""
    count = len(rule_ids)
    if count < 1:
        return ()
    required = (1 << count) - 1
    if required > max_actions:
        raise ValueError(
            f"Gray traversal needs {required} actions, budget is {max_actions}."
        )
    previous = 0
    clicks: list[str] = []
    for index in range(1, 1 << count):
        current = index ^ (index >> 1)
        changed = previous ^ current
        bit = changed.bit_length() - 1
        clicks.append(rule_ids[bit])
        previous = current
    return tuple(clicks)


def _predict(
    board: Board,
    match: RuleMatch,
    hypothesis_id: str,
) -> tuple[tuple[int, ...], ...]:
    predicted = [list(row) for row in freeze_board(board)]
    center_row, center_col = match.action_center
    for transition in match.rule.relative_transitions:
        row = center_row + transition.drow
        col = center_col + transition.dcol
        observed = predicted[row][col]
        if hypothesis_id == "binary-xor":
            if observed == transition.before:
                predicted[row][col] = transition.after
            elif observed == transition.after:
                predicted[row][col] = transition.before
            else:
                raise ValueError(
                    f"{match.rule.rule_id} expected color "
                    f"{transition.before}/{transition.after} at {(row, col)}, "
                    f"found {observed}."
                )
        elif hypothesis_id in {"monotone-set", "sparse-observed-effect"}:
            if observed == transition.before:
                predicted[row][col] = transition.after
            elif observed != transition.after:
                raise ValueError(
                    f"{match.rule.rule_id} cannot set unexpected color "
                    f"{observed} at {(row, col)}."
                )
        else:
            raise ValueError(f"Unknown hypothesis: {hypothesis_id}")
    return freeze_board(predicted)


def board_mismatches(expected: Board, observed: Board) -> list[tuple[int, int, int, int]]:
    left = freeze_board(expected)
    right = freeze_board(observed)
    if len(left) != len(right) or len(left[0]) != len(right[0]):
        raise ValueError("Cannot compare boards with different shapes.")
    return [
        (row, col, left[row][col], right[row][col])
        for row in range(len(left))
        for col in range(len(left[0]))
        if left[row][col] != right[row][col]
    ]


@dataclass(frozen=True)
class PlannedProbe:
    index: int
    rule_id: str
    row: int
    col: int
    predicted_board: tuple[tuple[int, ...], ...]


class BoundedReasoningController:
    """Deterministic controller with hard budgets and falsifiable predictions."""

    def __init__(
        self,
        *,
        context: ReasoningContext,
        initial_board: Board,
        matches: Sequence[RuleMatch],
        selected_hypothesis: str,
        max_actions: int,
    ) -> None:
        if max_actions < 1:
            raise ValueError("max_actions must be positive.")
        self.context = context
        self.initial_observation = observe_board(initial_board)
        self.matches = {match.rule.rule_id: match for match in matches}
        self.hypotheses = {
            item.hypothesis_id: item for item in propose_hypotheses(matches)
        }
        if selected_hypothesis not in self.hypotheses:
            raise ValueError(
                f"Selected hypothesis {selected_hypothesis!r} was not proposed."
            )
        self.selected_hypothesis = selected_hypothesis
        self.max_actions = max_actions
        self.plan = gray_code_clicks(tuple(self.matches), max_actions)
        self.records: list[dict[str, object]] = []
        self.stop_reason: str | None = None
        self._pending: tuple[PlannedProbe, tuple[tuple[int, ...], ...], dict[str, tuple[tuple[int, ...], ...]]] | None = None
        self._last_board = freeze_board(initial_board)
        self._rule_evidence: dict[str, dict[str, object]] = {}
        for match in matches:
            count = len(match.rule.relative_transitions)
            self._rule_evidence[match.rule.rule_id] = {
                "forward": set(
                    range(min(count, match.rule.forward_verified_pixels))
                ),
                "reverse": set(
                    range(min(count, match.rule.reverse_verified_pixels))
                ),
                "successful_probes": 0,
            }

    @classmethod
    def from_memory(
        cls,
        *,
        memory: MechanicsMemory,
        context: ReasoningContext,
        initial_board: Board,
        selected_hypothesis: str = "binary-xor",
        max_actions: int = 7,
    ) -> "BoundedReasoningController":
        matches = memory.retrieve(context, initial_board)
        if not matches:
            raise ValueError("No mechanics-memory rules apply to this board.")
        return cls(
            context=context,
            initial_board=initial_board,
            matches=matches,
            selected_hypothesis=selected_hypothesis,
            max_actions=max_actions,
        )

    @property
    def stopped(self) -> bool:
        return self.stop_reason is not None

    def next_action(self, current_board: Board) -> PlannedProbe | None:
        if self.stopped:
            return None
        if self._pending is not None:
            raise RuntimeError("The previous probe has not been observed.")
        current = freeze_board(current_board)
        unexpected = board_mismatches(self._last_board, current)
        if unexpected:
            self.stop_reason = "board_changed_before_probe"
            return None
        if len(self.records) >= len(self.plan):
            self.stop_reason = "state_space_exhausted"
            return None
        if len(self.records) >= self.max_actions:
            self.stop_reason = "action_budget_exhausted"
            return None
        rule_id = self.plan[len(self.records)]
        match = self.matches[rule_id]
        predictions = {
            hypothesis_id: _predict(current, match, hypothesis_id)
            for hypothesis_id, state in self.hypotheses.items()
            if state.status == "consistent"
        }
        selected = predictions[self.selected_hypothesis]
        planned = PlannedProbe(
            index=len(self.records) + 1,
            rule_id=rule_id,
            row=match.action_center[0],
            col=match.action_center[1],
            predicted_board=selected,
        )
        self._pending = (planned, current, predictions)
        return planned

    def observe(
        self,
        observed_board: Board,
        *,
        level_completed: bool = False,
        game_over: bool = False,
        run_complete: bool = False,
    ) -> bool:
        if self._pending is None:
            raise RuntimeError("No probe is awaiting observation.")
        planned, before, predictions = self._pending
        self._pending = None
        observed = freeze_board(observed_board)
        record: dict[str, object] = {
            "step": planned.index,
            "rule_id": planned.rule_id,
            "action": {"kind": "mouse", "row": planned.row, "col": planned.col},
            "before_sha256": board_sha256(before),
            "observed_sha256": board_sha256(observed),
            "level_completed": level_completed,
            "game_over": game_over,
            "run_complete": run_complete,
        }
        if level_completed:
            record["prediction_check"] = "terminal_level_transition"
            self.records.append(record)
            self._last_board = observed
            self.stop_reason = "level_completed"
            return True

        selected_mismatches = board_mismatches(
            predictions[self.selected_hypothesis], observed
        )
        record["prediction_check"] = (
            "match" if not selected_mismatches else "mismatch"
        )
        record["mismatch_count"] = len(selected_mismatches)
        record["mismatch_sample"] = [
            list(item) for item in selected_mismatches[:12]
        ]
        for hypothesis_id, prediction in predictions.items():
            state = self.hypotheses[hypothesis_id]
            mismatches = board_mismatches(prediction, observed)
            if mismatches:
                state.status = "rejected"
                state.rejected_step = planned.index
            else:
                state.verified_steps += 1
        if not selected_mismatches:
            match = self.matches[planned.rule_id]
            evidence = self._rule_evidence[planned.rule_id]
            forward = evidence["forward"]
            reverse = evidence["reverse"]
            assert isinstance(forward, set)
            assert isinstance(reverse, set)
            for index, transition in enumerate(match.rule.relative_transitions):
                row = planned.row + transition.drow
                col = planned.col + transition.dcol
                if before[row][col] == transition.before:
                    forward.add(index)
                elif before[row][col] == transition.after:
                    reverse.add(index)
            evidence["successful_probes"] = int(evidence["successful_probes"]) + 1
        self.records.append(record)
        self._last_board = observed

        if selected_mismatches:
            self.stop_reason = "prediction_mismatch"
            return False
        if game_over or run_complete:
            self.stop_reason = "game_over" if game_over else "run_complete"
            return False
        if len(self.records) >= len(self.plan):
            self.stop_reason = "state_space_exhausted"
        elif len(self.records) >= self.max_actions:
            self.stop_reason = "action_budget_exhausted"
        return True

    def trace_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "controller": "bounded_reasoning_loop",
            "runtime_llm": False,
            "context": asdict(self.context),
            "initial_observation": self.initial_observation.compact_dict(),
            "candidate_controls": [
                match.compact_dict() for match in self.matches.values()
            ],
            "hypotheses": [
                asdict(self.hypotheses[key]) for key in sorted(self.hypotheses)
            ],
            "selected_hypothesis": self.selected_hypothesis,
            "action_budget": self.max_actions,
            "planned_actions": list(self.plan),
            "executed_actions": len(self.records),
            "stop_reason": self.stop_reason,
            "records": self.records,
            "rule_evidence": self.rule_evidence_dict(),
        }

    def rule_evidence_dict(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for rule_id, evidence in self._rule_evidence.items():
            forward = evidence["forward"]
            reverse = evidence["reverse"]
            assert isinstance(forward, set)
            assert isinstance(reverse, set)
            total = len(self.matches[rule_id].rule.relative_transitions)
            rows.append(
                {
                    "rule_id": rule_id,
                    "effect_pixels": total,
                    "forward_verified_pixels": len(forward),
                    "reverse_verified_pixels": len(reverse),
                    "successful_probes": int(evidence["successful_probes"]),
                    "bidirectional_current_board": (
                        len(forward) == total and len(reverse) == total
                    ),
                }
            )
        return rows

    def memory_snapshot(self) -> MechanicsMemory:
        """Return source rules plus evidence learned during this bounded run."""
        by_id = {str(row["rule_id"]): row for row in self.rule_evidence_dict()}
        updated: list[ActionEffectRule] = []
        for match in self.matches.values():
            rule = match.rule
            evidence = by_id[rule.rule_id]
            reverse_count = int(evidence["reverse_verified_pixels"])
            status = rule.status
            if bool(evidence["bidirectional_current_board"]):
                status = "validated_bidirectional_current_board"
            elif reverse_count:
                status = "observed_mixed_direction_current_board"
            updated.append(
                replace(
                    rule,
                    status=status,
                    observations=rule.observations
                    + int(evidence["successful_probes"]),
                    forward_verified_pixels=int(
                        evidence["forward_verified_pixels"]
                    ),
                    reverse_verified_pixels=reverse_count,
                )
            )
        return MechanicsMemory(rules=updated)

    def save_trace(self, path: Path) -> None:
        path.write_text(
            json.dumps(self.trace_dict(), indent=2) + "\n",
            encoding="utf-8",
        )


def parse_changed_cells(value: str) -> tuple[tuple[int, int, int, int], ...]:
    if not value or value == "none":
        return ()
    parsed: list[tuple[int, int, int, int]] = []
    for item in value.split("|"):
        row_col, transition = item.rsplit(",", 1)
        row, col = map(int, row_col.split(","))
        before, after = map(int, transition.split(">"))
        parsed.append((row, col, before, after))
    return tuple(parsed)


def build_exp033_memory(
    validation: dict[str, object],
    untouched_board: Board,
) -> MechanicsMemory:
    """Convert validated EXP-DUCK-033 evidence into narrow reusable rules."""
    if not bool(validation.get("structural_pass")):
        raise ValueError("EXP-DUCK-033 structural validation did not pass.")
    observation = observe_board(untouched_board)
    candidates_by_center = {
        candidate.center: candidate for candidate in observation.candidate_regions
    }
    rules: list[ActionEffectRule] = []
    for arm in validation["arms"]:  # type: ignore[index]
        center = tuple(arm["observed_cell"])  # type: ignore[arg-type,index]
        candidate = candidates_by_center.get(center)
        if candidate is None:
            raise ValueError(f"No compact region found at probe center {center}.")
        changed = parse_changed_cells(str(arm["changed_cells"]))  # type: ignore[index]
        transitions = tuple(
            RelativeTransition(
                drow=row - center[0],
                dcol=col - center[1],
                before=before,
                after=after,
            )
            for row, col, before, after in changed
        )
        rules.append(
            ActionEffectRule(
                rule_id=f"ft09-level5-magenta-{arm['arm']}",  # type: ignore[index]
                mechanic="sparse-regional-color-transition",
                action_kind="mouse",
                observed_center=center,
                anchor_color=candidate.color,
                anchor_area=candidate.area,
                anchor_patch_radius=candidate.patch_radius,
                anchor_patch=candidate.patch,
                relative_transitions=transitions,
                status="observed_forward_only",
                evidence_experiment="EXP-DUCK-033",
                observations=1,
                forward_verified_pixels=len(transitions),
                reverse_verified_pixels=0,
                game_family="ft09",
                game_id="ft09-0d8bbf25",
                level=5,
                board_shape=observation.shape,
                initial_board_sha256=observation.sha256,
            )
        )
    return MechanicsMemory(rules=rules)
