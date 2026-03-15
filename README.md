# Othello Bot Arena

Othello Bot Arena is a course project focused on game AI rather than UI polish. The repository starts with a pure Othello rules engine that can later support baseline bots, adversarial search, lightweight move explanations, and tournament-style evaluation.

## Repository Layout

- `engine/`: pure game rules and state transitions
- `bots/`: future AI agents and explanation logic
- `ui/`: future playable interface
- `sim/`: future bot-vs-bot evaluation tools
- `tests/`: automated correctness tests

## Development

Run the test suite with:

```bash
python3 -m unittest discover -s tests
```
