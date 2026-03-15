"""Heuristic baseline bot."""

from bots.base import (
    CandidateInsight,
    DecisionDetails,
    OthelloBot,
    format_move,
    move_order_key,
    resolve_player,
)
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

    def build_details(
        self,
        state: GameState,
        color: str,
        move: Move,
    ) -> DecisionDetails:
        player = resolve_player(state, color)
        evaluations = []
        for candidate in legal_moves(state, player):
            breakdown = evaluate_state(apply_move(state, candidate), player)
            evaluations.append((candidate, breakdown))

        top_candidates = tuple(
            CandidateInsight(
                move=candidate,
                score_text=f"heuristic {breakdown.total:+d}",
                rationale=(
                    f"corners {breakdown.corner_score:+d}, "
                    f"mobility {breakdown.mobility_score:+d}, "
                    f"edges {breakdown.edge_score:+d}, "
                    f"disc balance {breakdown.disc_score:+d}, "
                    f"corner risk {breakdown.corner_risk_score:+d}"
                ),
            )
            for candidate, breakdown in sorted(
                evaluations,
                key=lambda item: (-item[1].total, move_order_key(item[0])),
            )[:3]
        )
        return DecisionDetails(
            top_candidates=top_candidates,
            notes=(
                "Weights: corners 25, corner danger -8, mobility 5, edges 2, discs 1-3 by game phase.",
            ),
        )
