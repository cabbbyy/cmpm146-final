# Othello Bot Arena

Othello Bot Arena is a CMPS/CMPM 146 course project centered on game AI rather than UI polish. The project combines a correct, pure Othello engine with a lightweight playable prototype and a growing ladder of bots that can later be compared in tournament-style evaluation.

## Current Status

Implemented so far:

- pure 8x8 Othello rules engine
- automated tests for move generation, flipping, passing, terminal states, and scoring
- baseline AI agents with short move explanations
- minimax search with alpha-beta pruning
- MCTS bot as a stretch-search agent
- minimal CLI prototype for human-vs-bot and bot-vs-bot play
- round-robin tournament simulation with summary statistics
- JSON and CSV export support for tournament results
- repeated evaluation mode with preset bot rosters and consistency summaries
- lightweight analysis helpers for exported tournament and experiment JSON

Planned next:

- MCTS tuning and stronger rollout/analysis comparisons if the team wants to push the stretch work further

## Repository Layout

- `engine/`: pure game rules and state transitions
- `bots/`: AI agents, shared bot interfaces, and evaluation helpers
- `ui/`: terminal-based playable prototype
- `sim/`: bot-vs-bot tournament and reporting tools
- `tests/`: automated correctness tests

## Engine Design

The engine is intentionally UI-independent. It exposes immutable game states and clear successor generation so the same rules layer can support:

- human play
- baseline bots
- minimax and alpha-beta search
- MCTS and other stretch-search experiments
- tournament simulation without duplicated rules logic

## Bots

Available bots:

- `RandomBot`: chooses a legal move uniformly at random
- `GreedyBot`: chooses the move that flips the most discs immediately
- `HeuristicBot`: evaluates successor states using corners, corner danger, mobility, edge control, and disc balance
- `MinimaxBot`: searches future positions with alpha-beta pruning and a configurable depth
- `MCTSBot`: searches with Monte Carlo Tree Search using configurable rollout counts

Each bot returns both a move and a short explanation string tied to its actual policy.

## Development

Run the test suite with:

```bash
python3 -m unittest discover -s tests
```

## Play The Prototype

Run a human vs bot game:

```bash
python3 -m ui --black human --white heuristic
```

Watch two bots play:

```bash
python3 -m ui --black greedy --white heuristic
```

Run against minimax at a specific depth:

```bash
python3 -m ui --black human --white minimax --minimax-depth 3
```

Run against MCTS with a chosen rollout budget:

```bash
python3 -m ui --black human --white mcts --mcts-iterations 200
```

Other supported controller names are `human`, `random`, `greedy`, `heuristic`, `minimax`, and `mcts`.

## Run Tournaments

Run a small round-robin tournament:

```bash
python3 -m sim random greedy heuristic --games-per-pair 2
```

Include minimax at a chosen depth:

```bash
python3 -m sim greedy heuristic minimax --games-per-pair 2 --minimax-depth 3
```

Run a repeated evaluation with a preset roster:

```bash
python3 -m sim --preset baseline --games-per-pair 1 --repetitions 5
```

Compare the search-oriented roster repeatedly:

```bash
python3 -m sim --preset search --games-per-pair 2 --repetitions 3 --minimax-depth 3
```

Compare the stretch-search roster with MCTS included:

```bash
python3 -m sim --preset stretch --games-per-pair 1 --repetitions 3 --minimax-depth 3 --mcts-iterations 200
```

The simulator prints:

- wins, losses, and draws
- average disc differential
- average final score
- first-player results across the tournament
- per-matchup summaries
- per-match scorelines
- repeated-mode first-place counts and average rank

Write structured experiment outputs:

```bash
python3 -m sim greedy heuristic minimax \
  --games-per-pair 2 \
  --minimax-depth 3 \
  --json-out results/tournament.json \
  --standings-csv results/standings.csv \
  --matches-csv results/matches.csv
```

You can include MCTS directly in explicit rosters as well:

```bash
python3 -m sim heuristic minimax mcts \
  --games-per-pair 1 \
  --minimax-depth 3 \
  --mcts-iterations 200
```

In repeated mode, `--json-out` writes the full experiment summary, while the CSV exports contain aggregate standings and aggregate per-match data across all repetitions.

## Analyze Exported Results

Analyze a tournament JSON export:

```bash
python3 -m sim.analysis results/tournament.json
```

Analyze a repeated experiment export:

```bash
python3 -m sim.analysis results/experiment.json
```

The analysis report summarizes:

- win-rate rankings
- average rank and first-place finishes when repeated-mode data is available
- close or split matchups
- possible first-player effects

## Course Framing

This repository is meant to stay focused on game AI:

- adversarial search
- heuristic and utility-style evaluation
- comparing weak and strong agents
- explainable move choices
- architecture that can later support tournaments and analysis
