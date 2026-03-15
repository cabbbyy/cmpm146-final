"""Minimal playable CLI loop for Othello Bot Arena."""

import argparse
import sys
import time
from dataclasses import dataclass
from typing import Callable, Optional, Protocol, Sequence, TextIO

from bots import (
    BOT_SPECS,
    BotDecision,
    OthelloBot,
    build_bot,
    format_move,
    render_decision_details,
    resolve_player,
)
from engine import (
    BLACK,
    BOARD_SIZE,
    SUPPORTED_BOARD_SIZES,
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
from ui.replay import ReplayRecorder, write_replay_json


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


@dataclass(frozen=True)
class PresentationOptions:
    """Controls optional presentation-oriented CLI output."""

    demo: bool = False
    demo_delay: float = 0.0
    explain_verbose: bool = False


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
                move = parse_move_text(raw_move, board_size=len(state.board))
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
    spec: str,
    input_fn=input,
    output: TextIO = sys.stdout,
    minimax_depth: int = 2,
    mcts_iterations: int = 64,
) -> PlayerController:
    """Create a human or bot controller from a short CLI name."""

    normalized = spec.strip().lower()
    if normalized == "human":
        return HumanCLIPlayer(input_fn=input_fn, output=output)
    return build_bot(
        normalized,
        minimax_depth=minimax_depth,
        mcts_iterations=mcts_iterations,
    )


def play_game(
    black: PlayerController,
    white: PlayerController,
    output: Optional[TextIO] = sys.stdout,
    initial: Optional[GameState] = None,
    presentation: Optional[PresentationOptions] = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    replay: Optional[ReplayRecorder] = None,
    board_size: int = BOARD_SIZE,
) -> GameResult:
    """Run a full game until terminal state."""

    options = PresentationOptions() if presentation is None else presentation
    state = initial_state(board_size=board_size) if initial is None else initial
    turn_count = 0
    if output is not None:
        if options.demo:
            output.write("Othello Bot Arena Demo\n")
            output.write("======================\n")
        output.write(f"Black: {black.name} | White: {white.name}\n")

    while not is_terminal(state):
        legal = legal_moves(state)
        controller = black if state.current_player == BLACK else white
        if output is not None:
            output.write("\n")
            if options.demo:
                output.write(
                    _render_demo_turn_header(state, controller.name, turn_count + 1)
                )
                output.write(render_board(state, legal, demo=True) + "\n")
                output.write("Legend: B=Black  W=White  *=legal move\n")
            else:
                output.write(render_status(state) + "\n")
                output.write(render_board(state, legal) + "\n")
            if legal:
                output.write(f"Legal moves: {legal_moves_text(legal)}\n")
            else:
                output.write("Legal moves: pass\n")
        decision = _choose_action(controller, state, output, replay)
        _validate_decision(state, decision.move)

        if output is not None:
            if options.demo:
                output.write(f"Chosen move: {format_move(decision.move)}\n")
                output.write(f"Explanation: {decision.explanation}\n")
            else:
                output.write(f"{player_name(state.current_player)} ({controller.name}): ")
                output.write(decision.explanation + "\n")
            if options.explain_verbose and decision.details is not None:
                output.write(render_decision_details(decision.details) + "\n")

        next_state = apply_move(state, decision.move)
        if replay is not None:
            replay.record_turn(
                turn_number=turn_count + 1,
                state_before_move=state,
                controller_name=controller.name,
                legal_moves_for_turn=legal,
                decision=decision,
                state_after_move=next_state,
            )
        state = next_state
        turn_count += 1
        if options.demo and options.demo_delay > 0 and not _is_human_controller(controller):
            sleep_fn(options.demo_delay)

    counts = score(state)
    winning_color = winner(state)
    if replay is not None:
        replay.finish(state, turn_count)
    if output is not None:
        output.write("\nFinal board\n")
        output.write(render_status(state) + "\n")
        output.write(render_board(state, demo=options.demo) + "\n")
        if options.demo:
            output.write(
                _render_demo_summary(state, black.name, white.name, turn_count) + "\n"
            )
        elif winning_color is None:
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
        choices=("human",) + BOT_SPECS,
        default="human",
        help="controller for the black side",
    )
    parser.add_argument(
        "--white",
        choices=("human",) + BOT_SPECS,
        default="heuristic",
        help="controller for the white side",
    )
    parser.add_argument(
        "--minimax-depth",
        type=int,
        default=2,
        help="search depth used by any minimax controller",
    )
    parser.add_argument(
        "--mcts-iterations",
        type=int,
        default=64,
        help="rollout count used by any MCTS controller",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="show presentation-friendly board output and labeled move summaries",
    )
    parser.add_argument(
        "--demo-delay",
        type=float,
        default=0.0,
        help="optional delay in seconds between bot turns when demo mode is enabled",
    )
    parser.add_argument(
        "--explain-verbose",
        action="store_true",
        help="show top candidate moves and bot-specific reasoning details when available",
    )
    parser.add_argument(
        "--replay-out",
        help="write a JSON replay log for the completed game",
    )
    parser.add_argument(
        "--board-size",
        type=int,
        choices=SUPPORTED_BOARD_SIZES,
        default=BOARD_SIZE,
        help="board size to use for the game",
    )
    args = parser.parse_args(argv)
    if args.demo_delay < 0:
        parser.error("--demo-delay must be non-negative.")

    black = build_controller(
        args.black,
        minimax_depth=args.minimax_depth,
        mcts_iterations=args.mcts_iterations,
    )
    white = build_controller(
        args.white,
        minimax_depth=args.minimax_depth,
        mcts_iterations=args.mcts_iterations,
    )
    replay = ReplayRecorder(black_controller=black.name, white_controller=white.name)
    play_game(
        black,
        white,
        presentation=PresentationOptions(
            demo=args.demo,
            demo_delay=args.demo_delay,
            explain_verbose=args.explain_verbose,
        ),
        replay=replay if args.replay_out else None,
        board_size=args.board_size,
    )
    if args.replay_out:
        write_replay_json(replay.build(), args.replay_out)
        print(f"Wrote replay JSON to {args.replay_out}")
    return 0


