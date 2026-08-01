import pytest
import os
import tempfile
from engine import ChessBoard, Piece, PieceType, Color, ChessAI

def clear_board(board):
    board.board = [[None for _ in range(8)] for _ in range(8)]

def test_initial_board_setup():
    board = ChessBoard()
    # Check white pawns
    for col in range(8):
        assert board.board[6][col] is not None
        assert board.board[6][col].type == PieceType.PAWN
        assert board.board[6][col].color == Color.WHITE
        
    # Check black pawns
    for col in range(8):
        assert board.board[1][col] is not None
        assert board.board[1][col].type == PieceType.PAWN
        assert board.board[1][col].color == Color.BLACK

    # Check back rows
    piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                  PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
    for col in range(8):
        assert board.board[7][col].type == piece_order[col]
        assert board.board[7][col].color == Color.WHITE
        assert board.board[0][col].type == piece_order[col]
        assert board.board[0][col].color == Color.BLACK

def test_pawn_movements():
    board = ChessBoard()
    pawn = board.board[6][0] # White pawn
    
    # 1. Forward 1 step is valid
    assert (5, 0) in board.get_valid_moves(pawn)
    # 2. Forward 2 steps (hasn't moved) is valid
    assert (4, 0) in board.get_valid_moves(pawn)
    # 3. Diagonal capture is invalid if empty
    assert (5, 1) not in board.get_valid_moves(pawn)

    # Place an enemy piece diagonally
    board.board[5][1] = Piece(PieceType.PAWN, Color.BLACK, 5, 1)
    assert (5, 1) in board.get_valid_moves(pawn)

    # Place a friendly piece forward to block
    board.board[5][0] = Piece(PieceType.PAWN, Color.WHITE, 5, 0)
    assert (5, 0) not in board.get_valid_moves(pawn)
    assert (4, 0) not in board.get_valid_moves(pawn) # Double step blocked too

def test_knight_movements():
    board = ChessBoard()
    knight = board.board[7][1] # White knight at b1
    
    # Can jump over pawns
    valid_moves = board.get_valid_moves(knight)
    assert (5, 2) in valid_moves
    assert (5, 0) in valid_moves
    
    # Place friendly piece on landing square
    board.board[5][2] = Piece(PieceType.PAWN, Color.WHITE, 5, 2)
    assert (5, 2) not in board.get_valid_moves(knight)

def test_bishop_movements():
    board = ChessBoard()
    clear_board(board)
    bishop = Piece(PieceType.BISHOP, Color.WHITE, 4, 4)
    board.board[4][4] = bishop
    
    valid_moves = board.get_valid_moves(bishop)
    assert (2, 2) in valid_moves
    assert (6, 6) in valid_moves
    assert (2, 6) in valid_moves
    assert (6, 2) in valid_moves
    assert (4, 5) not in valid_moves # No straight moves
    
    # Block path
    board.board[2][2] = Piece(PieceType.PAWN, Color.WHITE, 2, 2)
    valid_moves = board.get_valid_moves(bishop)
    assert (2, 2) not in valid_moves
    assert (1, 1) not in valid_moves # Blocked behind

def test_rook_movements():
    board = ChessBoard()
    clear_board(board)
    rook = Piece(PieceType.ROOK, Color.WHITE, 4, 4)
    board.board[4][4] = rook
    
    valid_moves = board.get_valid_moves(rook)
    assert (4, 0) in valid_moves
    assert (4, 7) in valid_moves
    assert (0, 4) in valid_moves
    assert (7, 4) in valid_moves
    assert (3, 3) not in valid_moves # No diagonal moves
    
    # Capture enemy
    board.board[4][6] = Piece(PieceType.PAWN, Color.BLACK, 4, 6)
    valid_moves = board.get_valid_moves(rook)
    assert (4, 6) in valid_moves
    assert (4, 7) not in valid_moves # Blocked behind enemy

def test_queen_movements():
    board = ChessBoard()
    clear_board(board)
    queen = Piece(PieceType.QUEEN, Color.WHITE, 4, 4)
    board.board[4][4] = queen
    
    valid_moves = board.get_valid_moves(queen)
    assert (4, 0) in valid_moves # Rook move
    assert (2, 2) in valid_moves # Bishop move

