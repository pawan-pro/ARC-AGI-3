import unittest

from batch_feedback_analysis import analyze_events


def event(kind, board, number=0, batch_index=None, batch_size=None, reward=0):
    return {
        "type": kind,
        "board": board,
        "level": 1,
        "action_num": number,
        "batch_index": batch_index,
        "batch_size": batch_size,
        "reward": reward,
        "level_completed": reward > 0,
    }


class BatchFeedbackAnalysisTests(unittest.TestCase):
    def test_counts_trailing_actions_after_no_change(self):
        a = [[0, 1]]
        b = [[1, 0]]
        events = [event("initial", a)]
        events += [
            event("action", a, 1, 1, 3),
            event("action", b, 2, 2, 3),
            event("action", a, 3, 3, 3),
        ]
        result = analyze_events(events)
        self.assertEqual(result["no_change_triggered_batches"], 1)
        self.assertEqual(result["no_change_trailing_actions"], 2)
        self.assertNotIn("no_change_unsafe_batches", result)

    def test_marks_later_progress_as_unsafe(self):
        a = [[0]]
        events = [event("initial", a)]
        events += [
            event("action", a, 1, 1, 2),
            event("action", [[1]], 2, 2, 2, reward=1),
        ]
        result = analyze_events(events)
        self.assertEqual(result["no_change_unsafe_batches"], 1)


if __name__ == "__main__":
    unittest.main()
