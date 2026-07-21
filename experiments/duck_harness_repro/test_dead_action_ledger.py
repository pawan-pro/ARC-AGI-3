import unittest

from dead_action_ledger import (
    action_signatures,
    analyze_game,
    changed_cells,
    object_signature,
)


def event(event_type, board, action_num=0, level=1, score=0, state="NOT_FINISHED"):
    return {
        "type": event_type,
        "board": board,
        "action_num": action_num,
        "level": level,
        "score": score,
        "reward": 0,
        "state": state,
        "run_status": "playing",
        "action_display": "LEFT" if event_type == "action" else "RESET",
    }


class DeadActionLedgerTests(unittest.TestCase):
    def test_changed_cells_handles_board_shape_changes(self):
        self.assertEqual(changed_cells([[1, 2]], [[1, 3], [4]]), 2)

    def test_mouse_signature_describes_selected_component(self):
        board = [[0, 0, 9], [1, 1, 9], [0, 0, 0]]
        signature = object_signature(board, 0, 2)
        self.assertEqual(signature, "color=9|pixels=2|bbox=2x1|rect=1|twins=1")
        _, structural = action_signatures(
            {"id": "ACTION6", "data": {"x": 2, "y": 0}}, board
        )
        self.assertIn(signature, structural)

    def test_exact_guard_waits_for_two_identical_no_effect_attempts(self):
        board = [[0, 1], [0, 1]]
        changed = [[1, 1], [0, 1]]
        events = [event("initial", board)]
        events.extend(event("action", board, number) for number in range(1, 4))
        events.append(event("action", changed, 4))
        history = [
            {"action": {"id": "ACTION3", "data": {}}} for _ in range(4)
        ]
        result = analyze_game(
            {"game_id": "test-game", "history": history}, events, threshold=2
        )
        self.assertEqual(result["exact_no_effect_actions"], 3)
        self.assertEqual(result["exact_guard_candidates"], 2)
        self.assertEqual(result["exact_guard_unsafe"], 1)
        self.assertEqual(result["structural_guard_candidates"], 2)
        self.assertEqual(result["structural_guard_unsafe"], 1)


if __name__ == "__main__":
    unittest.main()
