# Othello Bot Arena

Othello Bot Arena is a CMPS/CMPM 146 course project centered on game AI rather than UI polish. The project combines a correct, pure Othello engine with a lightweight playable prototype and a growing ladder of bots that can later be compared in tournament-style evaluation.

## Current Status

Implemented so far:

- pure 8x8 Othello rules engine
- automated tests for move generation, flipping, passing, terminal states, and scoring
- baseline AI agents with short move explanations
- minimax search with alpha-beta pruning
- minimal CLI prototype for human-vs-bot and bot-vs-bot play

Planned next:

- tournament and simulation tooling
- stronger AI comparisons and analysis output
- optional MCTS as a stretch goal

## Repository Layout

- `engine/`: pure game rules and state transitions
- `bots/`: AI agents, shared bot interfaces, and evaluation helpers
- `ui/`: terminal-based playable prototype
- `sim/`: future bot-vs-bot evaluation tools
- `tests/`: automated correctness tests

## Engine Design

The engine is intentionally UI-independent. It exposes immutable game states and clear successor generation so the same rules layer can support:

- human play
- baseline bots
- minimax and alpha-beta search
- possible MCTS later
- tournament simulation without duplicated rules logic

## Bots

Available bots:

- `RandomBot`: chooses a legal move uniformly at random
- `GreedyBot`: chooses the move that flips the most discs immediately
- `HeuristicBot`: evaluates successor states using corners, corner danger, mobility, edge control, and disc balance
- `MinimaxBot`: searches future positions with alpha-beta pruning and a configurable depth

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

Other supported controller names are `human`, `random`, `greedy`, `heuristic`, and `minimax`.

## Course Framing

This repository is meant to stay focused on game AI:

- adversarial search
- heuristic and utility-style evaluation
- comparing weak and strong agents
- explainable move choices
- architecture that can later support tournaments and analysis
