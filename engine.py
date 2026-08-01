from enum import Enum
import random

class PieceType(Enum):
    KING = "king"
    QUEEN = "queen"
    ROOK = "rook"
    BISHOP = "bishop"
    KNIGHT = "knight"
    PAWN = "pawn"

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

MATERIAL_VALUES = {
    PieceType.KING: 20000,
    PieceType.QUEEN: 900,
    PieceType.ROOK: 500,
    PieceType.BISHOP: 330,
    PieceType.KNIGHT: 320,
    PieceType.PAWN: 100
}

PAWN_PST = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_PST = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

BISHOP_PST = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

ROOK_PST = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
]

QUEEN_PST = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,  0,  5,  5,  5,  5,  0, -5],
    [0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  5,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

KING_PST = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
]

PST_MAP = {
    PieceType.PAWN: PAWN_PST,
    PieceType.KNIGHT: KNIGHT_PST,
    PieceType.BISHOP: BISHOP_PST,
    PieceType.ROOK: ROOK_PST,
    PieceType.QUEEN: QUEEN_PST,
    PieceType.KING: KING_PST
}

class Piece:
    def __init__(self, piece_type, color, row, col):
        self.type = piece_type
        self.color = color
        self.row = row
        self.col = col
        self.has_moved = False

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = Color.WHITE
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.in_check = False
        self.checkmate = False
        self.stalemate = False
        self.last_move = None  # For en passant
        self.move_history = []  # For castling and game history
        self.move_count = 0  # For fifty-move rule
        self.position_history = []  # For threefold repetition
        self.move_states = []  # For move navigation
        self.current_move_index = -1  # For move navigation
        self.setup_board()
    
    def setup_board(self):
        """Initialize the chess board with pieces"""
        # Place pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK, 1, col)
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE, 6, col)
        
        # Place other pieces
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                      PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
        
        for col in range(8):
            self.board[0][col] = Piece(piece_order[col], Color.BLACK, 0, col)
            self.board[7][col] = Piece(piece_order[col], Color.WHITE, 7, col)
    
    def get_piece(self, row, col):
        """Get piece at given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def move_piece(self, from_row, from_col, to_row, to_col):
        """Move piece from one position to another"""
        piece = self.board[from_row][from_col]
        if piece:
            piece.row = to_row
            piece.col = to_col
            piece.has_moved = True
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            return True
        return False
    
    def is_valid_move(self, piece, to_row, to_col):
        """Check if a move is valid for the given piece"""
        if not (0 <= to_row < 8 and 0 <= to_col < 8):
            return False
        
        target_piece = self.board[to_row][to_col]
        if target_piece and target_piece.color == piece.color:
            return False
        
        from_row, from_col = piece.row, piece.col
        
        if piece.type == PieceType.PAWN:
            return self.is_valid_pawn_move(piece, to_row, to_col)
        elif piece.type == PieceType.ROOK:
            return self.is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.BISHOP:
            return self.is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.QUEEN:
            return (self.is_valid_rook_move(from_row, from_col, to_row, to_col) or
                   self.is_valid_bishop_move(from_row, from_col, to_row, to_col))
        elif piece.type == PieceType.KING:
            return self.is_valid_king_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.KNIGHT:
            return self.is_valid_knight_move(from_row, from_col, to_row, to_col)
        
        return False
    
    def is_valid_pawn_move(self, piece, to_row, to_col):
        """Check if pawn move is valid"""
        from_row, from_col = piece.row, piece.col
        direction = -1 if piece.color == Color.WHITE else 1
        
        # Forward move
        if from_col == to_col:
            if to_row == from_row + direction and not self.board[to_row][to_col]:
                return True
            # Two squares forward from starting position
            if (not piece.has_moved and to_row == from_row + 2 * direction and 
                not self.board[to_row][to_col] and not self.board[from_row + direction][from_col]):
                return True
        
        # Diagonal capture
        elif abs(from_col - to_col) == 1 and to_row == from_row + direction:
            target_piece = self.board[to_row][to_col]
            if target_piece and target_piece.color != piece.color:
                return True
        
        return False
    
    def is_valid_rook_move(self, from_row, from_col, to_row, to_col):
        """Check if rook move is valid"""
        if from_row != to_row and from_col != to_col:
            return False
        
        # Check path is clear
        if from_row == to_row:
            start, end = min(from_col, to_col), max(from_col, to_col)
            for col in range(start + 1, end):
                if self.board[from_row][col]:
                    return False
        else:
            start, end = min(from_row, to_row), max(from_row, to_row)
            for row in range(start + 1, end):
                if self.board[row][from_col]:
                    return False
        
        return True
    
    def is_valid_bishop_move(self, from_row, from_col, to_row, to_col):
        """Check if bishop move is valid"""
        if abs(from_row - to_row) != abs(from_col - to_col):
            return False
        
        # Check path is clear
        row_step = 1 if to_row > from_row else -1
        col_step = 1 if to_col > from_col else -1
        
        row, col = from_row + row_step, from_col + col_step
        while row != to_row and col != to_col:
            if self.board[row][col]:
                return False
            row += row_step
            col += col_step
        
        return True
    
    def is_valid_king_move(self, from_row, from_col, to_row, to_col):
        """Check if king move is valid"""
        return abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1
    
    def is_valid_knight_move(self, from_row, from_col, to_row, to_col):
        """Check if knight move is valid"""
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def get_valid_moves(self, piece):
        """Get all valid moves for a piece that don't put own king in check"""
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(piece, row, col):
                    # Check if this move would put own king in check
                    if not self.would_be_in_check_after_move(piece, row, col):
                        valid_moves.append((row, col))
        
        # Add castling moves for king
        if piece.type == PieceType.KING and not piece.has_moved:
            castling_moves = self.get_castling_moves(piece)
            valid_moves.extend(castling_moves)
        
        # Add en passant moves for pawns
        if piece.type == PieceType.PAWN:
            en_passant_moves = self.get_en_passant_moves(piece)
            valid_moves.extend(en_passant_moves)
        
        return valid_moves
    
    def would_be_in_check_after_move(self, piece, to_row, to_col):
        """Check if moving a piece would put own king in check"""
        # Save original state
        from_row, from_col = piece.row, piece.col
        captured_piece = self.board[to_row][to_col]
        
        # Make temporary move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.row, piece.col = to_row, to_col
        
        # Check if king is in check
        in_check = self.is_in_check(piece.color)
        
        # Restore original state
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured_piece
        piece.row, piece.col = from_row, from_col
        
        return in_check
    
    def get_castling_moves(self, king):
        """Get valid castling moves for the king"""
        moves = []
        if king.has_moved or self.is_in_check(king.color):
            return moves
            
        # Check kingside castling
        if not self.board[king.row][5] and not self.board[king.row][6]:
            rook = self.board[king.row][7]
            if rook and rook.type == PieceType.ROOK and not rook.has_moved:
                if not any(self.would_square_be_attacked(king.row, col, king.color) 
                          for col in range(4, 7)):
                    moves.append((king.row, 6))
                    
        # Check queenside castling
        if not self.board[king.row][1] and not self.board[king.row][2] and not self.board[king.row][3]:
            rook = self.board[king.row][0]
            if rook and rook.type == PieceType.ROOK and not rook.has_moved:
                if not any(self.would_square_be_attacked(king.row, col, king.color) 
                          for col in range(2, 5)):
                    moves.append((king.row, 2))
                    
        return moves
    
    def would_square_be_attacked(self, row, col, defending_color):
        """Check if a square would be attacked by the opponent"""
        opponent_color = Color.BLACK if defending_color == Color.WHITE else Color.WHITE
        
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == opponent_color:
                    if self.is_valid_move(piece, row, col):
                        return True
        return False
    
    def get_en_passant_moves(self, pawn):
        """Get valid en passant moves for a pawn"""
        moves = []
        if not self.last_move:
            return moves
            
        last_piece, last_from, last_to = self.last_move
        if last_piece.type != PieceType.PAWN:
            return moves
            
        # Check if last move was a two-square pawn move
        if abs(last_to[0] - last_from[0]) == 2:
            # Check if this pawn is adjacent to the last moved pawn
            if abs(pawn.col - last_to[1]) == 1 and pawn.row == last_to[0]:
                direction = -1 if pawn.color == Color.WHITE else 1
                moves.append((last_to[0] + direction, last_to[1]))
        
        return moves
    
    def get_algebraic_coord(self, row, col):
        """Convert (row, col) to algebraic notation (e.g., (6, 4) -> 'e2')"""
        col_char = chr(ord('a') + col)
        row_char = str(8 - row)
        return col_char + row_char

    def execute_move(self, from_row, from_col, to_row, to_col):
        """Execute a move with all special rules.
        Returns (True, "promotion") if a pawn reaches the end, (True, "normal") otherwise, or (False, "error")
        """
        # Save state before move
        self.move_states = self.move_states[:self.current_move_index + 1]
        self.move_states.append(self.save_board_state())
        self.current_move_index = len(self.move_states) - 1

        piece = self.board[from_row][from_col]
        if not piece:
            return False, "error"

        # Record move in algebraic notation
        move_notation = f"{self.get_algebraic_coord(from_row, from_col)}{self.get_algebraic_coord(to_row, to_col)}"
        self.move_history.append(move_notation)

        # Save move for en passant
        self.last_move = (piece, (from_row, from_col), (to_row, to_col))

        # Handle castling
        if piece.type == PieceType.KING and abs(from_col - to_col) == 2:
            # Determine rook's position and new position
            rook_col = 0 if to_col < from_col else 7
            new_rook_col = 3 if to_col < from_col else 5
            rook = self.board[from_row][rook_col]

            # Move rook
            self.board[from_row][new_rook_col] = rook
            self.board[from_row][rook_col] = None
            if rook:
                rook.col = new_rook_col
                rook.has_moved = True

        # Handle en passant capture
        if piece.type == PieceType.PAWN and abs(from_col - to_col) == 1 and not self.board[to_row][to_col]:
            captured_pawn_row = from_row
            self.board[captured_pawn_row][to_col] = None

        # Handle pawn promotion detection
        if piece.type == PieceType.PAWN and (to_row == 0 or to_row == 7):
            # Move the pawn first, but don't promote yet
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            piece.row = to_row
            piece.col = to_col
            piece.has_moved = True
            return True, "promotion"
        else:
            # Regular move
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            piece.row = to_row
            piece.col = to_col
            piece.has_moved = True

        # Update move count for fifty-move rule
        if piece.type == PieceType.PAWN or self.board[to_row][to_col]:
            self.move_count = 0
        else:
            self.move_count += 1

        # Update position history for threefold repetition
        self.position_history.append(self.get_board_state())

        # Switch player
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE

        # Check for check, checkmate, and stalemate
        self.in_check = self.is_in_check(self.current_player)
        if self.in_check:
            if self.is_checkmate(self.current_player):
                self.checkmate = True
                self.game_over = True
                self.winner = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        elif self.is_stalemate(self.current_player):
            self.stalemate = True
            self.game_over = True

        # Check for draw conditions
        if self.check_threefold_repetition() or self.check_fifty_move_rule() or self.check_insufficient_material():
            self.game_over = True
            self.stalemate = True

        return True, "normal"

    def complete_promotion(self, row, col, piece_type):
        """Finalize pawn promotion and switch turns"""
        piece = Piece(piece_type, self.board[row][col].color, row, col)
        self.board[row][col] = piece

        # Switch player
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE

        # Check for game states
        self.in_check = self.is_in_check(self.current_player)
        if self.in_check:
            if self.is_checkmate(self.current_player):
                self.checkmate = True
                self.game_over = True
                self.winner = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        elif self.is_stalemate(self.current_player):
            self.stalemate = True
            self.game_over = True

        return True
    
    def is_checkmate(self, color):
        """Check if the given color is in checkmate"""
        if not self.is_in_check(color):
            return False
        
        # Check if any move can get out of check
        pieces = self.get_all_pieces(color)
        for piece in pieces:
            valid_moves = self.get_valid_moves(piece)
            if valid_moves:
                return False
        
        return True
    
    def is_stalemate(self, color):
        """Check if the given color is in stalemate"""
        if self.is_in_check(color):
            return False
        
        # Check if any legal moves available
        pieces = self.get_all_pieces(color)
        for piece in pieces:
            valid_moves = self.get_valid_moves(piece)
            if valid_moves:
                return False
        
        return True
    
    def is_in_check(self, color):
        """Check if the king of given color is in check"""
        # Find the king
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.type == PieceType.KING and piece.color == color:
                    king_pos = (row, col)
                    break
        
        if not king_pos:
            return False
        
        # Check if any opponent piece can attack the king
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    if self.is_valid_move(piece, king_pos[0], king_pos[1]):
                        return True
        
        return False
    
    def get_all_pieces(self, color):
        """Get all pieces of a given color"""
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    pieces.append(piece)
        return pieces

    def get_board_state(self):
        """Get current board state for threefold repetition"""
        state = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    state.append(f"{piece.color.value}_{piece.type.value}_{row}_{col}")
        return tuple(sorted(state))

    def check_threefold_repetition(self):
        """Check for threefold repetition"""
        current_state = self.get_board_state()
        count = 1
        for state in reversed(self.position_history):
            if state == current_state:
                count += 1
            if count >= 3:
                return True
        return False

    def check_fifty_move_rule(self):
        """Check for fifty-move rule"""
        return self.move_count >= 50

    def check_insufficient_material(self):
        """Check for insufficient material to checkmate"""
        white_pieces = self.get_all_pieces(Color.WHITE)
        black_pieces = self.get_all_pieces(Color.BLACK)
        
        # King vs King
        if len(white_pieces) == 1 and len(black_pieces) == 1:
            return True
            
        # King and Knight vs King
        if len(white_pieces) == 2 and len(black_pieces) == 1:
            if any(p.type == PieceType.KNIGHT for p in white_pieces):
                return True
        if len(black_pieces) == 2 and len(white_pieces) == 1:
            if any(p.type == PieceType.KNIGHT for p in black_pieces):
                return True
                
        # King and Bishop vs King
        if len(white_pieces) == 2 and len(black_pieces) == 1:
            if any(p.type == PieceType.BISHOP for p in white_pieces):
                return True
        if len(black_pieces) == 2 and len(white_pieces) == 1:
            if any(p.type == PieceType.BISHOP for p in black_pieces):
                return True
                
        return False

    def save_board_state(self):
        """Save current board state for move navigation"""
        state = {
            'board': [[None if piece is None else {
                'type': piece.type.value,
                'color': piece.color.value,
                'has_moved': piece.has_moved
            } for piece in row] for row in self.board],
            'current_player': self.current_player.value,
            'last_move': None if self.last_move is None else {
                'from': list(self.last_move[1]),
                'to': list(self.last_move[2])
            },
            'move_count': self.move_count,
            'in_check': self.in_check
        }
        return state

    def load_board_state(self, state):
        """Load a saved board state"""
        for row in range(8):
            for col in range(8):
                piece_data = state['board'][row][col]
                if piece_data is None:
                    self.board[row][col] = None
                else:
                    piece = Piece(PieceType(piece_data['type']), Color(piece_data['color']), row, col)
                    piece.has_moved = piece_data['has_moved']
                    self.board[row][col] = piece
        
        self.current_player = Color(state['current_player'])
        
        if state['last_move']:
            last_to = tuple(state['last_move']['to'])
            piece = self.board[last_to[0]][last_to[1]]
            self.last_move = (piece, tuple(state['last_move']['from']), last_to)
        else:
            self.last_move = None
            
        self.move_count = state['move_count']
        self.in_check = state['in_check']

    def save_game(self, filepath):
        """Save the entire game state to a JSON file"""
        import json
        game_data = {
            'board_state': self.save_board_state(),
            'move_history': self.move_history,
            'position_history': [list(state) for state in self.position_history],
            'move_states': self.move_states,
            'current_move_index': self.current_move_index,
            'game_over': self.game_over,
            'winner': self.winner.value if self.winner else None,
            'checkmate': self.checkmate,
            'stalemate': self.stalemate
        }
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving game to {filepath}: {e}")
            return False

    def load_game(self, filepath):
        """Load the entire game state from a JSON file"""
        import json
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            self.load_board_state(game_data['board_state'])
            self.move_history = game_data['move_history']
            self.position_history = [tuple(state) for state in game_data['position_history']]
            self.move_states = game_data['move_states']
            self.current_move_index = game_data['current_move_index']
            self.game_over = game_data['game_over']
            winner_str = game_data['winner']
            self.winner = Color(winner_str) if winner_str else None
            self.checkmate = game_data['checkmate']
            self.stalemate = game_data['stalemate']
            return True
        except Exception as e:
            print(f"Error loading game from {filepath}: {e}")
            return False

    def evaluate_board(self):
        """Evaluate the board state. Positive values favor Black, negative favor White."""
        score = 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None:
                    val = MATERIAL_VALUES.get(piece.type, 0)
                    pst = PST_MAP.get(piece.type)
                    pst_val = 0
                    if pst:
                        if piece.color == Color.WHITE:
                            pst_val = pst[r][c]
                            score -= (val + pst_val)
                        else:
                            pst_val = pst[7 - r][c]
                            score += (val + pst_val)
        return score

    def make_temp_move(self, piece, to_row, to_col):
        """Make a temporary move in the board for minimax search"""
        from_row, from_col = piece.row, piece.col
        captured = self.board[to_row][to_col]
        captured_state = None
        if captured:
            captured_state = (captured.row, captured.col, captured.has_moved)
            
        saved_state = (
            from_row, from_col, piece.has_moved,
            captured, captured_state,
            self.current_player, self.last_move, self.move_count,
            self.in_check, self.checkmate, self.stalemate, self.game_over
        )
        
        # Apply move on board matrix
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.row, piece.col = to_row, to_col
        piece.has_moved = True
        
        # Handle castling (rook movement)
        rook_move = None
        if piece.type == PieceType.KING and abs(from_col - to_col) == 2:
            rook_col = 0 if to_col < from_col else 7
            new_rook_col = 3 if to_col < from_col else 5
            rook = self.board[from_row][rook_col]
            if rook:
                self.board[from_row][new_rook_col] = rook
                self.board[from_row][rook_col] = None
                rook_move = (rook, rook_col, new_rook_col, rook.has_moved)
                rook.col = new_rook_col
                rook.has_moved = True
                
        # Handle en passant capture
        en_passant_capture = None
        if piece.type == PieceType.PAWN and abs(from_col - to_col) == 1 and not captured:
            ep_pawn = self.board[from_row][to_col]
            if ep_pawn:
                en_passant_capture = (ep_pawn, from_row, to_col)
                self.board[from_row][to_col] = None
                
        # Handle promotion to Queen in simulation
        promoted_type = None
        if piece.type == PieceType.PAWN and (to_row == 0 or to_row == 7):
            promoted_type = piece.type
            piece.type = PieceType.QUEEN
            
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        self.in_check = self.is_in_check(self.current_player)
        
        # Update last move representation for en passant
        self.last_move = (piece, (from_row, from_col), (to_row, to_col))
        
        return saved_state, rook_move, en_passant_capture, promoted_type

    def undo_temp_move(self, piece, saved_state, rook_move, en_passant_capture, promoted_type):
        """Restore board state after temporary move simulation"""
        (
            from_row, from_col, piece_has_moved,
            captured, captured_state,
            self.current_player, self.last_move, self.move_count,
            self.in_check, self.checkmate, self.stalemate, self.game_over
        ) = saved_state
        
        # Restore piece
        to_row, to_col = piece.row, piece.col
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured
        piece.row, piece.col = from_row, from_col
        piece.has_moved = piece_has_moved
        
        # Restore captured piece properties
        if captured and captured_state:
            captured.row, captured.col, captured.has_moved = captured_state
            
        # Restore castling rook
        if rook_move:
            rook, rook_col, new_rook_col, rook_has_moved = rook_move
            self.board[from_row][rook_col] = rook
            self.board[from_row][new_rook_col] = None
            rook.col = rook_col
            rook.has_moved = rook_has_moved
            
        # Restore en passant captured pawn
        if en_passant_capture:
            ep_pawn, ep_row, ep_col = en_passant_capture
            self.board[ep_row][ep_col] = ep_pawn
            
        # Restore promotion
        if promoted_type:
            piece.type = promoted_type

    def minimax(self, depth, alpha, beta, maximizing_player):
        """Minimax with Alpha-Beta pruning recursive search"""
        if depth == 0 or self.game_over:
            return self.evaluate_board()
            
        turn_color = Color.BLACK if maximizing_player else Color.WHITE
        pieces = self.get_all_pieces(turn_color)
        valid_moves = []
        for piece in pieces:
            moves = self.get_valid_moves(piece)
            for move in moves:
                valid_moves.append((piece, move))
                
        if not valid_moves:
            if self.is_in_check(turn_color):
                return -99999 + depth if maximizing_player else 99999 - depth
            else:
                return 0
                
        # Sort moves for optimal alpha-beta pruning
        def move_priority(item):
            p, (r, c) = item
            target = self.board[r][c]
            return 10 + (MATERIAL_VALUES.get(target.type, 0) - MATERIAL_VALUES.get(p.type, 0) / 100) if target else 0
            
        valid_moves.sort(key=move_priority, reverse=True)
        
        if maximizing_player:
            max_eval = -9999999
            for piece, (to_row, to_col) in valid_moves:
                saved, rook, ep, prom = self.make_temp_move(piece, to_row, to_col)
                evaluation = self.minimax(depth - 1, alpha, beta, False)
                self.undo_temp_move(piece, saved, rook, ep, prom)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 9999999
            for piece, (to_row, to_col) in valid_moves:
                saved, rook, ep, prom = self.make_temp_move(piece, to_row, to_col)
                evaluation = self.minimax(depth - 1, alpha, beta, True)
                self.undo_temp_move(piece, saved, rook, ep, prom)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval


