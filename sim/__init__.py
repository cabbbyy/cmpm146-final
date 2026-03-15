"""Simulation tools for Othello Bot Arena."""

from sim.tournament import (
    BotEntry,
    BotStats,
    MatchResult,
    TournamentResult,
    build_entries,
    main,
    render_tournament_report,
    run_match,
    run_round_robin,
    summarize_tournament,
)

__all__ = [
    "BotEntry",
    "BotStats",
    "MatchResult",
    "TournamentResult",
    "build_entries",
    "main",
    "render_tournament_report",
    "run_match",
    "run_round_robin",
    "summarize_tournament",
]
