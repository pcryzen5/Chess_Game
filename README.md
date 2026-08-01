# Chess Game

A fully functional chess game built with Python and Pygame featuring both 2-player and player vs computer modes.

## Features

- **Two Game Modes:**
  - Two Player mode (human vs human)
  - Player vs Computer mode (human vs AI)

- **AI Difficulty Levels:**
  - Easy: Random moves
  - Medium: Prefers capturing pieces
  - Hard: Strategic play with priority for checks and captures

- **Complete Chess Rules:**
  - All piece movement rules implemented (pawn, rook, bishop, knight, queen, king)
  - Castling and en passant moves
  - Pawn promotion with selection UI
  - Check, checkmate, and stalemate detection
  - Draw rules: threefold repetition, fifty-move rule, insufficient material
  - Valid move highlighting
  - Turn-based gameplay
  - Move history tracking in algebraic notation
  - Move navigation (browse game history with ← / → keys or buttons)

- **Visual Features:**
  - Custom PNG piece graphics
  - Board highlighting for selected pieces
  - Valid move indicators
  - Clean, intuitive interface

## Requirements

- Python 3.6 or higher
- Pygame library

## Installation

1. Install Python from https://python.org
2. Install Pygame:
   ```
   pip install pygame
   ```

## Setup

1. Navigate to the ChessGame directory
2. First, create the piece images by running:
   ```
   python create_pieces.py
   ```
   This will create an `assets` folder with all the chess piece PNG files.

3. Run the main game:
   ```
   python chess_game.py
   ```

## How to Play

### Main Menu
- Press `1` to select Two Player mode
- Press `2` to select Player vs Computer mode
- If playing vs Computer, use `E`, `M`, `H` to select difficulty (Easy, Medium, Hard)
- Press `SPACE` to start the game

### During Game
- **Mouse Controls:**
  - Click on a piece to select it
  - Click on a highlighted square to move the selected piece
  - Click on another piece of the same color to select it instead

- **Keyboard Controls:**
  - Press `R` to restart the current match (or click "Restart Game (R)" on the sidebar)
  - Press `B` to return to the main menu
  - Press `U` to undo the last move (or click "Undo Move (U)" on the sidebar)
  - Press `T` to cycle board themes

### Game Rules
- White always moves first
- In Player vs Computer mode, you play as White, computer plays as Black
- Green highlighting shows the selected piece
- Green dots show valid moves for the selected piece
- Game ends when a player has no valid moves

## File Structure

```
ChessGame/
├── chess_game.py          # Main game file
├── create_pieces.py       # Piece image generator
├── README.md             # This file
└── assets/               # Generated piece images
    ├── white_king.png
    ├── white_queen.png
    ├── white_rook.png
    ├── white_bishop.png
    ├── white_knight.png
    ├── white_pawn.png
    ├── black_king.png
    ├── black_queen.png
    ├── black_rook.png
    ├── black_bishop.png
    ├── black_knight.png
    └── black_pawn.png
```

## Chess Piece Movement Rules

- **Pawn:** Moves forward one square, captures diagonally, can move two squares on first move
- **Rook:** Moves horizontally and vertically any distance
- **Bishop:** Moves diagonally any distance
- **Knight:** Moves in an L-shape (2+1 squares)
- **Queen:** Combines rook and bishop movements
- **King:** Moves one square in any direction

## AI Behavior

- **Easy:** Makes random legal moves
- **Medium:** Prioritizes capturing opponent pieces when possible
- **Hard:** Full Minimax search with Alpha-Beta pruning (depth 3), driven by material values and Piece-Square Tables for positional evaluation

## Recent Enhancements

- **Save/Load Game**: Persist and resume matches as JSON files (`save_game()` / `load_game()`)
- **Minimax AI**: Hard AI uses recursive Minimax search with Alpha-Beta pruning and Piece-Square Tables
- **Visual Themes**: Four board themes selectable via `T` key (Classic Brown, Forest Green, Ocean Blue, Midnight Dark)
- **Game Timers**: Blitz (3m, 5m), Rapid (10m), and Infinite presets selectable via `C` key in menu
- **Undo Move**: Roll back moves with `U` key or sidebar button (2 plies in vs-computer mode)
- **Sound Effects**: Synthesized in-memory audio for moves, captures, checks, and game over

## Future Enhancements

Possible improvements that could be added:
- Network multiplayer

## Troubleshooting

**Game won't start:**
- Make sure Pygame is installed: `pip install pygame`
- Ensure you're running Python 3.6+

**Pieces appear as circles with letters:**
- Run `python create_pieces.py` to generate piece images
- Make sure the `assets` folder exists in the same directory

**Game runs slowly:**
- This is normal for the AI on hard difficulty
- Try using easy or medium difficulty for faster gameplay

Enjoy your chess game!

"# chessGame" 
"# Chess_Game" 
"# Chess_Game" 
