import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sim.analysis import analyze_export, main as analysis_main, render_analysis_report
from sim.experiment import experiment_to_dict, run_experiment
from sim.export import tournament_to_dict
from sim.tournament import build_entries, run_round_robin


class SimulationAnalysisTests(unittest.TestCase):
    def test_analyze_export_supports_tournament_payloads(self):
        payload = tournament_to_dict(
            run_round_robin(build_entries(["greedy", "heuristic"]), games_per_pair=1)
        )

        analysis = analyze_export(payload)

        self.assertEqual(analysis.export_kind, "tournament")
        self.assertEqual(analysis.matches_played, 1)
        self.assertEqual(len(analysis.rankings), 2)
        self.assertEqual(analysis.rankings[0].label, "heuristic")

    def test_analyze_export_supports_experiment_payloads(self):
        payload = experiment_to_dict(
            run_experiment(
                build_entries(["heuristic", "minimax"], minimax_depth=2),
                repetitions=2,
                games_per_pair=1,
            )
        )

        analysis = analyze_export(payload)
        report = render_analysis_report(analysis)

        self.assertEqual(analysis.export_kind, "experiment")
        self.assertEqual(analysis.rankings[0].label, "heuristic")
        self.assertIn("avg rank 1.00", report)
        self.assertIn("firsts 2", report)

    def test_analysis_cli_reads_json_and_prints_report(self):
        payload = experiment_to_dict(
            run_experiment(
                build_entries(["heuristic", "minimax"], minimax_depth=2),
                repetitions=2,
                games_per_pair=1,
            )
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "experiment.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = analysis_main([str(path)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Othello Bot Arena Export Analysis", output)
            self.assertIn("Source type: experiment", output)


if __name__ == "__main__":
    unittest.main()
