"""Lightweight analysis helpers for exported tournament data."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple


@dataclass(frozen=True)
class BotInsight:
    """Ranking-oriented insight for one bot in an export."""

    label: str
    win_rate: float
    average_margin: float
    average_rank: Optional[float]
    first_place_finishes: Optional[int]


@dataclass(frozen=True)
class MatchupInsight:
    """Interpretation of one matchup summary from an export."""

    pair_label: str
    record: str
    average_margin_for_left: float
    note: str


@dataclass(frozen=True)
class ExportAnalysis:
    """Human-readable insights derived from an exported JSON file."""

    export_kind: str
    board_size: int
    matches_played: int
    first_player_note: str
    rankings: Tuple[BotInsight, ...]
    matchup_insights: Tuple[MatchupInsight, ...]


def load_export(path: str) -> Dict[str, object]:
    """Load an exported tournament or experiment JSON file."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def analyze_export(payload: Dict[str, object]) -> ExportAnalysis:
    """Build a lightweight analysis from tournament or experiment JSON."""

    export_kind, aggregate, summaries = _normalize_payload(payload)
    summary = aggregate["summary"]
    rankings = _build_rankings(aggregate["standings"], summaries)
    matchup_insights = _build_matchup_insights(aggregate["matchups"])
    return ExportAnalysis(
        export_kind=export_kind,
        board_size=payload.get("board_size", aggregate.get("board_size", 8)),
        matches_played=summary["matches_played"],
        first_player_note=_build_first_player_note(summary),
        rankings=rankings,
        matchup_insights=matchup_insights,
    )


def render_analysis_report(analysis: ExportAnalysis) -> str:
    """Render a readable report from export analysis."""

    lines = [
        "Othello Bot Arena Export Analysis",
        f"Source type: {analysis.export_kind}",
        f"Board size: {analysis.board_size}x{analysis.board_size}",
        f"Matches analyzed: {analysis.matches_played}",
        analysis.first_player_note,
        "",
        "Rankings",
    ]

    for index, insight in enumerate(analysis.rankings, start=1):
        suffix = ""
        if insight.average_rank is not None:
            suffix += f" | avg rank {insight.average_rank:.2f}"
        if insight.first_place_finishes is not None:
            suffix += f" | firsts {insight.first_place_finishes}"
        lines.append(
            f"{index}. {insight.label} | win rate {insight.win_rate:.2%} | "
            f"avg margin {insight.average_margin:+.2f}{suffix}"
        )

    lines.append("")
    lines.append("Matchup Notes")
    for insight in analysis.matchup_insights:
        lines.append(
            f"- {insight.pair_label} | record {insight.record} | "
            f"avg margin {insight.average_margin_for_left:+.2f} | {insight.note}"
        )
    return "\n".join(lines)


