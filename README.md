# Othello Bot Arena

Othello Bot Arena is a CMPM/CMPS 146 game AI project built around three connected goals:

- a playable Othello/Reversi prototype
- an explainable bot sandbox
- a comparative evaluation lab for weak and strong agents

The code stays centered on course themes: adversarial search, heuristic evaluation, simulation-based comparison, explainable decision-making, and contrasting baseline agents with stronger search bots.

## What The Project Supports

- Pure Othello engine with immutable state transitions for 8x8 and 6x6 play
- Playable terminal game for human-vs-bot and bot-vs-bot matches
- Demo mode for live presentations with clearer board rendering and labeled move output
- Optional verbose explanations with top candidate moves and bot-specific reasoning
- Replay export to JSON plus markdown replay summaries
- Tournament mode, repeated evaluation mode, JSON/CSV exports, and markdown summary reports

## Repository Layout

- `engine/`: pure rules, board geometry helpers, and state transitions
- `bots/`: bot interface, evaluators, and bot implementations
- `ui/`: terminal play loop, demo mode, and replay helpers
- `sim/`: tournaments, repeated experiments, exports, and summary analysis
- `tests/`: automated correctness and integration coverage

## Bots

- `RandomBot`: samples uniformly from legal moves
- `GreedyBot`: maximizes immediate flips
- `HeuristicBot`: uses corners, corner danger, mobility, edges, and disc balance
- `MinimaxBot`: adversarial search with alpha-beta pruning and configurable depth
- `MCTSBot`: Monte Carlo Tree Search with configurable rollout budget and heuristic-guided playouts

The stronger bots reuse the same pure engine and evaluation helpers, so tournament comparisons stay grounded in the same game logic.

## Run Tests

```bash
python3 -B -m unittest discover -s tests
```

## Play The Game

Human vs heuristic bot:

```bash
python3 -m ui --black human --white heuristic
```

Live demo between bots:

```bash
python3 -m ui --black greedy --white heuristic --demo
```

Verbose demo with search bots:

```bash
python3 -m ui --black minimax --white mcts --demo --explain-verbose
```

Smaller-board demo:

```bash
python3 -m ui --black human --white minimax --board-size 6 --minimax-depth 3
```

Useful CLI options:

- `--demo`: presentation-friendly rendering and labeled move summaries
- `--demo-delay`: optional pause between bot turns during demos
- `--explain-verbose`: show top candidate moves and bot-specific reasoning
- `--replay-out path.json`: write a replay JSON file for the finished game
- `--board-size {6,8}`: choose the board size
- `--minimax-depth N`: configure minimax depth
- `--mcts-iterations N`: configure MCTS rollout budget

Default search budgets are tuned to keep live demo commands responsive. Use explicit `--minimax-depth` and `--mcts-iterations` values when you want stronger but slower evaluations.

## Replay Export

Write a replay while a game runs:

```bash
python3 -m ui --black greedy --white heuristic --demo --replay-out results/game.json
```

Convert a replay JSON file into markdown:

```bash
python3 -m ui.replay results/game.json --markdown-out results/game.md
```

Replay turns include:

- board state before the move
- player to move
- legal moves
- chosen move
- explanation text
- score after the move

## Run Experiments

Small tournament:

```bash
python3 -m sim random greedy heuristic --games-per-pair 2
```

Repeated search-focused comparison:

```bash
python3 -m sim --preset stretch --games-per-pair 1 --repetitions 2
```

6x6 repeated evaluation with exports:

```bash
python3 -m sim heuristic minimax mcts \
  --games-per-pair 2 \
  --repetitions 3 \
  --board-size 6 \
  --minimax-depth 3 \
  --mcts-iterations 200 \
  --json-out results/experiment.json \
  --standings-csv results/standings.csv \
  --matches-csv results/matches.csv \
  --summary-md results/summary.md
```

Preset rosters:

- `baseline`: random, greedy, heuristic
- `search`: heuristic, minimax
- `stretch`: heuristic, minimax, mcts
- `full`: random, greedy, heuristic, minimax, mcts

## Analyze Results

Analyze an exported tournament or experiment JSON file:

```bash
python3 -m sim.analysis results/experiment.json
```

Write a presentation-ready markdown summary:

```bash
python3 -m sim.analysis results/experiment.json --markdown-out results/summary.md
```

Summary output highlights:

- win rate rankings
- average margin
- repeated-run average rank and first-place finishes
- matchup notes
- possible first-player effects

## Architecture Notes

- `engine/` stays pure and UI-independent so minimax, MCTS, and future bots all share one rules layer.
- `bots/` separates weak and strong agents cleanly, which makes tournaments and writeups easier.
- `sim/` keeps comparative evaluation reusable instead of tying experiments to the playable UI.
- explanation strings and verbose candidate details are attached to actual bot decisions, not mocked presentation text.

## Course Framing

This project is already suitable for discussing:

- adversarial search and alpha-beta pruning
- utility-style heuristic design
- weak-vs-strong agent comparisons
- explainable game AI outputs
- tournament-style evaluation and repeated experiments
- MCTS as a stretch-search extension
