"""Structured export helpers for tournament results."""

import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Iterable, List

if TYPE_CHECKING:
    from sim.tournament import TournamentResult


def tournament_to_dict(result: "TournamentResult") -> Dict[str, object]:
    """Convert a tournament result into a JSON-serializable dictionary."""

    return {
        "entries": [
            {
                "label": entry.label,
                "spec": entry.spec,
                "minimax_depth": entry.minimax_depth,
            }
            for entry in result.entries
        ],
        "summary": {
            "matches_played": len(result.matches),
            "black_wins": result.black_wins,
            "white_wins": result.white_wins,
            "draws": result.draws,
        },
        "standings": list(standings_rows(result)),
        "matchups": [
            {
                "left_label": matchup.left_label,
                "right_label": matchup.right_label,
                "games": matchup.games,
                "left_wins": matchup.left_wins,
                "right_wins": matchup.right_wins,
                "draws": matchup.draws,
                "total_margin_for_left": matchup.total_margin_for_left,
                "average_margin_for_left": matchup.average_margin_for_left,
            }
            for matchup in result.matchups
        ],
        "matches": list(matches_rows(result)),
    }


def standings_rows(result: "TournamentResult") -> List[Dict[str, object]]:
    """Return standings rows suitable for CSV export."""

    return [
        {
            "label": stats.label,
            "games": stats.games,
            "wins": stats.wins,
            "losses": stats.losses,
            "draws": stats.draws,
            "black_games": stats.black_games,
            "white_games": stats.white_games,
            "total_disc_diff": stats.total_disc_diff,
            "average_disc_diff": stats.average_disc_diff,
            "total_discs": stats.total_discs,
            "average_score": stats.average_score,
        }
        for stats in result.standings
    ]


def matches_rows(result: "TournamentResult") -> List[Dict[str, object]]:
    """Return per-match rows suitable for CSV export."""

    return [
        {
            "black_label": match.black_label,
            "white_label": match.white_label,
            "black_score": match.black_score,
            "white_score": match.white_score,
            "disc_diff": match.disc_diff,
            "turns": match.turns,
            "winner_label": match.winner_label,
        }
        for match in result.matches
    ]


def write_tournament_json(result: "TournamentResult", path: str) -> None:
    """Write a full tournament export as JSON."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(tournament_to_dict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_csv(path: str, fieldnames: Iterable[str], rows: Iterable[Dict[str, object]]) -> None:
    """Write generic CSV rows to disk."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def write_standings_csv(result: "TournamentResult", path: str) -> None:
    """Write tournament standings to CSV."""

    rows = standings_rows(result)
    fieldnames = (
        "label",
        "games",
        "wins",
        "losses",
        "draws",
        "black_games",
        "white_games",
        "total_disc_diff",
        "average_disc_diff",
        "total_discs",
        "average_score",
    )
    write_csv(path, fieldnames, rows)


def write_matches_csv(result: "TournamentResult", path: str) -> None:
    """Write per-match tournament data to CSV."""

    rows = matches_rows(result)
    fieldnames = (
        "black_label",
        "white_label",
        "black_score",
        "white_score",
        "disc_diff",
        "turns",
        "winner_label",
    )
    write_csv(path, fieldnames, rows)
