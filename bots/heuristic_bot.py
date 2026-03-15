"""Heuristic baseline bot."""

from bots.base import OthelloBot, format_move, resolve_player
from bots.heuristics import dominant_reason, evaluate_state
from engine import GameState, Move, apply_move, legal_moves


class HeuristicBot(OthelloBot):
    """Choose the move with the best heuristic successor evaluation."""

    name = "HeuristicBot"

    def choose_move(self, state: GameState, color: str) -> Move:
        player = resolve_player(state, color)
        moves = legal_moves(state, player)
        if not moves:
            return None

        best_move = None
        best_value = None
        for move in moves:
            successor = apply_move(state, move)
            value = evaluate_state(successor, player).total
            if best_value is None or value > best_value:
                best_move = move
                best_value = value
        return best_move

    def explain_move(self, state: GameState, color: str, move: Move) -> str:
        player = resolve_player(state, color)
        if move is None:
            return "No legal move was available, so HeuristicBot passes."

        successor = apply_move(state, move)
        breakdown = evaluate_state(successor, player)
        reason = dominant_reason(breakdown)
        return (
            f"Chose {format_move(move)} because {reason}. "
            f"Heuristic score {breakdown.total}."
        )
