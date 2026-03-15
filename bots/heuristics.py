"""Heuristic evaluation helpers shared by stronger Othello bots."""

from dataclasses import dataclass

from engine import (
    BLACK,
    WHITE,
    EMPTY,
    GameState,
    corner_adjacent_positions,
    corner_positions,
    edge_positions,
    legal_moves,
    opponent,
    score,
)

_CORNER_WEIGHT = 25
_CORNER_RISK_WEIGHT = -8
_MOBILITY_WEIGHT = 5
_EDGE_WEIGHT = 2
_EARLY_DISC_WEIGHT = 1
_LATE_DISC_WEIGHT = 3
_LATE_GAME_THRESHOLD = 48


@dataclass(frozen=True)
class HeuristicBreakdown:
    """Weighted feature contributions for a board evaluation."""

    total: int
    corner_score: int
    corner_risk_score: int
    mobility_score: int
    edge_score: int
    disc_score: int


def evaluate_state(state: GameState, color: str) -> HeuristicBreakdown:
    """Score a state from ``color``'s perspective."""

    enemy = opponent(color)
    counts = score(state)
    occupied = counts[BLACK] + counts[WHITE]
    disc_weight = (
        _LATE_DISC_WEIGHT if occupied >= _LATE_GAME_THRESHOLD else _EARLY_DISC_WEIGHT
    )
    corners = corner_positions(state.size)
    edges = edge_positions(state.size)
    corner_adjacent = corner_adjacent_positions(state.size)

    corner_score = _CORNER_WEIGHT * (
        _count_positions(state, corners, color) - _count_positions(state, corners, enemy)
    )
    corner_risk_score = _CORNER_RISK_WEIGHT * (
        _corner_risk_count(state, corner_adjacent, color)
        - _corner_risk_count(state, corner_adjacent, enemy)
    )
    mobility_score = _MOBILITY_WEIGHT * (
        len(legal_moves(state, color)) - len(legal_moves(state, enemy))
    )
    edge_score = _EDGE_WEIGHT * (
        _count_positions(state, edges, color)
        - _count_positions(state, edges, enemy)
    )
    disc_score = disc_weight * (counts[color] - counts[enemy])

    total = (
        corner_score
        + corner_risk_score
        + mobility_score
        + edge_score
        + disc_score
    )
    return HeuristicBreakdown(
        total=total,
        corner_score=corner_score,
        corner_risk_score=corner_risk_score,
        mobility_score=mobility_score,
        edge_score=edge_score,
        disc_score=disc_score,
    )


def dominant_reason(breakdown: HeuristicBreakdown) -> str:
    """Return a short human-readable reason for the evaluation."""

    features = (
        ("corners are permanent and highly valuable", breakdown.corner_score),
        ("it improves mobility and keeps more future options open", breakdown.mobility_score),
        (
            "it avoids risky squares near empty corners",
            breakdown.corner_risk_score,
        ),
        ("it strengthens edge control", breakdown.edge_score),
        ("it improves the disc balance", breakdown.disc_score),
    )

    best_reason, best_value = max(features, key=lambda item: item[1])
    if best_value > 0:
        return best_reason
    return "it gives the best overall heuristic balance available"


def _count_positions(state: GameState, positions, color: str) -> int:
    return sum(1 for row, col in positions if state.board[row][col] == color)


def _corner_risk_count(state: GameState, corner_adjacent, color: str) -> int:
    count = 0
    for corner, adjacent_positions in corner_adjacent.items():
        row, col = corner
        if state.board[row][col] != EMPTY:
            continue
        count += sum(
            1
            for adjacent_row, adjacent_col in adjacent_positions
            if state.board[adjacent_row][adjacent_col] == color
        )
    return count
