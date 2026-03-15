import random
import unittest

from bots import MCTSBot
from engine import WHITE, GameState, initial_state, legal_moves


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
        self.assertIsNotNone(decision.details)
        self.assertEqual(len(decision.details.top_candidates), 3)
        self.assertIn("visits", decision.details.top_candidates[0].score_text)
        self.assertTrue(any("Iterations: 64" in note for note in decision.details.notes))

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
        self.assertIsNotNone(decision.details)

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
        self.assertIsNotNone(decision.details)

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

    def test_mcts_supports_six_by_six_opening_states(self):
        state = initial_state(board_size=6)

        decision = MCTSBot(iterations=16, rng=random.Random(5)).decide(state)

        self.assertIn(decision.move, legal_moves(state))
        self.assertIsNotNone(decision.details)


if __name__ == "__main__":
    unittest.main()
