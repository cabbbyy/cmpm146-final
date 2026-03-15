"""Pure Othello rules for standard 8x8 play.

The engine uses zero-based ``(row, col)`` coordinates measured from the
top-left corner of the board. State transitions are immutable so future search
agents can safely generate successor states without mutating shared state.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

BLACK = "B"
WHITE = "W"
EMPTY = "."
BOARD_SIZE = 8

Position = Tuple[int, int]
Move = Optional[Position]
Board = Tuple[Tuple[str, ...], ...]

_DIRECTIONS = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)


@dataclass(frozen=True)
class GameState:
    """Immutable Othello game state."""

    board: Board
    current_player: str = BLACK
    consecutive_passes: int = 0


def initial_board() -> Board:
    """Return the standard 8x8 starting board."""

    rows = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    middle = BOARD_SIZE // 2
    rows[middle - 1][middle - 1] = WHITE
    rows[middle - 1][middle] = BLACK
    rows[middle][middle - 1] = BLACK
    rows[middle][middle] = WHITE
    return tuple(tuple(row) for row in rows)


def initial_state() -> GameState:
    """Return the standard starting state with black to move first."""

    return GameState(board=initial_board(), current_player=BLACK)


def opponent(player: str) -> str:
    """Return the opposing player color."""

    if player == BLACK:
        return WHITE
    if player == WHITE:
        return BLACK
    raise ValueError("Player must be 'B' or 'W'.")


def in_bounds(position: Position) -> bool:
    """Return whether a board position lies on the 8x8 board."""

    row, col = position
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def piece_at(board: Board, position: Position) -> str:
    """Return the disc at a board position."""

    row, col = position
    return board[row][col]


def flips_for_move(
    state: GameState, move: Position, player: Optional[str] = None
) -> Tuple[Position, ...]:
    """Return the discs that would flip for ``move``.

    An empty tuple means the move is illegal.
    """

    active_player = state.current_player if player is None else player
    if not in_bounds(move):
        return ()
    if piece_at(state.board, move) != EMPTY:
        return ()

    flips = []
    for direction in _DIRECTIONS:
        flips.extend(_captures_in_direction(state.board, move, active_player, direction))
    return tuple(flips)


def legal_moves(
    state: GameState, player: Optional[str] = None
) -> Tuple[Position, ...]:
    """Return all legal moves for ``player`` or the current player."""

    active_player = state.current_player if player is None else player
    moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            move = (row, col)
            if flips_for_move(state, move, active_player):
                moves.append(move)
    return tuple(moves)


def legal_actions(state: GameState) -> Tuple[Move, ...]:
    """Return legal actions for the current player.

    When no board move is legal but the game is not over, the only legal action
    is ``None``, representing a forced pass.
    """

    if is_terminal(state):
        return ()

    moves = legal_moves(state)
    if moves:
        return moves
    return (None,)


def apply_move(state: GameState, move: Move) -> GameState:
    """Return the successor state after applying ``move``."""

    if is_terminal(state):
        raise ValueError("Cannot apply a move to a terminal state.")

    active_player = state.current_player
    if move is None:
        if legal_moves(state, active_player):
            raise ValueError("Pass is only legal when no moves are available.")
        return GameState(
            board=state.board,
            current_player=opponent(active_player),
            consecutive_passes=state.consecutive_passes + 1,
        )

    flips = flips_for_move(state, move, active_player)
    if not flips:
        raise ValueError("Illegal move.")

    updated_board = _board_with_discs(
        state.board,
        ((move, active_player),) + tuple((position, active_player) for position in flips),
    )
    return GameState(
        board=updated_board,
        current_player=opponent(active_player),
        consecutive_passes=0,
    )


def is_terminal(state: GameState) -> bool:
    """Return whether the game has reached a terminal position."""

    if state.consecutive_passes >= 2:
        return True
    return not legal_moves(state, BLACK) and not legal_moves(state, WHITE)


def score(state: GameState) -> Dict[str, int]:
    """Count black and white discs on the board."""

    counts = {BLACK: 0, WHITE: 0}
    for row in state.board:
        for disc in row:
            if disc in counts:
                counts[disc] += 1
    return counts


def winner(state: GameState) -> Optional[str]:
    """Return the winner color for a terminal game, or ``None`` for a draw."""

    if not is_terminal(state):
        return None

    counts = score(state)
    if counts[BLACK] > counts[WHITE]:
        return BLACK
    if counts[WHITE] > counts[BLACK]:
        return WHITE
    return None


def successors(state: GameState) -> Tuple[Tuple[Move, GameState], ...]:
    """Return legal actions paired with successor states."""

    return tuple((move, apply_move(state, move)) for move in legal_actions(state))


def _captures_in_direction(
    board: Board, move: Position, player: str, direction: Position
) -> Tuple[Position, ...]:
    enemy = opponent(player)
    row, col = move
    row += direction[0]
    col += direction[1]

    captured = []
    while in_bounds((row, col)):
        disc = board[row][col]
        if disc == enemy:
            captured.append((row, col))
        elif disc == player:
            return tuple(captured) if captured else ()
        else:
            return ()
        row += direction[0]
        col += direction[1]
    return ()


def _board_with_discs(
    board: Board, updates: Tuple[Tuple[Position, str], ...]
) -> Board:
    rows = [list(row) for row in board]
    for position, disc in updates:
        row, col = position
        rows[row][col] = disc
    return tuple(tuple(row) for row in rows)
