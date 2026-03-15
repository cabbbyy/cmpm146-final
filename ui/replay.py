"""Replay recording and markdown rendering helpers for Othello Bot Arena."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

from bots import BotDecision, format_move
from engine import BLACK, WHITE, Board, GameState, Position, score, winner
from ui.cli import player_name


@dataclass(frozen=True)
class ReplayTurn:
    """Turn-level replay data captured from one completed game."""

    turn_number: int
    board: Tuple[str, ...]
    player_to_move: str
    controller_name: str
    legal_moves: Tuple[str, ...]
    chosen_move: str
    explanation: str
    score_after_move: Dict[str, int]


@dataclass(frozen=True)
class ReplayLog:
    """Replay export built from a completed game transcript."""

    board_size: int
    black_controller: str
    white_controller: str
    turn_count: int
    turns: Tuple[ReplayTurn, ...]
    final_score: Dict[str, int]
    winner: Optional[str]


class ReplayRecorder:
    """Mutable replay recorder used during a live game."""

    def __init__(self, black_controller: str, white_controller: str):
        self.black_controller = black_controller
        self.white_controller = white_controller
        self._turns = []
        self._final_state: Optional[GameState] = None
        self._turn_count = 0

    def record_turn(
        self,
        turn_number: int,
        state_before_move: GameState,
        controller_name: str,
        legal_moves_for_turn: Tuple[Position, ...],
        decision: BotDecision,
        state_after_move: GameState,
    ) -> None:
        """Store one move choice and the surrounding state."""

        self._turns.append(
            ReplayTurn(
                turn_number=turn_number,
                board=_board_rows(state_before_move.board),
                player_to_move=state_before_move.current_player,
                controller_name=controller_name,
                legal_moves=tuple(format_move(move) for move in legal_moves_for_turn),
                chosen_move=format_move(decision.move),
                explanation=decision.explanation,
                score_after_move=score(state_after_move),
            )
        )

    def finish(self, final_state: GameState, turn_count: int) -> None:
        """Mark the replay as complete and ready to build."""

        self._final_state = final_state
        self._turn_count = turn_count

    def build(self) -> ReplayLog:
        """Return the immutable replay log for the completed game."""

        if self._final_state is None:
            raise ValueError("ReplayRecorder.finish() must be called before build().")

        return ReplayLog(
            board_size=len(self._final_state.board),
            black_controller=self.black_controller,
            white_controller=self.white_controller,
            turn_count=self._turn_count,
            turns=tuple(self._turns),
            final_score=score(self._final_state),
            winner=winner(self._final_state),
        )


def replay_to_dict(log: ReplayLog) -> Dict[str, object]:
    """Convert a replay log into a JSON-serializable dictionary."""

    return {
        "board_size": log.board_size,
        "black_controller": log.black_controller,
        "white_controller": log.white_controller,
        "turn_count": log.turn_count,
        "final_score": dict(log.final_score),
        "winner": log.winner,
        "turns": [
            {
                "turn_number": turn.turn_number,
                "board": list(turn.board),
                "player_to_move": turn.player_to_move,
                "controller_name": turn.controller_name,
                "legal_moves": list(turn.legal_moves),
                "chosen_move": turn.chosen_move,
                "explanation": turn.explanation,
                "score_after_move": dict(turn.score_after_move),
            }
            for turn in log.turns
        ],
    }


def write_replay_json(log: ReplayLog, path: str) -> None:
    """Write one replay log to disk as JSON."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(replay_to_dict(log), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_replay_json(path: str) -> Dict[str, object]:
    """Load a replay export from JSON."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def render_replay_markdown(payload: Dict[str, object]) -> str:
    """Render a readable markdown summary for a replay export."""

    final_score = payload["final_score"]
    lines = [
        "# Othello Bot Arena Replay",
        "",
        f"- Black controller: {payload['black_controller']}",
        f"- White controller: {payload['white_controller']}",
        f"- Board size: {payload['board_size']}x{payload['board_size']}",
        f"- Turns: {payload['turn_count']}",
        (
            f"- Winner: {player_name(payload['winner'])}"
            if payload["winner"] in (BLACK, WHITE)
            else "- Winner: Draw"
        ),
        f"- Final score: Black {final_score[BLACK]} | White {final_score[WHITE]}",
        "",
    ]

    for turn in payload["turns"]:
        score_after_move = turn["score_after_move"]
        lines.extend(
            [
                f"## Turn {turn['turn_number']}",
                "",
                f"- Player to move: {player_name(turn['player_to_move'])}",
                f"- Controller: {turn['controller_name']}",
                "- Legal moves: "
                + (", ".join(turn["legal_moves"]) if turn["legal_moves"] else "pass"),
                f"- Chosen move: {turn['chosen_move']}",
                f"- Explanation: {turn['explanation']}",
                (
                    "- Score after move: "
                    f"Black {score_after_move[BLACK]} | White {score_after_move[WHITE]}"
                ),
                "",
                "```text",
                "\n".join(turn["board"]),
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_replay_markdown(payload: Dict[str, object], path: str) -> None:
    """Write a replay markdown summary to disk."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_replay_markdown(payload), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point for replay markdown rendering."""

    parser = argparse.ArgumentParser(
        description="Render an Othello Bot Arena replay JSON file as markdown."
    )
    parser.add_argument("input_json", help="path to a replay JSON file")
    parser.add_argument(
        "--markdown-out",
        help="optional path to write the rendered markdown summary",
    )
    args = parser.parse_args(argv)

    payload = load_replay_json(args.input_json)
    markdown = render_replay_markdown(payload)
    if args.markdown_out:
        write_replay_markdown(payload, args.markdown_out)
        print(f"Wrote replay markdown to {args.markdown_out}")
        return 0

    print(markdown, end="")
    return 0


def _board_rows(board: Board) -> Tuple[str, ...]:
    return tuple("".join(row) for row in board)


if __name__ == "__main__":
    raise SystemExit(main())