class ChessAI:
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
    
    def get_move(self, board):
        """Get AI move based on difficulty"""
        pieces = board.get_all_pieces(Color.BLACK)
        valid_moves = []
        
        for piece in pieces:
            moves = board.get_valid_moves(piece)
            for move in moves:
                valid_moves.append((piece, move))
        
        if not valid_moves:
            return None
        
        if self.difficulty == "easy":
            return random.choice(valid_moves)
        elif self.difficulty == "medium":
            return self.get_medium_move(board, valid_moves)
        else:
            return self.get_hard_move(board, valid_moves)
    
    def get_medium_move(self, board, valid_moves):
        """Medium difficulty AI - prefer captures"""
        capture_moves = []
        for piece, (to_row, to_col) in valid_moves:
            if board.board[to_row][to_col]:  # There's a piece to capture
                capture_moves.append((piece, (to_row, to_col)))
        
        if capture_moves:
            return random.choice(capture_moves)
        return random.choice(valid_moves)
    
    def get_hard_move(self, board, valid_moves):
        """Hard difficulty AI - search based using Minimax and Alpha-Beta pruning"""
        best_score = -9999999
        best_moves = []
        
        alpha = -9999999
        beta = 9999999
        
        # Sort moves for better pruning
        def move_priority(item):
            p, (r, c) = item
            target = board.board[r][c]
            return 10 + (MATERIAL_VALUES.get(target.type, 0) - MATERIAL_VALUES.get(p.type, 0) / 100) if target else 0
            
        valid_moves.sort(key=move_priority, reverse=True)
        
        for piece, (to_row, to_col) in valid_moves:
            # Simulate
            saved, rook, ep, prom = board.make_temp_move(piece, to_row, to_col)
            
            # Evaluate move (depth = 2 since root move is already applied)
            score = board.minimax(2, alpha, beta, False)
            
            # Restore
            board.undo_temp_move(piece, saved, rook, ep, prom)
            
            if score > best_score:
                best_score = score
                best_moves = [(piece, (to_row, to_col))]
            elif score == best_score:
                best_moves.append((piece, (to_row, to_col)))
                
            alpha = max(alpha, best_score)
            
        if best_moves:
            return random.choice(best_moves)
        return random.choice(valid_moves)
