"""Round-robin simulation tools for Othello Bot Arena."""

import argparse
import io
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Optional, Sequence, Tuple

from bots import BOT_SPECS, build_bot
from engine import BLACK, WHITE, score, winner
from sim.export import write_matches_csv, write_standings_csv, write_tournament_json
from sim.presets import PRESET_ROSTERS, resolve_roster
from ui.game import play_game


@dataclass(frozen=True)
class BotEntry:
    """A named bot configuration used in simulations."""

    label: str
    spec: str
    minimax_depth: int = 3
    mcts_iterations: int = 200

    def create(self):
        """Build a fresh bot instance for a single game."""

        return build_bot(
            self.spec,
            minimax_depth=self.minimax_depth,
            mcts_iterations=self.mcts_iterations,
        )


@dataclass(frozen=True)
class MatchResult:
    """Summary of one completed simulated match."""

    black_label: str
    white_label: str
    black_score: int
    white_score: int
    turns: int
    winner_label: Optional[str]

    @property
    def disc_diff(self) -> int:
        return self.black_score - self.white_score


@dataclass(frozen=True)
class BotStats:
    """Aggregate tournament statistics for one bot."""

    label: str
    games: int
    wins: int
    losses: int
    draws: int
    total_disc_diff: int
    total_discs: int
    black_games: int
    white_games: int

    @property
    def average_disc_diff(self) -> float:
        return self.total_disc_diff / self.games if self.games else 0.0

    @property
    def average_score(self) -> float:
        return self.total_discs / self.games if self.games else 0.0


@dataclass(frozen=True)
class MatchupStats:
    """Aggregate results for one unordered bot pairing."""

    left_label: str
    right_label: str
    games: int
    left_wins: int
    right_wins: int
    draws: int
    total_margin_for_left: int

    @property
    def average_margin_for_left(self) -> float:
        return self.total_margin_for_left / self.games if self.games else 0.0


@dataclass(frozen=True)
class TournamentResult:
    """Full tournament output."""

    entries: Tuple[BotEntry, ...]
    matches: Tuple[MatchResult, ...]
    standings: Tuple[BotStats, ...]
    matchups: Tuple[MatchupStats, ...]
    black_wins: int
    white_wins: int
    draws: int


def run_match(black: BotEntry, white: BotEntry) -> MatchResult:
    """Run one bot-vs-bot match."""

    transcript = io.StringIO()
    game = play_game(black.create(), white.create(), output=transcript)
    counts = score(game.final_state)
    winning_color = winner(game.final_state)
    if winning_color is None:
        winner_label = None
    elif winning_color == BLACK:
        winner_label = black.label
    else:
        winner_label = white.label

    return MatchResult(
        black_label=black.label,
        white_label=white.label,
        black_score=counts[BLACK],
        white_score=counts[WHITE],
        turns=game.turns,
        winner_label=winner_label,
    )


def run_round_robin(
    entries: Sequence[BotEntry],
    games_per_pair: int = 2,
) -> TournamentResult:
    """Run a round-robin tournament across all bot entries."""

    if len(entries) < 2:
        raise ValueError("Round-robin requires at least two bot entries.")
    if games_per_pair < 1:
        raise ValueError("games_per_pair must be at least 1.")

    normalized_entries = tuple(entries)
    matches = []
    for left, right in combinations(normalized_entries, 2):
        for game_index in range(games_per_pair):
            if game_index % 2 == 0:
                black, white = left, right
            else:
                black, white = right, left
            matches.append(run_match(black, white))

    standings, black_wins, white_wins, draws = summarize_tournament(
        normalized_entries, matches
    )
    matchups = summarize_matchups(matches)
    return TournamentResult(
        entries=normalized_entries,
        matches=tuple(matches),
        standings=standings,
        matchups=matchups,
        black_wins=black_wins,
        white_wins=white_wins,
        draws=draws,
    )


