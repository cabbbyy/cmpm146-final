import unittest

from sim import (
    BotEntry,
    MatchResult,
    TournamentResult,
    build_entries,
    render_tournament_report,
    run_match,
    run_round_robin,
    summarize_tournament,
)


class TournamentTests(unittest.TestCase):
    def test_build_entries_formats_minimax_and_rejects_duplicates(self):
        entries = build_entries(["greedy", "minimax"], minimax_depth=2)

        self.assertEqual(entries[0].label, "greedy")
        self.assertEqual(entries[1].label, "minimax(d=2)")
        with self.assertRaises(ValueError):
            build_entries(["greedy", "greedy"])

    def test_run_match_returns_complete_scoreline(self):
        result = run_match(
            BotEntry(label="greedy", spec="greedy"),
            BotEntry(label="heuristic", spec="heuristic"),
        )

        self.assertEqual(result.black_score + result.white_score, 64)
        self.assertGreater(result.turns, 0)
        self.assertIn(result.winner_label, {"greedy", "heuristic", None})

    def test_summarize_tournament_aggregates_wins_draws_and_disc_diff(self):
        entries = (
            BotEntry(label="alpha", spec="greedy"),
            BotEntry(label="beta", spec="heuristic"),
        )
        matches = (
            MatchResult(
                black_label="alpha",
                white_label="beta",
                black_score=40,
                white_score=24,
                turns=60,
                winner_label="alpha",
            ),
            MatchResult(
                black_label="beta",
                white_label="alpha",
                black_score=32,
                white_score=32,
                turns=60,
                winner_label=None,
            ),
        )

        standings, black_wins, white_wins, draws = summarize_tournament(entries, matches)
        by_label = {stats.label: stats for stats in standings}

        self.assertEqual(black_wins, 1)
        self.assertEqual(white_wins, 0)
        self.assertEqual(draws, 1)

        alpha = by_label["alpha"]
        beta = by_label["beta"]
        self.assertEqual((alpha.games, alpha.wins, alpha.losses, alpha.draws), (2, 1, 0, 1))
        self.assertEqual((beta.games, beta.wins, beta.losses, beta.draws), (2, 0, 1, 1))
        self.assertEqual(alpha.total_disc_diff, 16)
        self.assertEqual(beta.total_disc_diff, -16)

    def test_run_round_robin_and_report_cover_all_pairings(self):
        result = run_round_robin(build_entries(["greedy", "heuristic"]), games_per_pair=2)

        self.assertEqual(len(result.matches), 2)
        self.assertEqual({result.matches[0].black_label, result.matches[0].white_label}, {"greedy", "heuristic"})
        self.assertEqual({result.matches[1].black_label, result.matches[1].white_label}, {"greedy", "heuristic"})
        self.assertNotEqual(result.matches[0].black_label, result.matches[1].black_label)

        report = render_tournament_report(result)
        self.assertIn("Othello Bot Arena Tournament", report)
        self.assertIn("Standings", report)
        self.assertIn("Matchup Summary", report)
        self.assertIn("Match Results", report)


if __name__ == "__main__":
    unittest.main()
