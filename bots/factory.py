"""Shared bot construction helpers."""

from bots.base import OthelloBot
from bots.greedy_bot import GreedyBot
from bots.heuristic_bot import HeuristicBot
from bots.mcts_bot import MCTSBot
from bots.minimax_bot import MinimaxBot
from bots.random_bot import RandomBot

BOT_SPECS = ("random", "greedy", "heuristic", "minimax", "mcts")


def build_bot(
    spec: str,
    minimax_depth: int = 3,
    mcts_iterations: int = 200,
) -> OthelloBot:
    """Create a bot instance from a short CLI-friendly name."""

    normalized = spec.strip().lower()
    if normalized == "random":
        return RandomBot()
    if normalized == "greedy":
        return GreedyBot()
    if normalized == "heuristic":
        return HeuristicBot()
    if normalized == "minimax":
        return MinimaxBot(depth=minimax_depth)
    if normalized == "mcts":
        return MCTSBot(iterations=mcts_iterations)
    raise ValueError(f"Unknown bot type: {spec}")