def render_analysis_markdown(analysis: ExportAnalysis) -> str:
    """Render a slide-ready markdown summary from export analysis."""

    lines = [
        "# Othello Bot Arena Summary",
        "",
        f"- Source: {analysis.export_kind}",
        f"- Board size: {analysis.board_size}x{analysis.board_size}",
        f"- Matches analyzed: {analysis.matches_played}",
        f"- First-player effect: {analysis.first_player_note}",
        "",
        "## Rankings",
        "",
        "| Rank | Bot | Win Rate | Avg Margin | Avg Rank | Firsts |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for index, insight in enumerate(analysis.rankings, start=1):
        average_rank = (
            f"{insight.average_rank:.2f}"
            if insight.average_rank is not None
            else "-"
        )
        firsts = (
            str(insight.first_place_finishes)
            if insight.first_place_finishes is not None
            else "-"
        )
        lines.append(
            f"| {index} | {insight.label} | {insight.win_rate:.2%} | "
            f"{insight.average_margin:+.2f} | {average_rank} | {firsts} |"
        )

    lines.extend(["", "## Matchup Notes", ""])
    for insight in analysis.matchup_insights:
        lines.append(
            f"- **{insight.pair_label}**: record {insight.record}, "
            f"avg margin {insight.average_margin_for_left:+.2f}. {insight.note}."
        )
    return "\n".join(lines).rstrip() + "\n"


def write_analysis_markdown(analysis: ExportAnalysis, path: str) -> None:
    """Write a slide-ready markdown summary to disk."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_analysis_markdown(analysis), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point for export analysis."""

    parser = argparse.ArgumentParser(
        description="Analyze exported Othello Bot Arena tournament JSON."
    )
    parser.add_argument("input_json", help="path to a tournament or experiment JSON export")
    parser.add_argument(
        "--markdown-out",
        help="optional path to write a markdown summary report",
    )
    args = parser.parse_args(argv)

    analysis = analyze_export(load_export(args.input_json))
    if args.markdown_out:
        write_analysis_markdown(analysis, args.markdown_out)
        print(f"Wrote analysis markdown to {args.markdown_out}")
        return 0
    print(render_analysis_report(analysis))
    return 0


def _normalize_payload(
    payload: Dict[str, object],
) -> Tuple[str, Dict[str, object], Dict[str, Dict[str, object]]]:
    if "aggregate" in payload:
        summaries = {item["label"]: item for item in payload.get("summaries", [])}
        return "experiment", payload["aggregate"], summaries
    return "tournament", payload, {}


def _build_rankings(
    standings: Sequence[Dict[str, object]],
    summaries: Dict[str, Dict[str, object]],
) -> Tuple[BotInsight, ...]:
    rankings = []
    for row in standings:
        label = row["label"]
        games = row["games"]
        summary = summaries.get(label, {})
        rankings.append(
            BotInsight(
                label=label,
                win_rate=(row["wins"] / games) if games else 0.0,
                average_margin=row["average_disc_diff"],
                average_rank=summary.get("average_rank"),
                first_place_finishes=summary.get("first_place_finishes"),
            )
        )
    return tuple(rankings)


def _build_matchup_insights(
    matchups: Sequence[Dict[str, object]],
) -> Tuple[MatchupInsight, ...]:
    insights = []
    for row in sorted(matchups, key=lambda item: (abs(item["average_margin_for_left"]), item["left_label"], item["right_label"])):
        left_label = row["left_label"]
        right_label = row["right_label"]
        average_margin = row["average_margin_for_left"]
        left_wins = row["left_wins"]
        right_wins = row["right_wins"]
        draws = row["draws"]
        if left_wins > 0 and right_wins > 0:
            note = "both bots won games in this pairing"
        elif abs(average_margin) < 6:
            note = "the average margin stayed small"
        elif draws > 0:
            note = "draws kept this pairing competitive"
        else:
            stronger = left_label if average_margin > 0 else right_label
            note = f"{stronger} had the clearer edge"
        insights.append(
            MatchupInsight(
                pair_label=f"{left_label} vs {right_label}",
                record=f"{left_wins}-{right_wins}-{draws}",
                average_margin_for_left=average_margin,
                note=note,
            )
        )
    return tuple(insights)


def _build_first_player_note(summary: Dict[str, object]) -> str:
    black_wins = summary["black_wins"]
    white_wins = summary["white_wins"]
    decisive_games = black_wins + white_wins
    if decisive_games == 0:
        return "No decisive games were present, so first-player effects are inconclusive."

    black_rate = black_wins / decisive_games
    if black_rate >= 0.60:
        return (
            f"Black won {black_rate:.2%} of decisive games, which suggests a possible "
            "first-player advantage."
        )
    if black_rate <= 0.40:
        return (
            f"Black won {black_rate:.2%} of decisive games, which suggests the second "
            "player may have held the edge in this sample."
        )
    return f"Black won {black_rate:.2%} of decisive games, which looks fairly balanced."


if __name__ == "__main__":
    raise SystemExit(main())
