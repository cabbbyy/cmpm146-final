"""Monte Carlo Tree Search bot."""

import random
from dataclasses import dataclass
from math import log, sqrt, tanh
from typing import List, Optional, Tuple

from bots.base import (
    BotDecision,
    CandidateInsight,
    DecisionDetails,
    OthelloBot,
    format_move,
    move_order_key,
    resolve_player,
)
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
_CORNER_ADJACENT = {
    (0, 1),
    (1, 0),
    (1, 1),
    (0, 6),
    (1, 6),
    (1, 7),
    (6, 0),
    (6, 1),
    (7, 1),
    (6, 6),
    (6, 7),
    (7, 6),
}


@dataclass(frozen=True)
class MCTSResult:
    """Best move summary from Monte Carlo Tree Search."""

    move: Move
    visits: int
    expected_value: float
    rollouts: int
    candidates: Tuple["MCTSCandidate", ...]


@dataclass(frozen=True)
class MCTSCandidate:
    """Root-child summary used for verbose explanation output."""

    move: Move
    visits: int
    expected_value: float


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
        rollout_depth_limit: int = 16,
        rollout_epsilon: float = 0.15,
        rng: Optional[random.Random] = None,
    ):
        if iterations < 1:
            raise ValueError("MCTS iterations must be at least 1.")
        if exploration <= 0:
            raise ValueError("MCTS exploration constant must be positive.")
        if rollout_depth_limit < 1:
            raise ValueError("MCTS rollout depth limit must be at least 1.")
        if not 0.0 <= rollout_epsilon <= 1.0:
            raise ValueError("MCTS rollout epsilon must be between 0 and 1.")
        self.iterations = iterations
        self.exploration = exploration
        self.rollout_depth_limit = rollout_depth_limit
        self.rollout_epsilon = rollout_epsilon
        self._rng = rng or random.Random()
        self.name = f"MCTSBot(n={iterations})"

    def decide(self, state: GameState, color: str = None) -> BotDecision:
        player = resolve_player(state, color)
        result = self._search(state, player)
        return BotDecision(
            move=result.move,
            explanation=self._build_explanation(state, player, result),
            details=self._build_details(state, player, result),
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
                candidates=(),
            )
        if actions == (None,):
            return MCTSResult(
                move=None,
                visits=0,
                expected_value=0.0,
                rollouts=0,
                candidates=(),
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
                node = node.add_child(
                    self._select_expansion_action(node.state, node.untried_actions)
                )

            rollout_value = self._rollout(node.state, player)
            self._backpropagate(node, rollout_value, player)

        best_child = self._best_root_child(root)
        candidates = tuple(
            MCTSCandidate(
                move=child.move,
                visits=child.visits,
                expected_value=child.average_value(),
            )
            for child in sorted(
                root.children,
                key=lambda child: (
                    -child.visits,
                    -child.average_value(),
                    move_order_key(child.move),
                ),
            )
        )
        return MCTSResult(
            move=best_child.move,
            visits=best_child.visits,
            expected_value=best_child.average_value(),
            rollouts=root.visits,
            candidates=candidates,
        )

    def _select_child(self, node: _MCTSNode) -> _MCTSNode:
        best_child = None
        best_score = None
        for child in node.children:
            score = child.uct_score(self.exploration)
            if best_child is None or score > best_score:
                best_child = child
                best_score = score
            elif score == best_score and move_order_key(child.move) < move_order_key(best_child.move):
                best_child = child
        return best_child

    def _rollout(self, state: GameState, root_player: str) -> float:
        rollout_state = state
        depth = 0
        while not is_terminal(rollout_state) and depth < self.rollout_depth_limit:
            action = self._sample_rollout_action(rollout_state)
            rollout_state = apply_move(rollout_state, action)
            depth += 1
        return self._evaluate_rollout_state(rollout_state, root_player)

    def _sample_rollout_action(self, state: GameState) -> Move:
        actions = legal_actions(state)
        if len(actions) == 1:
            return actions[0]
        corner_actions = [action for action in actions if action in _CORNERS]
        if corner_actions:
            return self._rng.choice(corner_actions)
        if self._rng.random() < self.rollout_epsilon:
            return self._rng.choice(actions)
        return self._select_expansion_action(state, actions)

    def _select_expansion_action(
        self, state: GameState, actions: List[Move]
    ) -> Move:
        best_action = None
        best_score = None
        player = state.current_player
        for action in actions:
            successor = apply_move(state, action)
            score = evaluate_state(successor, player).total + self._heuristic_move_bonus(
                action
            )
            if best_action is None or score > best_score:
                best_action = action
                best_score = score
            elif score == best_score and move_order_key(action) < move_order_key(best_action):
                best_action = action
        return best_action

    def _evaluate_rollout_state(self, state: GameState, root_player: str) -> float:
        if is_terminal(state):
            winning_color = winner(state)
            if winning_color is None:
                return 0.0
            return 1.0 if winning_color == root_player else -1.0
        heuristic_total = evaluate_state(state, root_player).total
        return tanh(heuristic_total / 32.0)

    def _backpropagate(
        self, node: _MCTSNode, rollout_value: float, root_player: str
    ) -> None:
        current = node
        while current is not None:
            current.visits += 1
            current.total_value += self._reward_for_player(
                current.player_just_moved,
                rollout_value,
                root_player,
            )
            current = current.parent

    def _reward_for_player(
        self,
        player_just_moved: Optional[str],
        rollout_value: float,
        root_player: str,
    ) -> float:
        if player_just_moved not in (BLACK, WHITE):
            return 0.0
        return rollout_value if player_just_moved == root_player else -rollout_value

    def _best_root_child(self, root: _MCTSNode) -> _MCTSNode:
        best_child = None
        for child in root.children:
            if best_child is None:
                best_child = child
                continue
            child_score = child.average_value() + self._rollout_move_bonus(child.move)
            best_score = best_child.average_value() + self._rollout_move_bonus(
                best_child.move
            )
            if child_score > best_score:
                best_child = child
                continue
            if child_score < best_score:
                continue
            if child.visits > best_child.visits:
                best_child = child
                continue
            if child.visits < best_child.visits:
                continue
            if move_order_key(child.move) < move_order_key(best_child.move):
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
            f"{result.expected_value:+.2f}. Rollouts were guided by heuristic "
            f"playouts, and {reason}."
        )

    def _build_details(
        self,
        state: GameState,
        player: str,
        result: MCTSResult,
    ) -> DecisionDetails:
        top_candidates = tuple(
            CandidateInsight(
                move=candidate.move,
                score_text=(
                    f"visits {candidate.visits}, "
                    f"value {candidate.expected_value:+.2f}"
                ),
                rationale=dominant_reason(
                    evaluate_state(apply_move(state, candidate.move), player)
                ),
            )
            for candidate in result.candidates[:3]
        )
        return DecisionDetails(
            top_candidates=top_candidates,
            notes=(
                f"Iterations: {self.iterations}",
                f"Exploration constant: {self.exploration:.2f}",
                f"Rollout depth limit: {self.rollout_depth_limit}",
                f"Rollout epsilon: {self.rollout_epsilon:.2f}",
            ),
        )

    def _heuristic_move_bonus(self, move: Move) -> int:
        if move is None:
            return 0
        if move in _CORNERS:
            return 12
        if move in _CORNER_ADJACENT:
            return -8
        row, col = move
        if row in (0, 7) or col in (0, 7):
            return 3
        return 0

    def _rollout_move_bonus(self, move: Move) -> float:
        return self._heuristic_move_bonus(move) / 100.0
