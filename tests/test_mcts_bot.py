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
        self.assertIn("heuristic playouts", decision.explanation)

    def test_tuned_rollout_policy_avoids_the_known_risky_move(self):
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

        decision = MCTSBot(iterations=64, rng=random.Random(7)).decide(state)

        self.assertEqual(decision.move, (5, 5))
        self.assertIn("heuristic playouts", decision.explanation)

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

    def test_invalid_rollout_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            MCTSBot(iterations=32, rollout_depth_limit=0)
        with self.assertRaises(ValueError):
            MCTSBot(iterations=32, rollout_epsilon=-0.1)
        with self.assertRaises(ValueError):
            MCTSBot(iterations=32, rollout_epsilon=1.1)


if __name__ == "__main__":
    unittest.main()
