import json
import tempfile
import unittest
from pathlib import Path

from sim import (
    build_entries,
    run_round_robin,
    tournament_to_dict,
    write_matches_csv,
    write_standings_csv,
    write_tournament_json,
)


class SimulationExportTests(unittest.TestCase):
    def test_tournament_to_dict_includes_summary_matchups_and_matches(self):
        result = run_round_robin(
            build_entries(["greedy", "heuristic"]),
            games_per_pair=1,
            board_size=6,
        )

        payload = tournament_to_dict(result)

        self.assertEqual(payload["board_size"], 6)
        self.assertIn("summary", payload)
        self.assertIn("matchups", payload)
        self.assertIn("matches", payload)
        self.assertEqual(payload["summary"]["matches_played"], 1)
        self.assertEqual(len(payload["matchups"]), 1)
        self.assertEqual(len(payload["matches"]), 1)

    def test_export_writers_create_json_and_csv_files(self):
        result = run_round_robin(
            build_entries(["greedy", "heuristic"]),
            games_per_pair=1,
            board_size=6,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            json_path = temp_path / "result.json"
            standings_path = temp_path / "standings.csv"
            matches_path = temp_path / "matches.csv"

            write_tournament_json(result, str(json_path))
            write_standings_csv(result, str(standings_path))
            write_matches_csv(result, str(matches_path))

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["board_size"], 6)
            self.assertIn("entries", payload)
            self.assertIn("standings", payload)

            standings_text = standings_path.read_text(encoding="utf-8")
            matches_text = matches_path.read_text(encoding="utf-8")
            self.assertIn("label,games,wins,losses,draws", standings_text)
            self.assertIn("black_label,white_label,black_score,white_score", matches_text)


if __name__ == "__main__":
    unittest.main()
