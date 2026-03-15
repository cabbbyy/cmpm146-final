"""Simulation tools for Othello Bot Arena."""

from sim.export import (
    matches_rows,
    standings_rows,
    tournament_to_dict,
    write_matches_csv,
    write_standings_csv,
    write_tournament_json,
)
from sim.presets import PRESET_ROSTERS, resolve_roster
from sim.tournament import (
    BotEntry,
    BotStats,
    MatchResult,
    MatchupStats,
    TournamentResult,
    build_entries,
    main,
    render_tournament_report,
    run_match,
    run_round_robin,
    summarize_matchups,
    summarize_tournament,
)

__all__ = [
    "BotEntry",
    "BotStats",
    "MatchResult",
    "MatchupStats",
    "PRESET_ROSTERS",
    "TournamentResult",
    "build_entries",
    "main",
    "matches_rows",
    "render_tournament_report",
    "resolve_roster",
    "run_match",
    "run_round_robin",
    "standings_rows",
    "summarize_matchups",
    "summarize_tournament",
    "tournament_to_dict",
    "write_matches_csv",
    "write_standings_csv",
    "write_tournament_json",
]
