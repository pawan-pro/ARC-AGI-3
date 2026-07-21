import unittest

from reki_fallback import FallbackClickLedger, changed_cells, components


class RekiFallbackTests(unittest.TestCase):
    def test_components_exclude_background_and_count_twins(self):
        grid = (
            (0, 1, 0, 1, 0),
            (0, 1, 0, 1, 0),
            (0, 0, 0, 0, 0),
        )
        found = components(grid)
        self.assertEqual(len(found), 2)
        self.assertEqual({item["signature"] for item in found}, {(1, 2, 1, 1)})

    def test_border_changes_are_ignored(self):
        before = tuple(tuple(0 for _ in range(8)) for _ in range(8))
        mutable = [list(row) for row in before]
        mutable[0][0] = 1
        self.assertEqual(changed_cells(before, tuple(map(tuple, mutable)), border=3), 0)

    def test_dead_signature_only_guides_fallback_choice(self):
        board = (
            (0, 0, 0, 0, 0),
            (0, 1, 0, 1, 0),
            (0, 0, 0, 0, 0),
        )
        ledger = FallbackClickLedger(dead_threshold=2, border_ignore=0)
        first = ledger.choose(board, level=1)
        self.assertIsNotNone(first)
        ledger.observe(board, board, 1, 1, first["row"], first["col"], fallback=True)
        second = ledger.choose(board, level=1)
        self.assertIsNotNone(second)
        self.assertNotEqual((first["row"], first["col"]), (second["row"], second["col"]))
        ledger.observe(board, board, 1, 1, second["row"], second["col"], fallback=True)
        self.assertIsNone(ledger.choose(board, level=1))
        self.assertEqual(len(ledger.dead_signatures), 1)

    def test_effective_signature_is_never_marked_dead(self):
        board = ((0, 0, 0), (0, 2, 0), (0, 0, 0))
        changed = ((0, 0, 0), (0, 3, 0), (0, 0, 0))
        ledger = FallbackClickLedger(dead_threshold=2, border_ignore=0)
        result = ledger.observe(board, changed, 1, 1, 1, 1)
        self.assertTrue(result["effective"])
        ledger.observe(board, board, 1, 1, 1, 1)
        ledger.observe(board, board, 1, 1, 1, 1)
        self.assertFalse(ledger.dead_signatures)

    def test_level_change_resets_dead_memory(self):
        board = ((0, 0, 0), (0, 4, 0), (0, 0, 0))
        ledger = FallbackClickLedger(dead_threshold=1, border_ignore=0)
        ledger.observe(board, board, 1, 1, 1, 1)
        self.assertTrue(ledger.dead_signatures)
        ledger.ensure_level(2)
        self.assertFalse(ledger.dead_signatures)
        self.assertEqual(ledger.fallback_attempts, 0)


if __name__ == "__main__":
    unittest.main()
