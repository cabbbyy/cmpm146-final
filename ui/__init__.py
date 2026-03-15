"""UI package for Othello Bot Arena."""

from ui.cli import legal_moves_text, parse_move_text, player_name, render_board, render_status
from ui.game import GameResult, HumanCLIPlayer, build_controller, main, play_game

__all__ = [
    "GameResult",
    "HumanCLIPlayer",
    "build_controller",
    "legal_moves_text",
    "main",
    "parse_move_text",
    "play_game",
    "player_name",
    "render_board",
    "render_status",
]
