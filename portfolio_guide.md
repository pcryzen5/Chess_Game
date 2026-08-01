# Portfolio Presentation Guide: Chess AI Enhancement

This guide details how to host, compile, and present this Chess Game project on your developer portfolio website.

---

## 1. Hosting a Playable Browser Version (WebAssembly)

Instead of just showing code, you can allow recruiters to play your game directly on your website using **WebAssembly** via the Pygame web compiler (`pygbag`).

### Steps to Compile to HTML5:
1. **Install pygbag**:
   ```bash
   pip install pygbag
   ```
2. **Compile the App**:
   Run the compiler in your terminal pointing to the project folder. If the `pygbag` command is not recognized directly due to PATH issues, use `python -m pygbag`:
   ```bash
   python -m pygbag c:\Users\shubhAM\Desktop\ChessGame
   ```
   This compiles your Python game loop into WebAssembly/HTML5 assets and creates a `build/web` folder.
3. **Host Online**:
   Upload the contents of `build/web` to static hosting platforms like **GitHub Pages**, **Netlify**, or **Vercel** for free. You can embed it in an `<iframe>` on your main portfolio site.

---

## 2. GitHub Repository Structure

A clean repository is the first thing recruiters look at. Configure your repository as follows:

1. **Add `requirements.txt`**:
   Add a standard package list at the root directory:
   ```
   pygame>=2.6.0
   pytest>=9.0.0
   ```
2. **Organize Source Files**:
   * `chess_game.py`: GUI Presentation and presentational logic.
   * `engine.py`: Pure Chess state, rules, and Minimax AI logic.
   * `tests/`: Directory containing pytest unit test scripts.
   * `assets/`: 3D wooden pieces sprites folder.

---

## 3. Highlighting Technical Architecture

When writing the project description on your portfolio site, emphasize these architectural achievements:

### 🌟 Decoupled Architecture (MVC Pattern)
* Separated presentation logic from game logic. `engine.py` is a 100% pure Python model with zero external library dependencies, meaning the rules can run headlessly or easily adapt to a web/mobile GUI in the future.

### 🧠 Recursive Minimax & Heuristic Evaluation
* Upgraded the AI from random/greedy moves to a **depth-3 Minimax search** with **Alpha-Beta pruning** to optimize nodes.
* Structured Piece-Square Tables (PST) to evaluate spatial positioning (e.g. Knight development, pawn center control).
* Wrote dynamic simulated rollback state mutators (`make_temp_move()` / `undo_temp_move()`) to evaluate paths without permanent memory overhead.

### 🔈 Procedural WAV Sound Synthesis
* Designed an in-memory sound generator using Python's standard `wave` and `struct` libraries. Tones, sweep captures, and alerts are synthesized programmatically on startup, ensuring the game has audio without requiring disk asset downloads.

### 🧪 Robust Test Coverage
* Built a test suite covering 18 validation criteria (repetition draws, checkmate paths, en-passant coordinate translations, castling rights) to guarantee engine stability.

---

## 4. Sample README Structure

Overwrite or append this layout to your `README.md` to show a professional presentation:

```markdown
# Chess AI Enhanced ♟️

A responsive Chess platform built with Python & Pygame, featuring a custom Minimax AI engine, procedural audio, and customizable themes.

## Key Features
* **Minimax Search Engine**: Hard AI calculates optimal moves using a search tree with Alpha-Beta pruning.
* **Procedural Sound**: Audio is compiled dynamically in-memory on startup.
* **Undo/Redo Navigation**: Roll back moves using the match state buffer.
* **Visual Styling**: Choose from four clean board color themes.
```
