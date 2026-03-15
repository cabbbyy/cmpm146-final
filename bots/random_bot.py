"""Random baseline bot."""

import random
from typing import Optional

from bots.base import OthelloBot, format_move, resolve_player
from engine import GameState, Move, legal_moves


class RandomBot(OthelloBot):
    """Choose uniformly among legal moves."""

    name = "RandomBot"

    def __init__(self, rng: Optional[random.Random] = None):
        self._rng = rng or random.Random()

    def choose_move(self, state: GameState, color: str) -> Move:
        player = resolve_player(state, color)
        moves = legal_moves(state, player)
        if not moves:
            return None
        return self._rng.choice(moves)

    def explain_move(self, state: GameState, color: str, move: Move) -> str:
        player = resolve_player(state, color)
        moves = legal_moves(state, player)
        if move is None:
            return "No legal move was available, so RandomBot passes."
        return (
            f"Chose {format_move(move)} uniformly at random from "
            f"{len(moves)} legal moves."
        )