def summarize_tournament(
    entries: Sequence[BotEntry],
    matches: Sequence[MatchResult],
) -> Tuple[Tuple[BotStats, ...], int, int, int]:
    """Aggregate standings and first-player results."""

    table: Dict[str, Dict[str, int]] = {
        entry.label: {
            "games": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "total_disc_diff": 0,
            "total_discs": 0,
            "black_games": 0,
            "white_games": 0,
        }
        for entry in entries
    }

    black_wins = 0
    white_wins = 0
    draws = 0
    for match in matches:
        black_row = table[match.black_label]
        white_row = table[match.white_label]

        black_row["games"] += 1
        black_row["black_games"] += 1
        black_row["total_discs"] += match.black_score
        black_row["total_disc_diff"] += match.disc_diff

        white_row["games"] += 1
        white_row["white_games"] += 1
        white_row["total_discs"] += match.white_score
        white_row["total_disc_diff"] -= match.disc_diff

        if match.winner_label is None:
            draws += 1
            black_row["draws"] += 1
            white_row["draws"] += 1
        elif match.winner_label == match.black_label:
            black_wins += 1
            black_row["wins"] += 1
            white_row["losses"] += 1
        else:
            white_wins += 1
            white_row["wins"] += 1
            black_row["losses"] += 1

    standings = tuple(
        sorted(
            (
                BotStats(label=label, **values)
                for label, values in table.items()
            ),
            key=lambda stats: (
                -stats.wins,
                -stats.total_disc_diff,
                -stats.total_discs,
                stats.label,
            ),
        )
    )
    return standings, black_wins, white_wins, draws


def render_tournament_report(result: TournamentResult) -> str:
    """Return a readable terminal report for a tournament."""

    lines = [
        "Othello Bot Arena Tournament",
        f"Bots: {', '.join(entry.label for entry in result.entries)}",
        f"Matches played: {len(result.matches)}",
        (
            "First-player results: "
            f"Black wins {result.black_wins} | "
            f"White wins {result.white_wins} | "
            f"Draws {result.draws}"
        ),
        "",
        "Standings",
        "Bot                  W  L  D  Games  AvgDiff  AvgScore",
    ]

    for stats in result.standings:
        lines.append(
            f"{stats.label:<20} "
            f"{stats.wins:>2} {stats.losses:>2} {stats.draws:>2} "
            f"{stats.games:>5} {stats.average_disc_diff:>8.2f} {stats.average_score:>8.2f}"
        )

    lines.append("")
    lines.append("Matchup Summary")
    lines.append("Pair                           Record   AvgMargin")
    for matchup in result.matchups:
        record = f"{matchup.left_wins}-{matchup.right_wins}-{matchup.draws}"
        pair_label = f"{matchup.left_label} vs {matchup.right_label}"
        margin = f"{matchup.average_margin_for_left:+.2f} for {matchup.left_label}"
        lines.append(f"{pair_label:<30} {record:>7}  {margin}")

    lines.append("")
    lines.append("Match Results")
    for match in result.matches:
        outcome = match.winner_label if match.winner_label is not None else "draw"
        lines.append(
            f"{match.black_label} (B) vs {match.white_label} (W): "
            f"{match.black_score}-{match.white_score} in {match.turns} turns -> {outcome}"
        )
    return "\n".join(lines)


def summarize_matchups(matches: Sequence[MatchResult]) -> Tuple[MatchupStats, ...]:
    """Aggregate results for each unordered bot pairing."""

    table: Dict[Tuple[str, str], Dict[str, int]] = {}
    for match in matches:
        left_label, right_label = sorted((match.black_label, match.white_label))
        key = (left_label, right_label)
        if key not in table:
            table[key] = {
                "games": 0,
                "left_wins": 0,
                "right_wins": 0,
                "draws": 0,
                "total_margin_for_left": 0,
            }

        row = table[key]
        row["games"] += 1
        if match.black_label == left_label:
            margin_for_left = match.black_score - match.white_score
        else:
            margin_for_left = match.white_score - match.black_score
        row["total_margin_for_left"] += margin_for_left

        if match.winner_label is None:
            row["draws"] += 1
        elif match.winner_label == left_label:
            row["left_wins"] += 1
        else:
            row["right_wins"] += 1

    return tuple(
        MatchupStats(
            left_label=left_label,
            right_label=right_label,
            **values,
        )
        for (left_label, right_label), values in sorted(table.items())
    )


