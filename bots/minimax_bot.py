"""Minimax bot with alpha-beta pruning."""

from dataclasses import dataclass
from math import inf
from typing import Tuple

from bots.base import BotDecision, OthelloBot, format_move, resolve_player
from bots.heuristics import dominant_reason, evaluate_state
from engine import GameState, Move, apply_move, is_terminal, legal_actions


@dataclass(frozen=True)
class SearchResult:
    """Best move and projected line from a minimax search."""

    move: Move
    score: int
    principal_variation: Tuple[Move, ...]


class MinimaxBot(OthelloBot):
    """Search the game tree with minimax and alpha-beta pruning."""

    def __init__(self, depth: int = 3):
        if depth < 1:
            raise ValueError("Minimax search depth must be at least 1.")
        self.depth = depth
        self.name = f"MinimaxBot(d={depth})"

    def decide(self, state: GameState, color: str = None) -> BotDecision:
        player = resolve_player(state, color)
        result = self._search_root(state, player)
        return BotDecision(
            move=result.move,
            explanation=self._build_explanation(state, player, result),
        )

    def choose_move(self, state: GameState, color: str) -> Move:
        player = resolve_player(state, color)
        return self._search_root(state, player).move

    def explain_move(self, state: GameState, color: str, move: Move) -> str:
        player = resolve_player(state, color)
        result = self._search_root(state, player)
        return self._build_explanation(state, player, result)

    def _search_root(self, state: GameState, player: str) -> SearchResult:
        actions = legal_actions(state)
        if not actions:
            return SearchResult(
                move=None,
                score=evaluate_state(state, player).total,
                principal_variation=(),
            )

        best_move = None
        best_score = -inf
        best_line: Tuple[Move, ...] = ()
        alpha = -inf
        beta = inf
        for action in actions:
            successor = apply_move(state, action)
            child_score, child_line = self._search(
                successor,
                player,
                self.depth - 1,
                alpha,
                beta,
            )
            candidate_line = (action,) + child_line
            if self._is_better_root_choice(
                action, child_score, best_move, best_score
            ):
                best_move = action
                best_score = child_score
                best_line = candidate_line
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return SearchResult(
            move=best_move,
            score=int(best_score),
            principal_variation=best_line,
        )

    def _search(
        self,
        state: GameState,
        root_player: str,
        depth: int,
        alpha: float,
        beta: float,
    ) -> Tuple[int, Tuple[Move, ...]]:
        if depth == 0 or is_terminal(state):
            return evaluate_state(state, root_player).total, ()

        actions = legal_actions(state)
        if not actions:
            return evaluate_state(state, root_player).total, ()

        maximizing = state.current_player == root_player
        if maximizing:
            best_score = -inf
            best_action = None
            best_line: Tuple[Move, ...] = ()
            for action in actions:
                successor = apply_move(state, action)
                child_score, child_line = self._search(
                    successor,
                    root_player,
                    depth - 1,
                    alpha,
                    beta,
                )
                if self._is_better_root_choice(
                    action, child_score, best_action, best_score
                ):
                    best_score = child_score
                    best_action = action
                    best_line = (action,) + child_line
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break
            return int(best_score), best_line

        best_score = inf
        best_action = None
        best_line = ()
        for action in actions:
            successor = apply_move(state, action)
            child_score, child_line = self._search(
                successor,
                root_player,
                depth - 1,
                alpha,
                beta,
            )
            if self._is_better_min_choice(action, child_score, best_action, best_score):
                best_score = child_score
                best_action = action
                best_line = (action,) + child_line
            beta = min(beta, best_score)
            if alpha >= beta:
                break
        return int(best_score), best_line

    def _build_explanation(
        self, state: GameState, player: str, result: SearchResult
    ) -> str:
        if result.move is None:
            return (
                f"No legal move was available, so MinimaxBot passes at depth "
                f"{self.depth}."
            )

        successor = apply_move(state, result.move)
        reason = dominant_reason(evaluate_state(successor, player))
        line_text = ""
        if len(result.principal_variation) > 1:
            shown_line = " -> ".join(
                format_move(move) for move in result.principal_variation[:2]
            )
            line_text = f" Best line starts {shown_line}."

        return (
            f"Chose {format_move(result.move)} because it leads to the best evaluated "
            f"future position at depth {self.depth} and {reason}.{line_text} "
            f"Search score {result.score}."
        )

    def _is_better_root_choice(
        self,
        action: Move,
        score: float,
        best_action: Move,
        best_score: float,
    ) -> bool:
        if best_action is None:
            return True
        if score > best_score:
            return True
        if score < best_score:
            return False
        return self._move_order_key(action) < self._move_order_key(best_action)

    def _is_better_min_choice(
        self,
        action: Move,
        score: float,
        best_action: Move,
        best_score: float,
    ) -> bool:
        if best_action is None:
            return True
        if score < best_score:
            return True
        if score > best_score:
            return False
        return self._move_order_key(action) < self._move_order_key(best_action)

    def _move_order_key(self, move: Move) -> Tuple[int, int, int]:
        if move is None:
            return (1, 8, 8)
        return (0, move[0], move[1])
