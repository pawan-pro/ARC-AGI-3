import json
import tempfile
import unittest
from pathlib import Path

from validate_exp_duck_014 import EXPECTED_TN36_ACTIONS, validate


def run(game_id, levels, score, note=""):
    return {
        "game_id": game_id,
        "levels_completed": levels,
        "final_score": score,
        "solver_note": note,
        "actions_per_level": [7],
    }


class ExpDuck014ValidationTests(unittest.TestCase):
    def benchmark_pair(self):
        ids = ["ft09-0d8bbf25", "tn36-ef4dde99"] + [f"g{i:02}" for i in range(23)]
        baseline = {"game_runs": [run(game_id, 0, 0) for game_id in ids]}
        candidate_runs = [run(game_id, 0, 0) for game_id in ids]
        by_id = {item["game_id"]: item for item in candidate_runs}
        by_id["ft09-0d8bbf25"].update(
            levels_completed=4, final_score=40, solver_note="ft09_overlap_target=x"
        )
        by_id["tn36-ef4dde99"].update(
            levels_completed=1,
            final_score=3,
            solver_note="tn36_level1_helper=success; helper_actions=7",
        )
        return baseline, {"game_runs": candidate_runs}

    def write_events(self, root: Path, *, continue_after=True):
        path = root / "artifacts"
        path.mkdir()
        events = [
            {
                "type": "action",
                "action_display": action,
                "generated_tokens": 0,
                "level_completed": index == 7,
            }
            for index, action in enumerate(EXPECTED_TN36_ACTIONS, start=1)
        ]
        if continue_after:
            events.append({"type": "action", "action_display": "MOUSE(row=1, col=1)"})
        (path / "tn36-ef4dde99_p0_events.jsonl").write_text(
            "\n".join(json.dumps(item) for item in events) + "\n"
        )

    def test_accepts_valid_candidate(self):
        baseline, candidate = self.benchmark_pair()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_events(root)
            result = validate(baseline, candidate, root)
        self.assertTrue(result["structural_pass"])
        self.assertTrue(result["recommended_submit"])

    def test_rejects_candidate_that_stops_after_prefix(self):
        baseline, candidate = self.benchmark_pair()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_events(root, continue_after=False)
            result = validate(baseline, candidate, root)
        self.assertFalse(result["checks"]["tn36_continued_after_prefix"])
        self.assertFalse(result["structural_pass"])


if __name__ == "__main__":
    unittest.main()
