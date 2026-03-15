"""Shared bot abstractions for Othello Bot Arena."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from engine import BLACK, WHITE, GameState, Move


@dataclass(frozen=True)
class BotDecision:
    """A bot's chosen action and the explanation shown to the player."""

    move: Move
    explanation: str


class OthelloBot(ABC):
    """Interface shared by all Othello bots."""

    name = "Bot"

    def decide(self, state: GameState, color: Optional[str] = None) -> BotDecision:
        """Choose a move and produce the matching explanation."""

        player = resolve_player(state, color)
        move = self.choose_move(state, player)
        return BotDecision(
            move=move,
            explanation=self.explain_move(state, player, move),
        )

    @abstractmethod
    def choose_move(self, state: GameState, color: str) -> Move:
        """Return the chosen move for ``color``."""

    @abstractmethod
    def explain_move(self, state: GameState, color: str, move: Move) -> str:
        """Explain why the bot selected ``move``."""


def resolve_player(state: GameState, color: Optional[str]) -> str:
    """Return the acting color and validate the request."""

    player = state.current_player if color is None else color
    if player not in (BLACK, WHITE):
        raise ValueError("Player must be 'B' or 'W'.")
    if player != state.current_player:
        raise ValueError("Bots may only choose moves for the current player.")
    return player


def format_move(move: Move) -> str:
    """Convert a zero-based move to simple Othello board notation."""

    if move is None:
        return "pass"

    row, col = move
    return f"{chr(ord('a') + col)}{row + 1}"
