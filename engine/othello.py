"""Pure Othello rules for configurable Othello play.

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
SUPPORTED_BOARD_SIZES = (6, 8)

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

    def __post_init__(self) -> None:
        validate_board(self.board)
        if self.current_player not in (BLACK, WHITE):
            raise ValueError("Player must be 'B' or 'W'.")
        if self.consecutive_passes < 0:
            raise ValueError("consecutive_passes cannot be negative.")

    @property
    def size(self) -> int:
        """Return the side length of the square board."""

        return len(self.board)


def initial_board(board_size: int = BOARD_SIZE) -> Board:
    """Return the starting board for a supported size."""

    validate_board_size(board_size)
    rows = [[EMPTY for _ in range(board_size)] for _ in range(board_size)]
    middle = board_size // 2
    rows[middle - 1][middle - 1] = WHITE
    rows[middle - 1][middle] = BLACK
    rows[middle][middle - 1] = BLACK
    rows[middle][middle] = WHITE
    return tuple(tuple(row) for row in rows)


def initial_state(board_size: int = BOARD_SIZE) -> GameState:
    """Return the starting state for a supported board size."""

    return GameState(board=initial_board(board_size=board_size), current_player=BLACK)


def opponent(player: str) -> str:
    """Return the opposing player color."""

    if player == BLACK:
        return WHITE
    if player == WHITE:
        return BLACK
    raise ValueError("Player must be 'B' or 'W'.")


def validate_board_size(board_size: int) -> None:
    """Reject unsupported board sizes."""

    if board_size not in SUPPORTED_BOARD_SIZES:
        supported = ", ".join(str(size) for size in SUPPORTED_BOARD_SIZES)
        raise ValueError(f"Board size must be one of: {supported}.")


def validate_board(board: Board) -> None:
    """Validate that a board is square and uses a supported size."""

    board_size = len(board)
    validate_board_size(board_size)
    if any(len(row) != board_size for row in board):
        raise ValueError("Board must be square.")


def in_bounds(position: Position, board_size: int = BOARD_SIZE) -> bool:
    """Return whether a board position lies on the current board."""

    row, col = position
    return 0 <= row < board_size and 0 <= col < board_size


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
    if not in_bounds(move, state.size):
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
    for row in range(state.size):
        for col in range(state.size):
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


def corner_positions(board_size: int) -> Tuple[Position, ...]:
    """Return corner coordinates for a supported board size."""

    validate_board_size(board_size)
    last = board_size - 1
    return ((0, 0), (0, last), (last, 0), (last, last))


def corner_adjacent_positions(board_size: int) -> Dict[Position, Tuple[Position, ...]]:
    """Return squares adjacent to each corner."""

    validate_board_size(board_size)
    last = board_size - 1
    next_to_last = board_size - 2
    return {
        (0, 0): ((0, 1), (1, 0), (1, 1)),
        (0, last): ((0, next_to_last), (1, next_to_last), (1, last)),
        (last, 0): ((next_to_last, 0), (next_to_last, 1), (last, 1)),
        (last, last): (
            (next_to_last, next_to_last),
            (next_to_last, last),
            (last, next_to_last),
        ),
    }


def edge_positions(board_size: int) -> Tuple[Position, ...]:
    """Return non-corner edge coordinates for a supported board size."""

    corners = set(corner_positions(board_size))
    last = board_size - 1
    return tuple(
        (row, col)
        for row in range(board_size)
        for col in range(board_size)
        if (row in (0, last) or col in (0, last)) and (row, col) not in corners
    )


def _captures_in_direction(
    board: Board, move: Position, player: str, direction: Position
) -> Tuple[Position, ...]:
    enemy = opponent(player)
    row, col = move
    row += direction[0]
    col += direction[1]

    captured = []
    while in_bounds((row, col), len(board)):
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
