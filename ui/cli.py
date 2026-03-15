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


def parse_move_text(text: str, board_size: int = 8) -> Move:
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
    max_column = chr(ord("a") + board_size - 1)
    if not ("a" <= column <= max_column) or not row_text.isdigit():
        raise ValueError("Move input must look like d3 or pass.")

    row = int(row_text) - 1
    col = ord(column) - ord("a")
    if not (0 <= row < board_size):
        raise ValueError(f"Move row must be between 1 and {board_size}.")
    return (row, col)


def legal_moves_text(moves: Iterable[Position]) -> str:
    """Return a readable comma-separated move list."""

    return ", ".join(format_move(move) for move in moves)


def render_board(
    state: GameState,
    legal_moves: Iterable[Position] = (),
    demo: bool = False,
) -> str:
    """Render the board, marking legal moves with ``*``."""

    legal_move_set = set(legal_moves)
    size = len(state.board)
    columns = [chr(ord("a") + index) for index in range(size)]
    rows = [
        [
            "*"
            if disc == EMPTY and (row_index, col_index) in legal_move_set
            else disc
            for col_index, disc in enumerate(row)
        ]
        for row_index, row in enumerate(state.board)
    ]
    if demo:
        return _render_demo_board(columns, rows)
    return _render_standard_board(columns, rows)


def render_status(state: GameState) -> str:
    """Render the current player and disc counts."""

    counts = score(state)
    return (
        f"{player_name(state.current_player)} to move | "
        f"Black: {counts[BLACK]}  White: {counts[WHITE]}"
    )


def _render_standard_board(columns, rows) -> str:
    lines = ["  " + " ".join(columns)]
    for row_index, row in enumerate(rows):
        lines.append(f"{row_index + 1} " + " ".join(row))
    return "\n".join(lines)


def _render_demo_board(columns, rows) -> str:
    header = "    " + "   ".join(columns)
    border = "  +" + "---+" * len(columns)
    lines = [header, border]
    for row_index, row in enumerate(rows, start=1):
        lines.append(f"{row_index:>2}| " + " | ".join(row) + " |")
        lines.append(border)
    return "\n".join(lines)
