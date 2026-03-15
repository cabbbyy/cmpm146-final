import io
import unittest

from bots import GreedyBot, MCTSBot, MinimaxBot
from engine import initial_state, is_terminal, legal_moves
from ui import parse_move_text, render_board
from ui.game import build_controller, play_game


class CliUiTests(unittest.TestCase):
    def test_parse_move_text_supports_board_notation_and_pass(self):
        self.assertEqual(parse_move_text("d3"), (2, 3))
        self.assertEqual(parse_move_text("A8"), (7, 0))
        self.assertIsNone(parse_move_text("pass"))

    def test_render_board_marks_legal_moves_with_asterisks(self):
        state = initial_state()

        rendered = render_board(state, legal_moves(state))

        self.assertIn("3 . . . * . . . .", rendered)
        self.assertIn("4 . . * W B . . .", rendered)

    def test_play_game_finishes_in_bot_vs_bot_mode(self):
        output = io.StringIO()

        result = play_game(GreedyBot(), GreedyBot(), output=output)

        self.assertTrue(is_terminal(result.final_state))
        self.assertGreater(result.turns, 0)
        transcript = output.getvalue()
        self.assertIn("Black: GreedyBot | White: GreedyBot", transcript)
        self.assertIn("Game over:", transcript)

    def test_build_controller_supports_minimax_depth(self):
        controller = build_controller("minimax", minimax_depth=2)

        self.assertIsInstance(controller, MinimaxBot)
        self.assertEqual(controller.depth, 2)

    def test_build_controller_supports_mcts_iterations(self):
        controller = build_controller("mcts", mcts_iterations=32)

        self.assertIsInstance(controller, MCTSBot)
        self.assertEqual(controller.iterations, 32)


if __name__ == "__main__":
    unittest.main()
