"""Repeated evaluation tools built on top of tournament simulation."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Sequence, Tuple

from sim.export import tournament_to_dict
from sim.tournament import (
    BotEntry,
    BotStats,
    TournamentResult,
    run_round_robin,
    summarize_matchups,
    summarize_tournament,
)


@dataclass(frozen=True)
class ExperimentBotSummary:
    """Aggregate and consistency metrics for one bot across repeated runs."""

    label: str
    aggregate: BotStats
    first_place_finishes: int
    average_rank: float

    @property
    def win_rate(self) -> float:
        return self.aggregate.wins / self.aggregate.games if self.aggregate.games else 0.0


@dataclass(frozen=True)
class ExperimentResult:
    """Repeated evaluation output built from multiple tournament runs."""

    entries: Tuple[BotEntry, ...]
    repetitions: int
    games_per_pair: int
    runs: Tuple[TournamentResult, ...]
    aggregate: TournamentResult
    summaries: Tuple[ExperimentBotSummary, ...]


def run_experiment(
    entries: Sequence[BotEntry],
    repetitions: int = 5,
    games_per_pair: int = 2,
) -> ExperimentResult:
    """Run the same round-robin experiment multiple times."""

    if repetitions < 1:
        raise ValueError("repetitions must be at least 1.")

    normalized_entries = tuple(entries)
    runs = tuple(
        run_round_robin(normalized_entries, games_per_pair=games_per_pair)
        for _ in range(repetitions)
    )
    aggregate = aggregate_experiment_runs(normalized_entries, runs)
    summaries = summarize_experiment_runs(runs, aggregate)
    return ExperimentResult(
        entries=normalized_entries,
        repetitions=repetitions,
        games_per_pair=games_per_pair,
        runs=runs,
        aggregate=aggregate,
        summaries=summaries,
    )


def aggregate_experiment_runs(
    entries: Sequence[BotEntry],
    runs: Sequence[TournamentResult],
) -> TournamentResult:
    """Combine repeated runs into one aggregate tournament-style result."""

    matches = tuple(match for run in runs for match in run.matches)
    standings, black_wins, white_wins, draws = summarize_tournament(entries, matches)
    matchups = summarize_matchups(matches)
    return TournamentResult(
        entries=tuple(entries),
        matches=matches,
        standings=standings,
        matchups=matchups,
        black_wins=black_wins,
        white_wins=white_wins,
        draws=draws,
    )


def summarize_experiment_runs(
    runs: Sequence[TournamentResult],
    aggregate: TournamentResult,
) -> Tuple[ExperimentBotSummary, ...]:
    """Compute consistency metrics such as first-place finishes and average rank."""

    if not runs:
        return ()

    rank_totals: Dict[str, int] = {stats.label: 0 for stats in aggregate.standings}
    first_places: Dict[str, int] = {stats.label: 0 for stats in aggregate.standings}
    for run in runs:
        for index, stats in enumerate(run.standings, start=1):
            rank_totals[stats.label] += index
            if index == 1:
                first_places[stats.label] += 1

    return tuple(
        ExperimentBotSummary(
            label=stats.label,
            aggregate=stats,
            first_place_finishes=first_places[stats.label],
            average_rank=rank_totals[stats.label] / len(runs),
        )
        for stats in aggregate.standings
    )


def render_experiment_report(result: ExperimentResult) -> str:
    """Return a readable report for repeated evaluations."""

    lines = [
        "Othello Bot Arena Repeated Evaluation",
        f"Bots: {', '.join(entry.label for entry in result.entries)}",
        f"Runs: {result.repetitions}",
        f"Games per unordered pair per run: {result.games_per_pair}",
        f"Aggregate matches: {len(result.aggregate.matches)}",
        (
            "Aggregate first-player results: "
            f"Black wins {result.aggregate.black_wins} | "
            f"White wins {result.aggregate.white_wins} | "
            f"Draws {result.aggregate.draws}"
        ),
        "",
        "Aggregate Standings",
        "Bot                  W  L  D  Games WinRate AvgDiff  1st AvgRank",
    ]

    for summary in result.summaries:
        stats = summary.aggregate
        lines.append(
            f"{summary.label:<20} "
            f"{stats.wins:>2} {stats.losses:>2} {stats.draws:>2} "
            f"{stats.games:>5} {summary.win_rate:>7.2%} "
            f"{stats.average_disc_diff:>7.2f} {summary.first_place_finishes:>4} "
            f"{summary.average_rank:>7.2f}"
        )

    lines.append("")
    lines.append("Aggregate Matchup Summary")
    lines.append("Pair                           Record   AvgMargin")
    for matchup in result.aggregate.matchups:
        record = f"{matchup.left_wins}-{matchup.right_wins}-{matchup.draws}"
        pair_label = f"{matchup.left_label} vs {matchup.right_label}"
        margin = f"{matchup.average_margin_for_left:+.2f} for {matchup.left_label}"
        lines.append(f"{pair_label:<30} {record:>7}  {margin}")
    return "\n".join(lines)


def experiment_to_dict(result: ExperimentResult) -> Dict[str, object]:
    """Convert a repeated evaluation into a JSON-serializable dictionary."""

    return {
        "repetitions": result.repetitions,
        "games_per_pair": result.games_per_pair,
        "entries": [
            {
                "label": entry.label,
                "spec": entry.spec,
                "minimax_depth": entry.minimax_depth,
                "mcts_iterations": entry.mcts_iterations,
            }
            for entry in result.entries
        ],
        "aggregate": tournament_to_dict(result.aggregate),
        "summaries": [
            {
                "label": summary.label,
                "first_place_finishes": summary.first_place_finishes,
                "average_rank": summary.average_rank,
                "win_rate": summary.win_rate,
            }
            for summary in result.summaries
        ],
    }


def write_experiment_json(result: ExperimentResult, path: str) -> None:
    """Write a repeated evaluation export as JSON."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(experiment_to_dict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
