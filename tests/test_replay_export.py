import io
import tempfile
import unittest
from pathlib import Path

from bots import GreedyBot
from engine import BLACK, WHITE
from ui.game import play_game
from ui.replay import (
    ReplayRecorder,
    load_replay_json,
    main as replay_main,
    render_replay_markdown,
    write_replay_json,
)


class ReplayExportTests(unittest.TestCase):
    def test_play_game_can_record_replay_turns(self):
        recorder = ReplayRecorder(
            black_controller="GreedyBot",
            white_controller="GreedyBot",
        )

        result = play_game(
            GreedyBot(),
            GreedyBot(),
            output=io.StringIO(),
            replay=recorder,
        )
        replay = recorder.build()

        self.assertEqual(replay.turn_count, result.turns)
        self.assertGreater(len(replay.turns), 0)
        first_turn = replay.turns[0]
        self.assertEqual(first_turn.turn_number, 1)
        self.assertEqual(first_turn.player_to_move, BLACK)
        self.assertEqual(
            set(first_turn.legal_moves),
            {"d3", "c4", "f5", "e6"},
        )
        self.assertEqual(first_turn.score_after_move, {BLACK: 4, WHITE: 1})

    def test_replay_can_be_written_loaded_and_rendered_as_markdown(self):
        recorder = ReplayRecorder(
            black_controller="GreedyBot",
            white_controller="GreedyBot",
        )
        play_game(
            GreedyBot(),
            GreedyBot(),
            output=io.StringIO(),
            replay=recorder,
        )
        replay = recorder.build()

        with tempfile.TemporaryDirectory() as tmpdir:
            replay_path = Path(tmpdir) / "game.json"
            write_replay_json(replay, str(replay_path))

            payload = load_replay_json(str(replay_path))
            markdown = render_replay_markdown(payload)

        self.assertEqual(payload["turn_count"], replay.turn_count)
        self.assertIn("# Othello Bot Arena Replay", markdown)
        self.assertIn("## Turn 1", markdown)
        self.assertIn("- Chosen move:", markdown)
        self.assertIn("- Final score:", markdown)

    def test_replay_helper_cli_writes_markdown_file(self):
        recorder = ReplayRecorder(
            black_controller="GreedyBot",
            white_controller="GreedyBot",
        )
        play_game(
            GreedyBot(),
            GreedyBot(),
            output=io.StringIO(),
            replay=recorder,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            replay_path = Path(tmpdir) / "game.json"
            markdown_path = Path(tmpdir) / "game.md"
            write_replay_json(recorder.build(), str(replay_path))

            exit_code = replay_main(
                [str(replay_path), "--markdown-out", str(markdown_path)]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(markdown_path.exists())
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("GreedyBot", markdown)
            self.assertIn("## Turn 1", markdown)


if __name__ == "__main__":
    unittest.main()
