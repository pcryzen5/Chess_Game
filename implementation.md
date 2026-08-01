# Implementation Plan: Chess Game Enhancement

## Context
The project is a Python/Pygame chess game. While the basic rules are implemented, the game needs professional-grade rule completeness (verified as mostly done but needs documentation update), a significant AI intelligence upgrade, better UX polish, and a more robust technical architecture to support further growth.

## Recommended Approach

### Phase 1: Architecture & Documentation
**Goal**: Establish a clean separation between game logic and presentation, and correct project documentation.
- **Task 1.1: Update README.md**: Move Castling, En Passant, Promotion, and Checkmate from "Future Enhancements" to "Complete Chess Rules".
- **Task 1.2: Decouple Engine from Renderer**: 
    - Create `engine.py`.
    - Move `PieceType`, `Color`, `Piece`, `ChessBoard`, and `ChessAI` classes to `engine.py`.
    - Remove Pygame dependencies from the `Piece` class.
    - Implement a mapping in `chess_game.py` to handle image assets for the decoupled pieces.

### Phase 2: Core Stability & Data Management
**Goal**: Ensure the engine is bug-free and implement state persistence.
- **Task 2.1: Unit Test Suite**: Create `tests/test_engine.py` to validate all piece movements and win/draw conditions using `pytest`.
- **Task 2.2: JSON Save/Load System**: Implement `save_game()` and `load_game()` in `ChessBoard` using the `json` module to serialize board state and history.

### Phase 3: AI Intelligence Upgrade
**Goal**: Transition from heuristic-based selection to a search-based AI.
- **Task 3.1: Piece-Square Tables**: Define 8x8 arrays for each piece type to evaluate positional strength.
- **Task 3.2: Minimax with Alpha-Beta Pruning**:
    - Implement recursive Minimax search.
    - Add Alpha-Beta pruning to optimize search depth.
    - Integrate this into `ChessAI.get_hard_move()`.

### Phase 4: UX Polish & Feature Set
**Goal**: Enhance the visual and auditory experience.
- **Task 4.1: Visual Themes**: Add a theme selection menu to change board and piece colors.
- **Task 4.2: Game Timers**: Implement Blitz (3m) and Rapid (10m) presets.
- **Task 4.3: Move History & Undo**: Enhance the sidebar UI and add Undo/Redo buttons leveraging `move_states`.
- **Task 4.4: Sound Effects**: Integrate audio assets for moves, captures, checks, and game over.

## Critical Files
- `chess_game.py`: Main renderer and current logic (will be split).
- `engine.py`: (New) Core game logic.
- `README.md`: Documentation update.
- `tests/test_engine.py`: (New) Unit tests.

## Verification Plan
1. **Architecture**: Run the game after decoupling to ensure no regressions in functionality.
2. **Rules/Stability**: Run the unit test suite to ensure 100% coverage of movement and win conditions.
3. **AI**: Compare "Hard" AI performance before and after Minimax implementation.
4. **UX**: Manual test of theme switching, timer countdowns, and undo functionality.
5. **Persistence**: Save a game, restart, load, and verify identical board state.
