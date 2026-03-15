# Othello Bot Arena Project Directions

This project should be built as **Direction 1 first** — a playable Othello game with solid rules and clear game loop support — and then **borrow a little from Direction 2** by adding lightweight bot move explanations and AI comparison tools.

That gives you a project that is:
- easy to demo,
- clearly a **game AI** project instead of just a board game clone,
- aligned with the course focus on agent behavior, search, decision-making, and comparing AI techniques.

---

## Recommended project framing

### Working title
**Othello Bot Arena: A Playable Reversi Game with Explainable Game AI**

### One-sentence pitch
Build a playable Othello/Reversi prototype where humans can play against multiple AI agents, bots can play each other, and each bot can briefly explain why it chose a move.

### Best project identity
Think of the project as:
- **80% playable game + AI strategy lab**
- **20% explainable AI sandbox**

Do **not** make the project primarily about graphics or UI polish. The course is about **game AI**, so the strongest version emphasizes:
- agent decision-making,
- adversarial search,
- utility/heuristic evaluation,
- simulation and comparison,
- explainability of choices.

---

## Final recommended scope

## Direction 1: Playable Game + AI Strategy Lab

### Core experience
A player can launch the game and do at least the following:
- play Othello against a bot,
- watch two bots play each other,
- switch between multiple AI styles,
- see a short explanation for bot moves,
- optionally run repeated bot-vs-bot matches to compare performance.

### Why this is the strongest direction
This direction directly supports the course goals:
- **What makes a smart agent smart?** You can compare weak and strong decision policies.
- **Do players want smart AI?** You can show how different bots feel to play against.
- **Game AI techniques matter more than graphics.** The interesting part is how the agents reason.
- **Prototype over product.** A convincing AI-focused prototype is better than a polished but shallow game.

---

## How to “steal a little” from Direction 2

Use explainability as a **supporting feature**, not the whole project.

That means:
- each bot returns both a move and a short explanation,
- the explanation should reference its actual policy,
- optionally show top candidate moves for stronger bots,
- optionally show a score breakdown for heuristic bots.

### Good examples of explanation text
- “Chose c4 because it flips the most discs immediately.”
- “Chose a1 because corners are permanent and highly valuable.”
- “Chose d3 because it improves mobility and avoids giving away a corner.”
- “Chose f5 because it leads to the best evaluated future position at depth 3.”

The point is not full natural-language sophistication. The point is to make the AI’s policy visible during play and demonstration.

---

## Course-aligned AI features to emphasize

These are the course ideas your project can naturally showcase.

### 1. Adversarial search
This is the most obvious and important course connection.
- **Minimax with alpha-beta pruning** should be your advanced bot.
- This is one of the clearest ways to show real game-AI reasoning in a deterministic board game.

### 2. Utility / heuristic models
Your mid-tier bots should use evaluation functions rather than pure search.
Possible features in the evaluation function:
- corner ownership,
- corner-adjacent danger,
- mobility,
- edge preference,
- disc differential,
- late-game weighting.

This connects well to the course’s discussion of **utility models** and what makes agents behave intelligently.

### 3. Strategy comparison through simulation
A tournament runner is a great way to evaluate agents under identical conditions.
That lets you answer questions like:
- does greedy beat random consistently?
- does heuristic beat greedy?
- how much stronger is minimax at shallow depth?
- is first-player advantage significant?

This makes the project feel analytical and game-AI-focused rather than just interactive.

### 4. Explainable decision-making
This is the small piece you borrow from Direction 2.
Use explanations to connect bot behavior back to its policy.
This helps during demo, presentation, and report writing.

### 5. Optional advanced stretch: MCTS
If your team finishes early and wants an extra course connection, add an **MCTS bot** as a stretch goal.
This would tie directly to the course’s Monte Carlo Tree Search content.
Do **not** make MCTS required for the baseline project. It is a great stretch goal, not a first priority.

---

## Recommended bot ladder

Build the bots in increasing order of sophistication.

### Bot 1 — RandomBot
- chooses any legal move uniformly at random
- useful baseline
- easy to verify

### Bot 2 — GreedyBot
- chooses the move that flips the most discs immediately
- intentionally short-sighted
- good demonstration that “more immediate reward” is not always smarter

### Bot 3 — HeuristicBot
- evaluates positions using weighted features
- stronger and more course-relevant than greedy
- can explain choices in terms of strategic values

