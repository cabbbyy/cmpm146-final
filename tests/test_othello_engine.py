import unittest

from engine import (
    BLACK,
    WHITE,
    GameState,
    apply_move,
    initial_state,
    is_terminal,
    legal_actions,
    legal_moves,
    piece_at,
    score,
    validate_board_size,
)


def make_state(rows, current_player=BLACK, consecutive_passes=0):
    board = tuple(tuple(row) for row in rows)
    return GameState(
        board=board,
        current_player=current_player,
        consecutive_passes=consecutive_passes,
    )


class OthelloEngineTests(unittest.TestCase):
    def test_initial_legal_moves_for_black(self):
        state = initial_state()

        self.assertEqual(
            set(legal_moves(state)),
            {(2, 3), (3, 2), (4, 5), (5, 4)},
        )
        self.assertEqual(set(legal_actions(state)), {(2, 3), (3, 2), (4, 5), (5, 4)})

    def test_initial_state_supports_six_by_six_play(self):
        state = initial_state(board_size=6)

        self.assertEqual(state.size, 6)
        self.assertEqual(
            set(legal_moves(state)),
            {(1, 2), (2, 1), (3, 4), (4, 3)},
        )

    def test_apply_move_places_disc_and_flips_captured_line(self):
        state = initial_state()

        next_state = apply_move(state, (2, 3))

        self.assertEqual(piece_at(state.board, (2, 3)), ".")
        self.assertEqual(piece_at(next_state.board, (2, 3)), BLACK)
        self.assertEqual(piece_at(next_state.board, (3, 3)), BLACK)
        self.assertEqual(next_state.current_player, WHITE)
        self.assertEqual(score(next_state), {BLACK: 4, WHITE: 1})

    def test_forced_pass_when_current_player_has_no_legal_moves(self):
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

        self.assertEqual(legal_moves(state), ())
        self.assertEqual(legal_actions(state), (None,))
        self.assertFalse(is_terminal(state))

        passed_state = apply_move(state, None)

        self.assertEqual(passed_state.current_player, BLACK)
        self.assertEqual(passed_state.consecutive_passes, 1)
        self.assertEqual(legal_moves(passed_state), ((7, 7),))

    def test_terminal_state_detected_when_no_moves_remain(self):
        state = make_state(
            [
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
                "BBBBBBBB",
            ],
            current_player=BLACK,
        )

        self.assertTrue(is_terminal(state))

    def test_score_counts_black_and_white_discs(self):
        state = make_state(
            [
                "BBB.....",
                "WW......",
                "........",
                "........",
                "........",
                "........",
                "........",
                "........",
            ]
        )

        self.assertEqual(score(state), {BLACK: 3, WHITE: 2})

    def test_invalid_board_size_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_board_size(10)
        with self.assertRaises(ValueError):
            initial_state(board_size=10)


if __name__ == "__main__":
    unittest.main()