def test_king_movements_standard():
    board = ChessBoard()
    clear_board(board)
    king = Piece(PieceType.KING, Color.WHITE, 4, 4)
    board.board[4][4] = king
    
    valid_moves = board.get_valid_moves(king)
    assert (4, 5) in valid_moves
    assert (3, 3) in valid_moves
    assert (2, 2) not in valid_moves # Out of range

def test_castling_kingside_and_queenside():
    board = ChessBoard()
    # Clear pieces between king and rooks
    board.board[7][1] = None # Knight
    board.board[7][2] = None # Bishop
    board.board[7][3] = None # Queen
    board.board[7][5] = None # Bishop
    board.board[7][6] = None # Knight
    
    king = board.board[7][4]
    
    # Castling moves should be available
    valid_moves = board.get_valid_moves(king)
    assert (7, 6) in valid_moves # Kingside
    assert (7, 2) in valid_moves # Queenside
    
    # Check that castling fails if king has moved
    king.has_moved = True
    assert (7, 6) not in board.get_valid_moves(king)
    assert (7, 2) not in board.get_valid_moves(king)

def test_en_passant():
    board = ChessBoard()
    # Move white pawn to 5th rank
    board.execute_move(6, 4, 4, 4) # White pawn e2 -> e4
    # Wait, execute_move switches turn. Since turn switched to Black, let's make a Black move.
    board.execute_move(1, 0, 2, 0) # Black pawn a7 -> a6
    # White moves pawn again to 5th rank
    board.execute_move(4, 4, 3, 4) # White pawn e4 -> e5
    
    # Black moves adjacent pawn double step
    board.execute_move(1, 5, 3, 5) # Black pawn f7 -> f5
    
    # Now white pawn at (3, 4) should have en passant option at (2, 5)
    white_pawn = board.board[3][4]
    assert (2, 5) in board.get_valid_moves(white_pawn)
    
    # Execute en passant capture
    success, _ = board.execute_move(3, 4, 2, 5)
    assert success is True
    # The black pawn on f5 (3, 5) should be captured
    assert board.board[3][5] is None
    assert board.board[2][5] == white_pawn

def test_pawn_promotion():
    board = ChessBoard()
    clear_board(board)
    
    # Place white pawn near 8th rank
    pawn = Piece(PieceType.PAWN, Color.WHITE, 1, 4)
    board.board[1][4] = pawn
    
    # Execute promotion step
    success, status = board.execute_move(1, 4, 0, 4)
    assert success is True
    assert status == "promotion"
    
    # Finalize promotion to Queen
    board.complete_promotion(0, 4, PieceType.QUEEN)
    assert board.board[0][4] is not None
    assert board.board[0][4].type == PieceType.QUEEN
    assert board.board[0][4].color == Color.WHITE

def test_check_and_checkmate():
    board = ChessBoard()
    clear_board(board)
    
    # Place White King and Black Rook in check alignment
    white_king = Piece(PieceType.KING, Color.WHITE, 7, 4)
    board.board[7][4] = white_king
    black_rook = Piece(PieceType.ROOK, Color.BLACK, 0, 4)
    board.board[0][4] = black_rook
    
    # Verify in_check
    board.in_check = board.is_in_check(Color.WHITE)
    assert board.in_check is True
    
    # Checkmate is false because King can move out of rook's line
    assert board.is_checkmate(Color.WHITE) is False
    
    # Trap the king with other pieces to trigger checkmate
    board.board[7][3] = Piece(PieceType.PAWN, Color.WHITE, 7, 3) # block left
    board.board[7][5] = Piece(PieceType.PAWN, Color.WHITE, 7, 5) # block right
    board.board[6][3] = Piece(PieceType.PAWN, Color.WHITE, 6, 3) # block diagonal left
    board.board[6][5] = Piece(PieceType.PAWN, Color.WHITE, 6, 5) # block diagonal right
    
    # Now the King has no valid escape squares
    assert board.is_checkmate(Color.WHITE) is True

def test_stalemate():
    board = ChessBoard()
    clear_board(board)
    
    # Classic stalemate setup (King in corner, Queen blocking all moves)
    board.board[0][0] = Piece(PieceType.KING, Color.BLACK, 0, 0)
    board.board[1][2] = Piece(PieceType.QUEEN, Color.WHITE, 1, 2)
    board.board[7][7] = Piece(PieceType.KING, Color.WHITE, 7, 7)
    
    assert board.is_in_check(Color.BLACK) is False
    assert board.is_stalemate(Color.BLACK) is True

