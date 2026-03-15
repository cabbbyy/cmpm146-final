"""Minimal playable CLI loop for Othello Bot Arena."""

import argparse
import sys
from dataclasses import dataclass
from typing import Optional, Protocol, Sequence, TextIO

from bots import (
    BotDecision,
    GreedyBot,
    HeuristicBot,
    RandomBot,
    format_move,
    resolve_player,
)
from engine import (
    BLACK,
    WHITE,
    GameState,
    Move,
    apply_move,
    initial_state,
    is_terminal,
    legal_actions,
    legal_moves,
    score,
    winner,
)
from ui.cli import legal_moves_text, parse_move_text, player_name, render_board, render_status


class PlayerController(Protocol):
    """Controller contract shared by humans and bots."""

    name: str

    def decide(self, state: GameState, color: Optional[str] = None) -> BotDecision:
        """Return a move and explanation for the current player."""


@dataclass(frozen=True)
class GameResult:
    """Summary of a completed game."""

    final_state: GameState
    turns: int


class HumanCLIPlayer:
    """Prompt a human for moves in board notation such as ``d3``."""

    name = "Human"

    def __init__(self, input_fn=input, output: TextIO = sys.stdout):
        self._input_fn = input_fn
        self._output = output

    def decide(self, state: GameState, color: Optional[str] = None) -> BotDecision:
        player = resolve_player(state, color)
        moves = legal_moves(state, player)
        if not moves:
            return BotDecision(
                move=None,
                explanation=f"{player_name(player)} has no legal move and must pass.",
            )

        while True:
            prompt = (
                f"{player_name(player)} move ({legal_moves_text(moves)} or pass): "
            )
            raw_move = self._input_fn(prompt)
            try:
                move = parse_move_text(raw_move)
            except ValueError as exc:
                self._write_line(f"Invalid input: {exc}")
                continue

            if move not in legal_actions(state):
                self._write_line(
                    f"Illegal move. Legal moves: {legal_moves_text(moves)}."
                )
                continue

            return BotDecision(
                move=move,
                explanation=f"Human selected {format_move(move)}.",
            )

    def _write_line(self, message: str) -> None:
        self._output.write(message + "\n")


def build_controller(
    spec: str, input_fn=input, output: TextIO = sys.stdout
) -> PlayerController:
    """Create a human or bot controller from a short CLI name."""

    normalized = spec.strip().lower()
    if normalized == "human":
        return HumanCLIPlayer(input_fn=input_fn, output=output)
    if normalized == "random":
        return RandomBot()
    if normalized == "greedy":
        return GreedyBot()
    if normalized == "heuristic":
        return HeuristicBot()
    raise ValueError(f"Unknown player type: {spec}")


def play_game(
    black: PlayerController,
    white: PlayerController,
    output: TextIO = sys.stdout,
    initial: Optional[GameState] = None,
) -> GameResult:
    """Run a full game until terminal state."""

    state = initial_state() if initial is None else initial
    turn_count = 0
    output.write(f"Black: {black.name} | White: {white.name}\n")

    while not is_terminal(state):
        legal = legal_moves(state)
        output.write("\n")
        output.write(render_status(state) + "\n")
        output.write(render_board(state, legal) + "\n")
        if legal:
            output.write(f"Legal moves: {legal_moves_text(legal)}\n")
        else:
            output.write("Legal moves: pass\n")

        controller = black if state.current_player == BLACK else white
        decision = controller.decide(state, state.current_player)
        _validate_decision(state, decision.move)

        output.write(f"{player_name(state.current_player)} ({controller.name}): ")
        output.write(decision.explanation + "\n")

        state = apply_move(state, decision.move)
        turn_count += 1

    counts = score(state)
    winning_color = winner(state)
    output.write("\nFinal board\n")
    output.write(render_status(state) + "\n")
    output.write(render_board(state) + "\n")
    if winning_color is None:
        output.write(f"Game over: draw {counts[BLACK]}-{counts[WHITE]}.\n")
    else:
        output.write(
            f"Game over: {player_name(winning_color)} wins "
            f"{counts[BLACK]}-{counts[WHITE]}.\n"
        )
    return GameResult(final_state=state, turns=turn_count)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point."""

    parser = argparse.ArgumentParser(description="Play Othello Bot Arena in the terminal.")
    parser.add_argument(
        "--black",
        choices=("human", "random", "greedy", "heuristic"),
        default="human",
        help="controller for the black side",
    )
    parser.add_argument(
        "--white",
        choices=("human", "random", "greedy", "heuristic"),
        default="heuristic",
        help="controller for the white side",
    )
    args = parser.parse_args(argv)

    black = build_controller(args.black)
    white = build_controller(args.white)
    play_game(black, white)
    return 0


def _validate_decision(state: GameState, move: Move) -> None:
    legal = legal_actions(state)
    if move not in legal:
        raise ValueError(
            f"Controller chose illegal move {format_move(move)}; "
            f"legal actions were {legal}."
        )
