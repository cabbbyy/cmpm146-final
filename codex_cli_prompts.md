# Codex CLI Prompts for Othello Bot Arena

These prompts are written for a project that should be built as:
- **Direction 1 first**: playable Othello game + AI strategy lab
- **Direction 2 second**: lightweight move explanations and strategy visibility

The overall goal is to keep the project centered on **game AI**, not on graphics polish.

Core course-aligned themes to preserve throughout implementation:
- adversarial search,
- heuristic / utility-based decision-making,
- comparing agent strategies,
- explainable agent behavior,
- optional MCTS as a stretch goal.

---

# Prompt 1 — Initialize a new repository and build the engine first

```text
You are helping me start a brand new Python repository for a course project called Othello Bot Arena.

This is a GAME AI project, not just a board game clone.
The project should be built as:
- a playable Othello/Reversi game prototype,
- plus an AI strategy lab where bots can be compared,
- plus lightweight move explanations so bot reasoning is visible.

Course focus to emphasize:
- adversarial search,
- utility / heuristic evaluation,
- comparing weak and strong agents,
- explainable game AI,
- architecture that can later support tournament evaluation,
- optional MCTS later as a stretch goal.

Important working style:
- Initialize a NEW git repository for me from scratch.
- Work commit by commit, not in one giant patch.
- Before each coding step, state:
  1. what you inspected,
  2. what you are about to create or change,
  3. which files you will edit,
  4. the exact commit message you recommend.
- After each step, stop and summarize what was completed and what should come next.
- Prefer small, reviewable commits.
- Reuse existing abstractions within the repo once they exist.
- Do not jump ahead to UI polish or advanced features before the engine is correct.

Repository setup requirements:
- Initialize git.
- Create a clean Python project layout.
- Add a README.md with a short project description.
- Add a .gitignore appropriate for Python.
- Add a basic test setup.
- Use a structure like:
  - engine/
  - bots/
  - ui/
  - sim/
  - tests/

Implementation priority for this first prompt:
1. initialize the repository structure,
2. create the pure Othello rules engine for standard 8x8 play,
3. add tests for correctness.

Engine requirements:
- board representation,
- initial starting position,
- legal move generation,
- applying a move,
- disc flipping,
- pass-turn handling,
- terminal-state detection,
- score counting,
- helpers that will support future search bots.

Design constraints:
- Keep engine code pure and independent from UI.
- Keep future bot integration in mind.
- Make state transitions clear enough for minimax and possible MCTS later.
- Favor readability over premature optimization.

Testing requirements:
- test initial legal moves,
- test move application and flipping,
- test pass behavior,
- test terminal detection,
- test score counting.

Non-goals for this step:
- no GUI yet,
- no advanced bots yet,
- no tournament runner yet,
- no polished UX.

Project framing reminder:
This course is about game AI. The architecture should make it easy in later steps to add:
- RandomBot,
- GreedyBot,
- HeuristicBot using utility-style evaluation,
- MinimaxBot with alpha-beta pruning,
- optional MCTSBot as a stretch goal,
- short explanation strings for chosen moves,
- bot-vs-bot tournament evaluation.

Start by inspecting the empty/new repository state, then initialize the repository and implement only the repository scaffold + pure engine + tests in small commits.
```

---

# Prompt 2 — Add baseline bots and explanations

```text
Continue from the current repository state.

Goal for this step:
Implement baseline Othello bots on top of the existing engine.

This is a game AI course project, so prioritize distinct decision policies over UI polish.

Requirements:
- Reuse the current engine.
- Do not duplicate move-generation logic inside bots.
- Add a shared bot interface with methods like:
  - choose_move(state, color)
  - explain_move(state, color, move)
- Implement:
  1. RandomBot
  2. GreedyBot
  3. HeuristicBot

HeuristicBot should use a utility-style evaluation function based on features like:
- corner ownership,
- corner danger / adjacency,
- mobility,
- edge preference,
- disc differential,
- optionally game-phase weighting.

Explanation requirements:
- Every bot must return a short explanation string tied to its actual policy.
- Avoid generic filler.
- Examples:
  - “Chose c4 because it flips the most discs immediately.”
  - “Chose a1 because corners are permanent and highly valuable.”
  - “Chose d3 to improve mobility while avoiding risky squares near corners.”

Process requirements:
- inspect existing code before editing,
- work commit by commit,
- explain which abstractions are being reused,
- add or update tests where appropriate,
- stop after each small implementation step and summarize progress.
```

---

# Prompt 3 — Build a minimal playable prototype

