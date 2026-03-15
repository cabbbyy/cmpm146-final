"""Preset tournament rosters for common evaluation workflows."""

from typing import Optional, Sequence, Tuple

PRESET_ROSTERS = {
    "baseline": ("random", "greedy", "heuristic"),
    "search": ("heuristic", "minimax"),
    "full": ("random", "greedy", "heuristic", "minimax"),
}


def resolve_roster(
    bots: Sequence[str],
    preset: Optional[str] = None,
) -> Tuple[str, ...]:
    """Resolve an explicit or preset roster for simulation commands."""

    if preset is not None and bots:
        raise ValueError("Choose either explicit bots or a preset roster, not both.")
    if preset is not None:
        normalized = preset.strip().lower()
        if normalized not in PRESET_ROSTERS:
            raise ValueError(f"Unknown roster preset: {preset}")
        return PRESET_ROSTERS[normalized]

    normalized_bots = tuple(bot.strip().lower() for bot in bots if bot.strip())
    if len(normalized_bots) < 2:
        raise ValueError("At least two bots are required unless a preset is used.")
    return normalized_bots
