"""Greedy immediate-gain baseline bot."""

from bots.base import (
    CandidateInsight,
    DecisionDetails,
    OthelloBot,
    format_move,
    move_order_key,
    resolve_player,
)
from engine import GameState, Move, flips_for_move, legal_moves


class GreedyBot(OthelloBot):
    """Choose the move that flips the most discs immediately."""

    name = "GreedyBot"

    def choose_move(self, state: GameState, color: str) -> Move:
        player = resolve_player(state, color)
        moves = legal_moves(state, player)
        if not moves:
            return None
        return max(moves, key=lambda move: len(flips_for_move(state, move, player)))

    def explain_move(self, state: GameState, color: str, move: Move) -> str:
        player = resolve_player(state, color)
        if move is None:
            return "No legal move was available, so GreedyBot passes."

        gains = {
            candidate: len(flips_for_move(state, candidate, player))
            for candidate in legal_moves(state, player)
        }
        best_gain = max(gains.values())
        tied_best = sum(1 for gain in gains.values() if gain == best_gain)
        tie_text = (
            "tied for the best short-term gain."
            if tied_best > 1
            else "the best short-term gain."
        )
        disc_word = "disc" if best_gain == 1 else "discs"
        return (
            f"Chose {format_move(move)} because it flips {best_gain} {disc_word} "
            f"immediately, {tie_text}"
        )

    def build_details(
        self,
        state: GameState,
        color: str,
        move: Move,
    ) -> DecisionDetails:
        player = resolve_player(state, color)
        gains = {
            candidate: len(flips_for_move(state, candidate, player))
            for candidate in legal_moves(state, player)
        }
        top_candidates = tuple(
            CandidateInsight(
                move=candidate,
                score_text=f"{gain} immediate flip{'s' if gain != 1 else ''}",
                rationale="maximizes short-term disc gain"
                if candidate == move
                else "strong immediate gain compared with the other legal moves",
            )
            for candidate, gain in sorted(
                gains.items(),
                key=lambda item: (-item[1], move_order_key(item[0])),
            )[:3]
        )
        return DecisionDetails(
            top_candidates=top_candidates,
            notes=(
                "Policy: choose the move with the highest immediate flip count.",
            ),
        )
