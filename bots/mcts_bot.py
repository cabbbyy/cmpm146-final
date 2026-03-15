"""Monte Carlo Tree Search bot."""

import random
from dataclasses import dataclass
from math import log, sqrt
from typing import List, Optional, Tuple

from bots.base import BotDecision, OthelloBot, format_move, resolve_player
from bots.heuristics import dominant_reason, evaluate_state
from engine import (
    BLACK,
    WHITE,
    GameState,
    Move,
    Position,
    apply_move,
    is_terminal,
    legal_actions,
    opponent,
    winner,
)

_CORNERS: Tuple[Position, ...] = ((0, 0), (0, 7), (7, 0), (7, 7))


@dataclass(frozen=True)
class MCTSResult:
    """Best move summary from Monte Carlo Tree Search."""

    move: Move
    visits: int
    expected_value: float
    rollouts: int


class _MCTSNode:
    """Mutable tree node used internally by MCTSBot."""

    def __init__(
        self,
        state: GameState,
        parent: Optional["_MCTSNode"] = None,
        move: Move = None,
        player_just_moved: Optional[str] = None,
    ):
        self.state = state
        self.parent = parent
        self.move = move
        self.player_just_moved = player_just_moved
        self.children: List["_MCTSNode"] = []
        self.untried_actions = list(legal_actions(state))
        self.visits = 0
        self.total_value = 0.0

    def add_child(self, action: Move) -> "_MCTSNode":
        """Expand one action from this node."""

        successor = apply_move(self.state, action)
        child = _MCTSNode(
            successor,
            parent=self,
            move=action,
            player_just_moved=self.state.current_player,
        )
        self.untried_actions.remove(action)
        self.children.append(child)
        return child

    def average_value(self) -> float:
        """Return the mean rollout value seen by this node."""

        if self.visits == 0:
            return 0.0
        return self.total_value / self.visits

    def uct_score(self, exploration: float) -> float:
        """Return the UCT score used during selection."""

        if self.visits == 0:
            return float("inf")
        parent_visits = self.parent.visits if self.parent is not None else 1
        return self.average_value() + exploration * sqrt(log(parent_visits) / self.visits)


class MCTSBot(OthelloBot):
    """Choose moves with Monte Carlo Tree Search."""

    def __init__(
        self,
        iterations: int = 200,
        exploration: float = 1.4,
        rng: Optional[random.Random] = None,
    ):
        if iterations < 1:
            raise ValueError("MCTS iterations must be at least 1.")
        if exploration <= 0:
            raise ValueError("MCTS exploration constant must be positive.")
        self.iterations = iterations
        self.exploration = exploration
        self._rng = rng or random.Random()
        self.name = f"MCTSBot(n={iterations})"

    def decide(self, state: GameState, color: str = None) -> BotDecision:
        player = resolve_player(state, color)
        result = self._search(state, player)
        return BotDecision(
            move=result.move,
            explanation=self._build_explanation(state, player, result),
        )

    def choose_move(self, state: GameState, color: str) -> Move:
        player = resolve_player(state, color)
        return self._search(state, player).move

    def explain_move(self, state: GameState, color: str, move: Move) -> str:
        player = resolve_player(state, color)
        result = self._search(state, player)
        return self._build_explanation(state, player, result)

    def _search(self, state: GameState, player: str) -> MCTSResult:
        actions = legal_actions(state)
        if not actions:
            return MCTSResult(
                move=None,
                visits=0,
                expected_value=0.0,
                rollouts=0,
            )
        if actions == (None,):
            return MCTSResult(
                move=None,
                visits=0,
                expected_value=0.0,
                rollouts=0,
            )

        root = _MCTSNode(
            state,
            parent=None,
            move=None,
            player_just_moved=opponent(player),
        )
        for _ in range(self.iterations):
            node = root

            while not node.untried_actions and node.children and not is_terminal(node.state):
                node = self._select_child(node)

            if node.untried_actions and not is_terminal(node.state):
                node = node.add_child(self._rng.choice(node.untried_actions))

            winner_color = self._rollout(node.state)
            self._backpropagate(node, winner_color)

        best_child = self._best_root_child(root)
        return MCTSResult(
            move=best_child.move,
            visits=best_child.visits,
            expected_value=best_child.average_value(),
            rollouts=root.visits,
        )

    def _select_child(self, node: _MCTSNode) -> _MCTSNode:
        best_child = None
        best_score = None
        for child in node.children:
            score = child.uct_score(self.exploration)
            if best_child is None or score > best_score:
                best_child = child
                best_score = score
            elif score == best_score and self._move_order_key(child.move) < self._move_order_key(best_child.move):
                best_child = child
        return best_child

    def _rollout(self, state: GameState) -> Optional[str]:
        rollout_state = state
        while not is_terminal(rollout_state):
            action = self._sample_rollout_action(rollout_state)
            rollout_state = apply_move(rollout_state, action)
        return winner(rollout_state)

    def _sample_rollout_action(self, state: GameState) -> Move:
        actions = legal_actions(state)
        corner_actions = [action for action in actions if action in _CORNERS]
        if corner_actions:
            return self._rng.choice(corner_actions)
        return self._rng.choice(actions)

    def _backpropagate(self, node: _MCTSNode, winner_color: Optional[str]) -> None:
        current = node
        while current is not None:
            current.visits += 1
            current.total_value += self._reward_for_player(
                current.player_just_moved,
                winner_color,
            )
            current = current.parent

    def _reward_for_player(
        self, player_just_moved: Optional[str], winner_color: Optional[str]
    ) -> float:
        if player_just_moved not in (BLACK, WHITE) or winner_color is None:
            return 0.0
        return 1.0 if winner_color == player_just_moved else -1.0

    def _best_root_child(self, root: _MCTSNode) -> _MCTSNode:
        best_child = None
        for child in root.children:
            if best_child is None:
                best_child = child
                continue
            if child.visits > best_child.visits:
                best_child = child
                continue
            if child.visits < best_child.visits:
                continue
            if child.average_value() > best_child.average_value():
                best_child = child
                continue
            if child.average_value() < best_child.average_value():
                continue
            if self._move_order_key(child.move) < self._move_order_key(best_child.move):
                best_child = child
        return best_child

    def _build_explanation(
        self, state: GameState, player: str, result: MCTSResult
    ) -> str:
        if result.move is None:
            return "No legal move was available, so MCTSBot passes."

        successor = apply_move(state, result.move)
        reason = dominant_reason(evaluate_state(successor, player))
        return (
            f"Chose {format_move(result.move)} after {result.rollouts} rollouts; "
            f"the move received {result.visits} visits with estimated value "
            f"{result.expected_value:+.2f}, and {reason}."
        )

    def _move_order_key(self, move: Move) -> Tuple[int, int, int]:
        if move is None:
            return (1, 8, 8)
        return (0, move[0], move[1])
