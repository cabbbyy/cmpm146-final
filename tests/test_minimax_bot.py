import unittest

from bots import MinimaxBot
from engine import WHITE, BLACK, GameState


def make_state(rows, current_player):
    board = tuple(tuple(row) for row in rows)
    return GameState(board=board, current_player=current_player, consecutive_passes=0)


class MinimaxBotTests(unittest.TestCase):
    def test_deeper_search_changes_the_tactical_choice(self):
        state = make_state(
            [
                "........",
                ".W......",
                ".BWB....",
                "...WB...",
                "...BBB..",
                "........",
                "........",
                "........",
            ],
            current_player=WHITE,
        )

        depth_one = MinimaxBot(depth=1).decide(state)
        depth_two = MinimaxBot(depth=2).decide(state)

        self.assertEqual(depth_one.move, (3, 5))
        self.assertEqual(depth_two.move, (5, 5))
        self.assertIn("depth 2", depth_two.explanation)
        self.assertIsNotNone(depth_two.details)
        self.assertEqual(len(depth_two.details.top_candidates), 3)
        self.assertIn("search value", depth_two.details.top_candidates[0].score_text)
        self.assertTrue(
            any("Search depth: 2" in note for note in depth_two.details.notes)
        )

    def test_minimax_bot_passes_when_no_legal_move_exists(self):
        state = make_state(
            [
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBW.",
            ],
            current_player=WHITE,
        )

        decision = MinimaxBot(depth=2).decide(state)

        self.assertIsNone(decision.move)
        self.assertIn("passes", decision.explanation)
        self.assertIsNotNone(decision.details)

    def test_invalid_depth_is_rejected(self):
        with self.assertRaises(ValueError):
            MinimaxBot(depth=0)


if __name__ == "__main__":
    unittest.main()