def test_draw_conditions():
    board = ChessBoard()
    
    # 1. Insufficient material: King vs King
    clear_board(board)
    board.board[0][0] = Piece(PieceType.KING, Color.BLACK, 0, 0)
    board.board[7][7] = Piece(PieceType.KING, Color.WHITE, 7, 7)
    assert board.check_insufficient_material() is True

    # 2. Insufficient material: King and Knight vs King
    board.board[6][6] = Piece(PieceType.KNIGHT, Color.WHITE, 6, 6)
    assert board.check_insufficient_material() is True

    # 3. Fifty move rule
    board.move_count = 50
    assert board.check_fifty_move_rule() is True

def test_ai_move_generation():
    board = ChessBoard()
    # Test easy, medium and hard AIs select moves successfully
    for difficulty in ["easy", "medium", "hard"]:
        ai = ChessAI(difficulty=difficulty)
        move = ai.get_move(board)
        assert move is not None
        piece, to_pos = move
        assert piece.color == Color.BLACK
        assert to_pos in board.get_valid_moves(piece)

def test_json_persistence():
    board = ChessBoard()
    
    # Make a move
    board.execute_move(6, 4, 4, 4)
    original_state = board.save_board_state()
    
    # Save match to temp file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".json")
    try:
        os.close(temp_fd)
        assert board.save_game(temp_path) is True
        
        # Create a new board and load state
        new_board = ChessBoard()
        assert new_board.load_game(temp_path) is True
        
        # Verify identical state keys
        assert new_board.current_player == board.current_player
        assert new_board.move_count == board.move_count
        assert new_board.in_check == board.in_check
        assert new_board.game_over == board.game_over
        
        # Compare visual board states
        loaded_state = new_board.save_board_state()
        assert loaded_state == original_state
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_positional_evaluation():
    board = ChessBoard()
    # Initial setup is symmetric, so evaluate_board should return 0
    assert board.evaluate_board() == 0
    
    # Place a black pawn in the center (rewards positional PST value)
    clear_board(board)
    board.board[3][3] = Piece(PieceType.PAWN, Color.BLACK, 3, 3)
    # Material is Black (100) + PST at (3,3) which is mirrored (row 7-3 = 4, col 3) -> 20. Total = 120.
    # White material is 0. So score should be 120.
    assert board.evaluate_board() == 120

def test_minimax_capture_preference():
    board = ChessBoard()
    clear_board(board)
    
    # White King and Black King far away
    board.board[7][7] = Piece(PieceType.KING, Color.WHITE, 7, 7)
    board.board[0][0] = Piece(PieceType.KING, Color.BLACK, 0, 0)
    
    # Black Rook can capture either a White Queen or a White Pawn
    board.board[3][3] = Piece(PieceType.ROOK, Color.BLACK, 3, 3)
    board.board[3][5] = Piece(PieceType.QUEEN, Color.WHITE, 3, 5) # White Queen
    board.board[5][3] = Piece(PieceType.PAWN, Color.WHITE, 5, 3) # White Pawn
    
    ai = ChessAI(difficulty="hard")
    move = ai.get_move(board)
    assert move is not None
    piece, to_pos = move
    # Rook should capture the Queen at (3, 5)
    assert piece.type == PieceType.ROOK
    assert to_pos == (3, 5)

def test_minimax_checkmate_avoidance():
    board = ChessBoard()
    clear_board(board)
    
    # Place Black King in a corner
    board.board[0][0] = Piece(PieceType.KING, Color.BLACK, 0, 0)
    
    # White Queen is attacking (0, 0) from (1, 1). White Rook is protecting Queen.
    # If Black does not capture the Queen, it is checkmate next move.
    board.board[1][1] = Piece(PieceType.QUEEN, Color.WHITE, 1, 1)
    board.board[2][1] = Piece(PieceType.ROOK, Color.WHITE, 2, 1)
    
    # Black has a Rook at (1, 7) that can capture the Queen at (1, 1)
    board.board[1][7] = Piece(PieceType.ROOK, Color.BLACK, 1, 7)
    
    # Verify that Black AI captures the Queen to avoid checkmate
    ai = ChessAI(difficulty="hard")
    move = ai.get_move(board)
    assert move is not None
    piece, to_pos = move
    assert piece.type == PieceType.ROOK
    assert to_pos == (1, 1)