### Bot 4 — MinimaxBot
- alpha-beta pruning
- configurable search depth
- strongest planned bot
- best example of adversarial game AI

### Stretch Bot — MCTSBot
- optional if the team has time
- great syllabus tie-in
- should only be attempted after the first four bots are stable

---

## Recommended architecture

Keep AI and rules separate from presentation.

## `engine/`
Pure Othello rules only.
Responsibilities:
- board representation,
- legal move generation,
- applying moves,
- flipping discs,
- pass-turn handling,
- terminal-state detection,
- scoring,
- cloning or successor generation as needed for bots.

This should be the most tested part of the project.

## `bots/`
All agents live here.
Suggested interface:

```python
choose_move(state, color) -> Move | None
explain_move(state, color, move) -> str
```

Optional shared helpers:
- evaluation functions,
- move ordering,
- search utilities.

## `ui/`
Keep it simple.
Could be:
- Tkinter,
- Pygame,
- or even a strong CLI/TUI if time is limited.

Responsibilities:
- draw board,
- accept human input,
- display current player,
- show score,
- show explanation text,
- run the turn loop.

## `sim/`
For experiments and comparisons.
Responsibilities:
- run bot-vs-bot matches,
- run repeated tournaments,
- collect aggregate statistics,
- print readable summaries.

## `tests/`
Most tests should focus on:
- legal move generation,
- correct flips,
- pass handling,
- terminal state detection,
- bot legality,
- reproducible tournament logic where possible.

---

## Concrete milestone plan

## Milestone 1 — Engine first
Deliverables:
- rules engine,
- board representation,
- legal moves,
- move application,
- pass logic,
- score counting,
- unit tests,
- simple CLI board printer.

Goal:
Make the game fully correct before adding sophisticated AI.

## Milestone 2 — Baseline AI agents
Deliverables:
- RandomBot,
- GreedyBot,
- HeuristicBot,
- bot interface,
- explanation strings.

Goal:
Show multiple distinct AI behaviors and connect them to course concepts.

## Milestone 3 — Playable prototype
Deliverables:
- human vs bot,
- bot vs bot,
- current score display,
- turn handling,
- game over screen/message,
- explanation panel/output.

Goal:
Have something demoable even before advanced search is added.

## Milestone 4 — Stronger AI and evaluation
Deliverables:
- MinimaxBot with alpha-beta pruning,
- configurable depth,
- basic tournament runner,
- summary stats.

Goal:
Make the project clearly about **game AI comparison**.

## Stretch milestone
Possible additions:
- MCTS bot,
- 6x6 variant,
- replay mode,
- top-3 candidate move display,
- CSV/JSON export,
- stronger explanation breakdown.

---

## What to say in the presentation/report

Emphasize these points.

### Why this belongs in the course
- The project studies **game-playing agents** in a controlled environment.
- It compares multiple AI techniques under the same rules.
- It demonstrates adversarial search, heuristics, utility-based evaluation, and explainability.
- It lets players directly experience the difference between weak and strong AI.

### The central question
A strong presentation angle is:
**How does the style of decision-making change the quality and feel of a game-playing agent?**

That lets you compare:
- random behavior,
- short-term reward behavior,
- strategic heuristic behavior,
- lookahead search behavior.

### What makes it more than “just Othello”
The novelty is not the game itself. The novelty is:
- the AI ladder,
- the tournament comparison,
- the explanation system,
- the use of Othello as a testbed for game AI design.

---

## What to avoid

Avoid these traps:
- spending most of the time on graphics,
- adding too many game variants too early,
- tightly coupling bots to UI code,
- implementing the strongest bot before simpler bots are working,
- overpromising advanced AI techniques you may not finish.

The cleanest successful version is:
- correct game,
- 3–4 working bots,
- short explanations,
- bot-vs-bot comparison,
- clear demo.

---

## Recommended team split

### Person 1
Rules engine + tests

### Person 2
Playable loop + UI

### Person 3
Baseline bots + explanations

### Person 4
Minimax + tournament runner + analysis/polish

If responsibilities overlap, that is fine, but keep one person primarily responsible for engine correctness.

---

## Final recommendation

Build this as a **playable Othello game first**, then layer in **game-AI comparison and lightweight explanation features**.

That gives you the best combination of:
- feasibility,
- course relevance,
- demo strength,
- AI depth,
- novelty.

If you stay disciplined, this can look like a very strong **game AI prototype** rather than just a class programming assignment.
