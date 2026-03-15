"""Shared bot abstractions for Othello Bot Arena."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple

from engine import BLACK, WHITE, GameState, Move


@dataclass(frozen=True)
class CandidateInsight:
    """Concise information about one candidate move."""

    move: Move
    score_text: str
    rationale: str


@dataclass(frozen=True)
class DecisionDetails:
    """Optional structured explanation data for verbose presentation output."""

    top_candidates: Tuple[CandidateInsight, ...] = ()
    notes: Tuple[str, ...] = ()


@dataclass(frozen=True)
class BotDecision:
    """A bot's chosen action and any explanation shown to the player."""

    move: Move
    explanation: str
    details: Optional[DecisionDetails] = None


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
            details=self.build_details(state, player, move),
        )

    @abstractmethod
    def choose_move(self, state: GameState, color: str) -> Move:
        """Return the chosen move for ``color``."""

    @abstractmethod
    def explain_move(self, state: GameState, color: str, move: Move) -> str:
        """Explain why the bot selected ``move``."""

    def build_details(
        self,
        state: GameState,
        color: str,
        move: Move,
    ) -> Optional[DecisionDetails]:
        """Return optional verbose decision details for presentation output."""

        return None


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


def move_order_key(move: Move) -> Tuple[int, int, int]:
    """Return a stable ordering key for deterministic move comparisons."""

    if move is None:
        return (1, 999, 999)
    return (0, move[0], move[1])


def render_decision_details(details: DecisionDetails) -> str:
    """Render structured decision details for CLI presentation."""

    lines = ["Verbose analysis:"]
    if details.top_candidates:
        lines.append("Top candidates:")
        for index, candidate in enumerate(details.top_candidates, start=1):
            lines.append(
                f"  {index}. {format_move(candidate.move)} | "
                f"{candidate.score_text} | {candidate.rationale}"
            )
    for note in details.notes:
        lines.append(f"  {note}")
    return "\n".join(lines)