def build_entries(
    specs: Sequence[str],
    minimax_depth: int = 3,
    mcts_iterations: int = 200,
) -> Tuple[BotEntry, ...]:
    """Create tournament entries from short bot names."""

    if len(specs) < 2:
        raise ValueError("At least two bots are required for a tournament.")

    entries = []
    seen_labels = set()
    for spec in specs:
        normalized = spec.strip().lower()
        if normalized not in BOT_SPECS:
            raise ValueError(f"Unknown bot type: {spec}")
        label = (
            f"minimax(d={minimax_depth})"
            if normalized == "minimax"
            else f"mcts(n={mcts_iterations})"
            if normalized == "mcts"
            else normalized
        )
        if label in seen_labels:
            raise ValueError(
                f"Duplicate tournament entry label is not supported: {label}"
            )
        seen_labels.add(label)
        entries.append(
            BotEntry(
                label=label,
                spec=normalized,
                minimax_depth=minimax_depth,
                mcts_iterations=mcts_iterations,
            )
        )
    return tuple(entries)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Simulation CLI entry point."""

    parser = argparse.ArgumentParser(
        description="Run bot-vs-bot tournaments for Othello Bot Arena."
    )
    parser.add_argument(
        "bots",
        nargs="*",
        help="explicit bot roster for the tournament or experiment",
    )
    parser.add_argument(
        "--preset",
        choices=tuple(sorted(PRESET_ROSTERS)),
        help="use a named bot roster preset instead of listing bots explicitly",
    )
    parser.add_argument(
        "--games-per-pair",
        type=int,
        default=2,
        help="number of games to play for each unordered bot pairing",
    )
    parser.add_argument(
        "--minimax-depth",
        type=int,
        default=3,
        help="search depth used by any minimax entry",
    )
    parser.add_argument(
        "--mcts-iterations",
        type=int,
        default=200,
        help="rollout count used by any MCTS entry",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=1,
        help="number of times to repeat the full round-robin evaluation",
    )
    parser.add_argument(
        "--json-out",
        help="write the tournament or repeated evaluation result to a JSON file",
    )
    parser.add_argument(
        "--standings-csv",
        help="write standings to a CSV file; repeated mode writes aggregate standings",
    )
    parser.add_argument(
        "--matches-csv",
        help="write per-match results to a CSV file; repeated mode writes aggregate matches",
    )
    args = parser.parse_args(argv)

    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1.")
    try:
        roster = resolve_roster(args.bots, preset=args.preset)
    except ValueError as exc:
        parser.error(str(exc))

    entries = build_entries(
        roster,
        minimax_depth=args.minimax_depth,
        mcts_iterations=args.mcts_iterations,
    )
    if args.repetitions == 1:
        result = run_round_robin(entries, games_per_pair=args.games_per_pair)
        print(render_tournament_report(result))
        if args.json_out:
            write_tournament_json(result, args.json_out)
            print(f"Wrote JSON export to {args.json_out}")
        if args.standings_csv:
            write_standings_csv(result, args.standings_csv)
            print(f"Wrote standings CSV to {args.standings_csv}")
        if args.matches_csv:
            write_matches_csv(result, args.matches_csv)
            print(f"Wrote matches CSV to {args.matches_csv}")
        return 0

    from sim.experiment import render_experiment_report, run_experiment, write_experiment_json

    result = run_experiment(
        entries,
        repetitions=args.repetitions,
        games_per_pair=args.games_per_pair,
    )
    print(render_experiment_report(result))
    if args.json_out:
        write_experiment_json(result, args.json_out)
        print(f"Wrote experiment JSON export to {args.json_out}")
    if args.standings_csv:
        write_standings_csv(result.aggregate, args.standings_csv)
        print(f"Wrote aggregate standings CSV to {args.standings_csv}")
    if args.matches_csv:
        write_matches_csv(result.aggregate, args.matches_csv)
        print(f"Wrote aggregate matches CSV to {args.matches_csv}")
    return 0
