import random
import unittest

from bots import GreedyBot, RandomBot
from engine import BLACK, WHITE, GameState, initial_state, legal_moves


def make_state(rows, current_player=BLACK, consecutive_passes=0):
    board = tuple(tuple(row) for row in rows)
    return GameState(
        board=board,
        current_player=current_player,
        consecutive_passes=consecutive_passes,
    )


class BaselineBotTests(unittest.TestCase):
    def test_random_bot_chooses_a_legal_move(self):
        state = initial_state()
        bot = RandomBot(rng=random.Random(7))

        decision = bot.decide(state)

        self.assertIn(decision.move, legal_moves(state))
        self.assertIn("uniformly at random", decision.explanation)

    def test_random_bot_passes_when_no_legal_move_exists(self):
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
        bot = RandomBot(rng=random.Random(1))

        decision = bot.decide(state)

        self.assertIsNone(decision.move)
        self.assertIn("passes", decision.explanation)

    def test_greedy_bot_prefers_highest_immediate_flip_count(self):
        state = make_state(
            [
                "........",
                "........",
                "...BW...",
                "...BW...",
                "...BW...",
                "........",
                "........",
                "........",
            ],
            current_player=BLACK,
        )
        bot = GreedyBot()

        decision = bot.decide(state)

        self.assertEqual(decision.move, (2, 5))
        self.assertIn("flips 2 discs immediately", decision.explanation)
        self.assertIsNotNone(decision.details)
        self.assertEqual(len(decision.details.top_candidates), 3)
        self.assertIn("immediate flip", decision.details.top_candidates[0].score_text)


if __name__ == "__main__":
    unittest.main()
