"""CLI rendering and input parsing helpers for the playable prototype."""

from typing import Iterable

from bots import format_move
from engine import BLACK, EMPTY, GameState, Move, Position, WHITE, score


def player_name(color: str) -> str:
    """Return a readable player label."""

    if color == BLACK:
        return "Black"
    if color == WHITE:
        return "White"
    raise ValueError("Player must be 'B' or 'W'.")


def parse_move_text(text: str) -> Move:
    """Parse board notation such as ``d3`` or the literal ``pass``."""

    cleaned = text.strip().lower()
    if not cleaned:
        raise ValueError("Move input cannot be empty.")
    if cleaned == "pass":
        return None
    if len(cleaned) < 2:
        raise ValueError("Move input must look like d3 or pass.")

    column = cleaned[0]
    row_text = cleaned[1:]
    if not ("a" <= column <= "h") or not row_text.isdigit():
        raise ValueError("Move input must look like d3 or pass.")

    row = int(row_text) - 1
    col = ord(column) - ord("a")
    if not (0 <= row < 8):
        raise ValueError("Move row must be between 1 and 8.")
    return (row, col)


def legal_moves_text(moves: Iterable[Position]) -> str:
    """Return a readable comma-separated move list."""

    return ", ".join(format_move(move) for move in moves)


def render_board(state: GameState, legal_moves: Iterable[Position] = ()) -> str:
    """Render the board, marking legal moves with ``*``."""

    legal_move_set = set(legal_moves)
    lines = ["  a b c d e f g h"]
    for row_index, row in enumerate(state.board):
        cells = []
        for col_index, disc in enumerate(row):
            position = (row_index, col_index)
            if disc == EMPTY and position in legal_move_set:
                cells.append("*")
            else:
                cells.append(disc)
        lines.append(f"{row_index + 1} " + " ".join(cells))
    return "\n".join(lines)


def render_status(state: GameState) -> str:
    """Render the current player and disc counts."""

    counts = score(state)
    return (
        f"{player_name(state.current_player)} to move | "
        f"Black: {counts[BLACK]}  White: {counts[WHITE]}"
    )
