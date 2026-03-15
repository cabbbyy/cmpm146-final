import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sim import PRESET_ROSTERS, build_entries, resolve_roster, run_experiment
from sim.tournament import main as sim_main


class ExperimentModeTests(unittest.TestCase):
    def test_resolve_roster_supports_presets_and_rejects_mixed_input(self):
        self.assertEqual(resolve_roster((), preset="baseline"), PRESET_ROSTERS["baseline"])
        self.assertEqual(resolve_roster((), preset="stretch"), PRESET_ROSTERS["stretch"])
        self.assertEqual(resolve_roster(("greedy", "heuristic")), ("greedy", "heuristic"))

        with self.assertRaises(ValueError):
            resolve_roster(("greedy", "heuristic"), preset="baseline")

    def test_run_experiment_tracks_consistency_metrics(self):
        result = run_experiment(
            build_entries(["heuristic", "minimax"], minimax_depth=2),
            repetitions=2,
            games_per_pair=1,
            board_size=6,
        )

        self.assertEqual(result.board_size, 6)
        self.assertEqual(result.repetitions, 2)
        self.assertEqual(len(result.runs), 2)
        self.assertEqual(len(result.aggregate.matches), 2)

        heuristic_summary = result.summaries[0]
        self.assertEqual(heuristic_summary.label, "heuristic")
        self.assertEqual(heuristic_summary.first_place_finishes, 2)
        self.assertEqual(heuristic_summary.average_rank, 1.0)

    def test_cli_supports_preset_repeated_mode_and_exports(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            json_path = temp_path / "experiment.json"
            standings_path = temp_path / "standings.csv"
            matches_path = temp_path / "matches.csv"
            summary_path = temp_path / "summary.md"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = sim_main(
                    [
                        "--preset",
                        "search",
                        "--repetitions",
                        "2",
                        "--games-per-pair",
                        "1",
                        "--minimax-depth",
                        "2",
                        "--board-size",
                        "6",
                        "--json-out",
                        str(json_path),
                        "--standings-csv",
                        str(standings_path),
                        "--matches-csv",
                        str(matches_path),
                        "--summary-md",
                        str(summary_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["board_size"], 6)
            self.assertEqual(payload["repetitions"], 2)
            self.assertIn("aggregate", payload)
            self.assertIn("summaries", payload)

            standings_text = standings_path.read_text(encoding="utf-8")
            matches_text = matches_path.read_text(encoding="utf-8")
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("label,games,wins,losses,draws", standings_text)
            self.assertIn("black_label,white_label,black_score,white_score", matches_text)
            self.assertIn("# Othello Bot Arena Summary", summary_text)
            self.assertIn("Avg Margin", summary_text)

            output = stdout.getvalue()
            self.assertIn("Othello Bot Arena Repeated Evaluation", output)
            self.assertIn("Board size: 6x6", output)
            self.assertIn("Wrote markdown summary", output)
            self.assertIn("Wrote experiment JSON export", output)


if __name__ == "__main__":
    unittest.main()
