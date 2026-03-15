import random
import unittest

from bots import MCTSBot
from engine import WHITE, GameState


def make_state(rows, current_player):
    board = tuple(tuple(row) for row in rows)
    return GameState(board=board, current_player=current_player, consecutive_passes=0)


class MCTSBotTests(unittest.TestCase):
    def test_seeded_mcts_prefers_the_available_corner(self):
        state = make_state(
            [
                ".B......",
                ".B......",
                ".BWB....",
                "...WB...",
                "...BW...",
                "........",
                "........",
                "........",
            ],
            current_player=WHITE,
        )

        decision = MCTSBot(iterations=64, rng=random.Random(7)).decide(state)

        self.assertEqual(decision.move, (0, 0))
        self.assertIn("after 64 rollouts", decision.explanation)
        self.assertIn("corners are permanent and highly valuable", decision.explanation)

    def test_mcts_bot_passes_when_no_legal_move_exists(self):
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

        decision = MCTSBot(iterations=32, rng=random.Random(1)).decide(state)

        self.assertIsNone(decision.move)
        self.assertIn("passes", decision.explanation)

    def test_invalid_iterations_are_rejected(self):
        with self.assertRaises(ValueError):
            MCTSBot(iterations=0)


if __name__ == "__main__":
    unittest.main()