def _validate_decision(state: GameState, move: Move) -> None:
    legal = legal_actions(state)
    if move not in legal:
        raise ValueError(
            f"Controller chose illegal move {format_move(move)}; "
            f"legal actions were {legal}."
        )


def _is_human_controller(controller: PlayerController) -> bool:
    return isinstance(controller, HumanCLIPlayer)


def _choose_action(
    controller: PlayerController,
    state: GameState,
    output: Optional[TextIO],
    replay: Optional[ReplayRecorder],
) -> BotDecision:
    if output is None and replay is None and isinstance(controller, OthelloBot):
        return BotDecision(
            move=controller.choose_move(state, state.current_player),
            explanation="",
        )
    return controller.decide(state, state.current_player)


def _render_demo_turn_header(
    state: GameState,
    controller_name: str,
    turn_number: int,
) -> str:
    counts = score(state)
    return (
        f"=== Demo Turn {turn_number} ===\n"
        f"Current player: {player_name(state.current_player)}\n"
        f"Current controller: {controller_name}\n"
        f"Score: Black {counts[BLACK]} | White {counts[WHITE]}\n"
    )


def _render_demo_summary(
    state: GameState,
    black_name: str,
    white_name: str,
    turn_count: int,
) -> str:
    counts = score(state)
    winning_color = winner(state)
    if winning_color is None:
        result_line = "Winner: Draw"
        matchup_summary = (
            f"Matchup summary: {black_name} and {white_name} finished level after "
            f"{turn_count} turns."
        )
    elif winning_color == BLACK:
        margin = counts[BLACK] - counts[WHITE]
        result_line = f"Winner: Black ({black_name})"
        matchup_summary = (
            f"Matchup summary: {black_name} beat {white_name} by {margin} discs in "
            f"{turn_count} turns."
        )
    else:
        margin = counts[WHITE] - counts[BLACK]
        result_line = f"Winner: White ({white_name})"
        matchup_summary = (
            f"Matchup summary: {white_name} beat {black_name} by {margin} discs in "
            f"{turn_count} turns."
        )
    return (
        "=== Final Summary ===\n"
        f"Final score: Black {counts[BLACK]} | White {counts[WHITE]}\n"
        f"{result_line}\n"
        f"{matchup_summary}"
    )
