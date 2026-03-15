Group 9: Reversi - Othello Bot Arena + Move Explanation Sandbox

Team: Arvin Arbabi, Mika Wu, Ethan Coates, Ryan Chou

Overview: We will build a playable Othello/Reversi game plus an AI sandbox for testing and comparing different strategies. The project will support human vs bot and bot vs bot play, with correct rule handling (legal moves, flipping, passing turns, scoring) and a simple move explanation system for bot decisions.
Theme: Classic board game strategy with an AI experimentation focus. The experience is part game and part “strategy lab,” where players can both play Othello and observe how different bots make decisions under the same game rules.

Novelty: Our project adds a creative AI sandbox layer:
Multiple bots with different play styles (random, greedy, heuristic, minimax)
Bot-vs-bot tournament mode for automated comparisons
Move explanation text (why a bot chose a move)
Optional board/rule variants (such as 6x6 mode) for testing strategy behavior

Value: This project is a way to apply game AI concepts from class. It demonstrates things like: adversarial search, heuristic evaluation, and simulation-based comparison in a game that is easy to understand but still has depth. It also has educational value because users can see how different AI strategies behave and improve.

Technology:
Language: Python
Game logic: custom Othello rules engine (board state, legal moves, disc flipping, scoring)
AI techniques:
Random action selection
Greedy heuristic (immediate gain)
Heuristic evaluation (corners, mobility, edges, disc count weighting)
Minimax with alpha-beta pruning (advanced bot)
UI: Tkinter or Pygame
Simulation tools: batch bot-vs-bot runner for win-rate and score statistics

The final assignment for CM 146 is a ~1 month long creative project (3 weeks in summer session)
that applies the knowledge about AI techniques you have gained. The goal is to employ AI in an
interesting/novel way to address any aspect of game design, development, game play, or
analysis, or to create a novel player experience, etc. The sky is the limit!
Your project should take the form of an implemented computational system, such as an
interactive/playable game prototype, a design tool prototype, or a non-interactive data analysis.
Note the use of the term prototype: your goal is to demonstrate that something is possible by
producing a convincing 1st instance - your goal is not to create a polished end-product.
