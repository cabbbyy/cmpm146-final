import unittest

from bots import HeuristicBot, evaluate_state
from engine import WHITE, GameState, apply_move


def make_state(rows, current_player):
    board = tuple(tuple(row) for row in rows)
    return GameState(board=board, current_player=current_player, consecutive_passes=0)


class HeuristicBotTests(unittest.TestCase):
    def test_evaluation_prefers_corner_successor(self):
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

        corner_state = apply_move(state, (0, 0))
        non_corner_state = apply_move(state, (2, 4))

        self.assertGreater(
            evaluate_state(corner_state, WHITE).total,
            evaluate_state(non_corner_state, WHITE).total,
        )

    def test_heuristic_bot_chooses_corner_and_explains_why(self):
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
        bot = HeuristicBot()

        decision = bot.decide(state)

        self.assertEqual(decision.move, (0, 0))
        self.assertIn("corners are permanent and highly valuable", decision.explanation)
        self.assertIsNotNone(decision.details)
        self.assertEqual(len(decision.details.top_candidates), 3)
        self.assertIn("heuristic", decision.details.top_candidates[0].score_text)
        self.assertIn("corners", decision.details.top_candidates[0].rationale)


if __name__ == "__main__":
    unittest.main()