```text
Continue from the current repository state.

Goal for this step:
Create a minimal playable Othello prototype that supports:
- human vs bot,
- bot vs bot.

Constraints:
- Keep the UI simple and functional.
- Do not entangle rendering/input with engine logic.
- Use the existing engine and bot interface.
- Prefer a clean CLI/TUI or a very lightweight Tkinter UI if practical.
- Game AI correctness matters more than visuals.

Display requirements:
- board state,
- current player,
- legal moves if practical,
- score,
- explanation text for bot turns.

Behavior requirements:
- enforce only legal moves,
- pass automatically when no legal move exists,
- detect terminal state correctly,
- announce final winner and score.

Process requirements:
- inspect first,
- work in small commits,
- explain file edits before making them,
- provide a short manual test plan at the end.
```

---

# Prompt 4 — Add tournament mode for agent comparison

```text
Continue from the current repository state.

Goal for this step:
Add a bot-vs-bot tournament and simulation module.

This is important because the project should function as an AI strategy lab, not just a playable board game.

Requirements:
- Reuse the existing engine and bot interface.
- Support many automated matches.
- Support at least round-robin comparisons between bots.
- Collect summary statistics such as:
  - wins,
  - losses,
  - draws,
  - average final score differential,
  - optional first-player advantage.
- Print clean summaries to the terminal.
- Structure the code so results could later be exported to CSV or JSON.

Engineering requirements:
- avoid hardcoding bot-specific logic into the simulator,
- keep match execution separate from statistics aggregation,
- add tests where reasonable.

Process requirements:
- inspect current code first,
- work commit by commit,
- summarize changed files and suggested commit messages.
```

---

# Prompt 5 — Add minimax with alpha-beta pruning

```text
Continue from the current repository state.

Goal for this step:
Implement an advanced Othello bot using minimax with alpha-beta pruning.

This is one of the most important game-AI techniques in the project.

Requirements:
- Reuse the existing engine and bot interface.
- Do not duplicate rules logic.
- Add configurable search depth.
- Reuse or cleanly refactor the existing heuristic evaluation so HeuristicBot and MinimaxBot can share it if appropriate.
- Keep the code readable for a class project.

Explanation requirements:
- Provide a short explanation for the chosen move based on evaluation priorities or the best line found.
- Keep explanations understandable to a human viewer.

Performance requirements:
- use alpha-beta pruning correctly,
- avoid unnecessary state copying where reasonable,
- prefer clarity over over-engineering.

Process requirements:
- inspect current code first,
- extend existing abstractions rather than introducing parallel systems,
- work in small commits,
- end with a note about tradeoffs and next improvements.
```

---

# Prompt 6 — Optional stretch: add MCTS

```text
Continue from the current repository state.

Goal for this step:
Add an optional Monte Carlo Tree Search bot as a stretch goal.

Only do this if the existing engine, bots, playable loop, and tournament mode are already stable.

Requirements:
- Reuse the existing engine and bot interface.
- Keep the implementation modular.
- Add configurable rollout count or time budget.
- Compare its behavior against the existing bots.
- Add a short explanation string describing why the chosen move scored well in simulation terms.

Constraints:
- do not destabilize the codebase for the sake of the stretch goal,
- keep the implementation understandable for a student project,
- preserve existing tests and behavior.
```

---

# Prompt 7 — Final cleanup and demo prep

```text
Continue from the current repository state.

Goal for this step:
Prepare the Othello Bot Arena project for final presentation and submission.

Tasks:
- inspect the repository for dead code, duplicated logic, and confusing naming,
- improve README setup and usage instructions,
- add a concise architecture section,
- add a project-features section,
- add a course-relevance section focused on game AI,
- add a limitations/future-work section,
- verify that the core functionality still works:
  - human vs bot,
  - bot vs bot,
  - tournament mode,
  - explanations,
  - minimax,
  - optional MCTS if implemented.

Constraints:
- avoid unnecessary rewrites,
- preserve working behavior,
- clearly separate required fixes from optional polish,
- propose a final cleanup commit sequence instead of one giant commit.
```

---

# Suggested usage order

Use these one at a time:
1. Prompt 1
2. Prompt 2
3. Prompt 3
4. Prompt 4
5. Prompt 5
6. Prompt 6 only if ahead of schedule
7. Prompt 7

---

# Small reminder you can prepend to any prompt

```text
Before coding, inspect the current repository carefully, reuse existing abstractions, keep the project centered on game AI, work on small reviewable commits, and stop after each commit-sized step to summarize progress.
```
