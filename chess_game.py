import pygame
import sys
import os
from enum import Enum
import random
import asyncio
from engine import PieceType, Color, Piece, ChessBoard, ChessAI

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 1024
HEIGHT = 680
BOARD_SIZE = 512
SQUARE_SIZE = BOARD_SIZE // 8
BOARD_X = 60
BOARD_Y = (HEIGHT - BOARD_SIZE) // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (16, 185, 129)
RED = (239, 68, 68)
BLUE = (59, 130, 246)
GRAY = (156, 163, 175)

class GameMode(Enum):
    TWO_PLAYER = "two_player"
    VS_COMPUTER = "vs_computer"

THEMES = [
    {"name": "Classic Brown", "light": (240, 217, 181), "dark": (181, 136, 99)},
    {"name": "Forest Green", "light": (235, 236, 208), "dark": (119, 149, 86)},
    {"name": "Ocean Blue", "light": (220, 230, 242), "dark": (74, 121, 181)},
    {"name": "Midnight Dark", "light": (180, 180, 180), "dark": (80, 80, 80)}
]

TIME_LIMITS = [
    {"name": "3 minutes (Blitz)", "val": 180},
    {"name": "5 minutes (Blitz)", "val": 300},
    {"name": "10 minutes (Rapid)", "val": 600},
    {"name": "Infinite (No Timer)", "val": float('inf')}
]

def draw_alpha_rect(surface, color, rect, border_radius=0):
    """Draw a rectangle with alpha channel (transparency) support and optional rounded corners"""
    shape_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, pygame.Rect(0, 0, rect.width, rect.height), border_radius=border_radius)
    surface.blit(shape_surf, (rect.x, rect.y))

def draw_button(screen, rect, text, font, bg_color, hover_color, text_color, is_hovered, border_color=None, border_width=1):
    """Draw a styled modern button with rounded corners and hover effect"""
    color = hover_color if is_hovered else bg_color
    pygame.draw.rect(screen, color, rect, border_radius=8)
    if border_color:
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)
    
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.sounds = {
                "move": self.create_move_sound(),
                "capture": self.create_capture_sound(),
                "check": self.create_check_sound(),
                "game_over": self.create_game_over_sound()
            }
        except Exception as e:
            print(f"Sound system error: {e}")
            self.sounds = {}

    def generate_sound(self, frequency_func, duration, volume=0.3):
        import io
        import wave
        import math
        import struct
        
        sample_rate = 22050
        num_samples = int(duration * sample_rate)
        
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            
            for i in range(num_samples):
                t = i / sample_rate
                freq = frequency_func(t)
                
                # Fade out to avoid clicking
                fade = 1.0
                if i > num_samples - 400:
                    fade = (num_samples - i) / 400.0
                    
                val = int(volume * fade * 32767.0 * math.sin(2.0 * math.pi * freq * t))
                wav.writeframesraw(struct.pack('<h', val))
                
        wav_buffer.seek(0)
        return pygame.mixer.Sound(wav_buffer)

    def create_move_sound(self):
        # Short simple beep (440Hz, 0.08s)
        return self.generate_sound(lambda t: 440.0, 0.08)

    def create_capture_sound(self):
        # Frequency sweep down (600Hz down to 200Hz, 0.12s)
        return self.generate_sound(lambda t: 600.0 - 400.0 * (t / 0.12), 0.12)

    def create_check_sound(self):
        # High pitched double alert beep (880Hz, 0.18s)
        return self.generate_sound(lambda t: 880.0, 0.18)

    def create_game_over_sound(self):
        # Sweeping arpeggio note (400Hz down to 150Hz, 0.5s)
        return self.generate_sound(lambda t: 400.0 - 250.0 * (t / 0.5), 0.5)

    def play(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = ChessBoard()
        self.game_mode = None
        self.ai = None
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.show_move_history = False
        self.sound_manager = SoundManager()
        self.current_theme_index = 0
        self.current_time_limit_index = 2 # default 10 minutes
        self.ai_difficulties = ["easy", "medium", "hard"]
        self.current_difficulty_index = 2 # default Hard
        self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
        self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
        self.promotion_pending = False
        self.pending_promotion_pos = None
        self.load_piece_images()
        
    def load_piece_images(self):
        """Load and scale piece images from assets, or create fallbacks"""
        self.piece_images = {}
        for color in Color:
            for piece_type in PieceType:
                filename = f"{color.value}_{piece_type.value}.png"
                image_path = os.path.join("assets", filename)
                if os.path.exists(image_path):
                    try:
                        img = pygame.image.load(image_path)
                        img = pygame.transform.scale(img, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
                        self.piece_images[(color, piece_type)] = img
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
                        self.piece_images[(color, piece_type)] = self.create_fallback_image(color, piece_type)
                else:
                    self.piece_images[(color, piece_type)] = self.create_fallback_image(color, piece_type)

    def create_fallback_image(self, color, piece_type):
        """Create a simple representation surface for a piece as a fallback"""
        surface = pygame.Surface((SQUARE_SIZE - 10, SQUARE_SIZE - 10))
        bg_color = (255, 255, 255) if color == Color.WHITE else (0, 0, 0)
        pygame.draw.circle(surface, bg_color, (SQUARE_SIZE//2 - 5, SQUARE_SIZE//2 - 5), 20)
        font = pygame.font.Font(None, 24)
        text = font.render(piece_type.value[0].upper(), True, (255, 0, 0))
        surface.blit(text, (SQUARE_SIZE//2 - 10, SQUARE_SIZE//2 - 10))
        return surface
        
    def draw_menu(self):
        """Draw the main menu with a beautiful dark theme and styled cards"""
        # Fill deep dark charcoal background
        self.screen.fill((18, 22, 30))
        
        # Draw soft background decorative elements
        pygame.draw.circle(self.screen, (28, 33, 46), (100, 100), 200)
        pygame.draw.circle(self.screen, (28, 33, 46), (WIDTH - 100, HEIGHT - 100), 250)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw Title with shadow effect
        title_text = "CHESS AI ENHANCED"
        shadow = self.font.render(title_text, True, (15, 17, 23))
        self.screen.blit(shadow, shadow.get_rect(center=(WIDTH//2 + 2, 82)))
        title = self.font.render(title_text, True, (243, 244, 246))
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 80)))
        
        # Define card rectangles
        rect_pvp = pygame.Rect(302, 190, 420, 45)
        rect_ai = pygame.Rect(302, 245, 420, 45)
        rect_diff = pygame.Rect(302, 310, 420, 45)
        rect_time = pygame.Rect(302, 375, 420, 45)
        rect_theme = pygame.Rect(302, 440, 420, 45)
        rect_start = pygame.Rect(302, 520, 420, 55)
        
        # Card colors
        bg_card = (28, 33, 46)
        hover_card = (38, 45, 62)
        border_card = (45, 55, 72)
        text_color = (243, 244, 246)
        
        # Draw Buttons
        draw_button(self.screen, rect_pvp, "1. Start Two Player Mode (Local PvP)", self.small_font,
                    bg_card, hover_card, text_color, rect_pvp.collidepoint(mouse_pos), border_card)
                    
        draw_button(self.screen, rect_ai, "2. Start vs Computer (AI Mode)", self.small_font,
                    bg_card, hover_card, text_color, rect_ai.collidepoint(mouse_pos), border_card)
                    
        diff_text = f"Difficulty: {self.ai_difficulties[self.current_difficulty_index].capitalize()} (Press D)"
        draw_button(self.screen, rect_diff, diff_text, self.small_font,
                    bg_card, hover_card, text_color, rect_diff.collidepoint(mouse_pos), border_card)
                    
        time_text = f"Time Limit: {TIME_LIMITS[self.current_time_limit_index]['name']} (Press C)"
        draw_button(self.screen, rect_time, time_text, self.small_font,
                    bg_card, hover_card, text_color, rect_time.collidepoint(mouse_pos), border_card)
                    
        theme_text = f"Board Theme: {THEMES[self.current_theme_index]['name']} (Press T)"
        draw_button(self.screen, rect_theme, theme_text, self.small_font,
                    bg_card, hover_card, text_color, rect_theme.collidepoint(mouse_pos), border_card)
                    
        # Accent button for Quick Match
        draw_button(self.screen, rect_start, "START VS COMPUTER (SPACE)", self.small_font,
                    (99, 102, 241), (129, 140, 248), WHITE, rect_start.collidepoint(mouse_pos))
                    
        # Instructions
        instructions = self.small_font.render("Use mouse or keyboard keys to choose options and play", True, (156, 163, 175))
        inst_rect = instructions.get_rect(center=(WIDTH//2, HEIGHT - 35))
        self.screen.blit(instructions, inst_rect)
    
    def draw_board(self):
        """Draw the chess board using the active theme colors and clean indicators"""
        theme = THEMES[self.current_theme_index]
        
        # 1. Draw themed squares
        for row in range(8):
            for col in range(8):
                color = theme["light"] if (row + col) % 2 == 0 else theme["dark"]
                rect = pygame.Rect(BOARD_X + col * SQUARE_SIZE, BOARD_Y + row * SQUARE_SIZE, 
                                 SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                
        # 2. Highlight last move (soft amber tint)
        if self.board.last_move:
            _, from_pos, to_pos = self.board.last_move
            for pos in [from_pos, to_pos]:
                if pos:
                    fr, fc = pos
                    rect = pygame.Rect(BOARD_X + fc * SQUARE_SIZE, BOARD_Y + fr * SQUARE_SIZE, 
                                     SQUARE_SIZE, SQUARE_SIZE)
                    draw_alpha_rect(self.screen, (245, 158, 11, 80), rect)
                    
        # 3. Highlight selected square (soft indigo/blue tint)
        if self.board.selected_pos:
            sr, sc = self.board.selected_pos
            rect = pygame.Rect(BOARD_X + sc * SQUARE_SIZE, BOARD_Y + sr * SQUARE_SIZE, 
                             SQUARE_SIZE, SQUARE_SIZE)
            draw_alpha_rect(self.screen, (99, 102, 241, 100), rect)
            pygame.draw.rect(self.screen, (99, 102, 241), rect, 2)
            
        # 4. Highlight valid moves
        for row, col in self.board.valid_moves:
            cx = BOARD_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = BOARD_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
            
            is_capture = self.board.board[row][col] is not None
            if is_capture:
                rect = pygame.Rect(BOARD_X + col * SQUARE_SIZE, BOARD_Y + row * SQUARE_SIZE, 
                                 SQUARE_SIZE, SQUARE_SIZE)
                draw_alpha_rect(self.screen, (239, 68, 68, 50), rect)
                pygame.draw.rect(self.screen, (239, 68, 68), rect, 2)
            else:
                dot_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(dot_surf, (16, 185, 129, 180), (10, 10), 8)
                self.screen.blit(dot_surf, (cx - 10, cy - 10))
    
    def draw_pieces(self):
        """Draw all pieces on the board"""
        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if piece:
                    img = self.piece_images.get((piece.color, piece.type))
                    if img:
                        x = BOARD_X + col * SQUARE_SIZE + 5
                        y = BOARD_Y + row * SQUARE_SIZE + 5
                        self.screen.blit(img, (x, y))

    def draw_promotion_menu(self):
        """Draw a menu for selecting the promotion piece"""
        row, col = self.pending_promotion_pos
        cx = BOARD_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
        cy = BOARD_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2

        # Draw a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Promotion options
        options = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
        for i, opt in enumerate(options):
            rect = pygame.Rect(cx - 100 + i * 50, cy - 25, 50, 50)
            pygame.draw.rect(self.screen, WHITE, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)

            # Draw a simple representation of the piece
            text = self.small_font.render(opt.value[0].upper(), True, BLACK)
            self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))
    
    def draw_game_info(self):
        """Draw game information including current player, check status, and game over conditions"""
        # Get mouse position for hover highlights
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw sidebar container panel
        panel_rect = pygame.Rect(580, 30, 384, 620)
        pygame.draw.rect(self.screen, (28, 33, 46), panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (45, 55, 72), panel_rect, 2, border_radius=12)
        
        # Draw Title
        title_surf = self.font.render("CHESS ENHANCED", True, (243, 244, 246))
        self.screen.blit(title_surf, (600, 50))
        
        # Draw Mode Description
        if self.game_mode == GameMode.TWO_PLAYER:
            mode_desc = "Local Player vs Player"
        else:
            diff_name = self.ai_difficulties[self.current_difficulty_index].capitalize()
            mode_desc = f"VS Computer ({diff_name})"
        mode_surf = self.small_font.render(mode_desc, True, (156, 163, 175))
        self.screen.blit(mode_surf, (600, 82))
        
        # Draw Fifty-move rule count
        fifty_count = f"Fifty-Move Count: {self.board.move_count}/50"
        fifty_surf = self.small_font.render(fifty_count, True, (156, 163, 175))
        self.screen.blit(fifty_surf, (600, 105))

        # Draw Timers side-by-side
        w_card = pygame.Rect(600, 130, 160, 60)
        b_card = pygame.Rect(784, 130, 160, 60)
        
        # Highlight active turn with indigo border
        w_border = (99, 102, 241) if self.board.current_player == Color.WHITE and not self.board.game_over else (45, 55, 72)
        b_border = (99, 102, 241) if self.board.current_player == Color.BLACK and not self.board.game_over else (45, 55, 72)
        
        pygame.draw.rect(self.screen, (38, 45, 62), w_card, border_radius=8)
        pygame.draw.rect(self.screen, w_border, w_card, 2, border_radius=8)
        pygame.draw.rect(self.screen, (38, 45, 62), b_card, border_radius=8)
        pygame.draw.rect(self.screen, b_border, b_card, 2, border_radius=8)
        
        # Render White time
        if self.white_time == float('inf'):
            w_time_str = "∞"
        else:
            w_time_str = f"{int(self.white_time // 60)}:{(int(self.white_time % 60)):02d}"
        
        # Render Black time
        if self.black_time == float('inf'):
            b_time_str = "∞"
        else:
            b_time_str = f"{int(self.black_time // 60)}:{(int(self.black_time % 60)):02d}"
            
        w_label = self.small_font.render("White", True, (156, 163, 175))
        self.screen.blit(w_label, (612, 135))
        w_val = self.font.render(w_time_str, True, (243, 244, 246))
        self.screen.blit(w_val, (612, 155))
        
        b_label = self.small_font.render("Black", True, (156, 163, 175))
        self.screen.blit(b_label, (796, 135))
        b_val = self.font.render(b_time_str, True, (243, 244, 246))
        self.screen.blit(b_val, (796, 155))
        
        # Draw check or game over alert banners
        if self.board.game_over:
            alert_rect = pygame.Rect(600, 210, 344, 50)
            pygame.draw.rect(self.screen, (30, 58, 138), alert_rect, border_radius=6)
            
            if self.board.checkmate:
                game_over_text = f"Checkmate! {self.board.winner.value.capitalize()} wins!"
            elif self.board.stalemate:
                if self.board.check_threefold_repetition():
                    game_over_text = "Draw: Threefold repetition"
                elif self.board.check_fifty_move_rule():
                    game_over_text = "Draw: Fifty-move rule"
                elif self.board.check_insufficient_material():
                    game_over_text = "Draw: Insufficient material"
                else:
                    game_over_text = "Stalemate! Game is a draw!"
            else:
                game_over_text = "Game Over!"
                
            text_surf = self.small_font.render(game_over_text, True, (219, 234, 254))
            self.screen.blit(text_surf, text_surf.get_rect(center=alert_rect.center))
        elif self.board.in_check:
            alert_rect = pygame.Rect(600, 210, 344, 50)
            pygame.draw.rect(self.screen, (153, 27, 27), alert_rect, border_radius=6)
            check_text = f"{self.board.current_player.value.capitalize()} is in check!"
            text_surf = self.small_font.render(check_text, True, (254, 226, 226))
            self.screen.blit(text_surf, text_surf.get_rect(center=alert_rect.center))

        # Control button dimensions
        rect_undo = pygame.Rect(600, 275, 160, 40)
        rect_restart = pygame.Rect(784, 275, 160, 40)
        rect_prev = pygame.Rect(600, 325, 160, 40)
        rect_next = pygame.Rect(784, 325, 160, 40)
        rect_menu = pygame.Rect(600, 375, 344, 40)
        
        # Colors for buttons
        bg_btn = (38, 45, 62)
        hover_btn = (48, 57, 78)
        border_btn = (45, 55, 72)
        btn_text = (243, 244, 246)
        
        # Draw Buttons
        draw_button(self.screen, rect_undo, "Undo Move (U)", self.small_font,
                    bg_btn, hover_btn, btn_text, rect_undo.collidepoint(mouse_pos), border_btn)
                    
        draw_button(self.screen, rect_restart, "Restart Game (R)", self.small_font,
                    bg_btn, hover_btn, btn_text, rect_restart.collidepoint(mouse_pos), border_btn)
                    
        draw_button(self.screen, rect_prev, "Previous (<-)", self.small_font,
                    bg_btn, hover_btn, btn_text, rect_prev.collidepoint(mouse_pos), border_btn)
                    
        draw_button(self.screen, rect_next, "Next (->)", self.small_font,
                    bg_btn, hover_btn, btn_text, rect_next.collidepoint(mouse_pos), border_btn)
                    
        draw_button(self.screen, rect_menu, "Back to Menu (B)", self.small_font,
                    bg_btn, hover_btn, btn_text, rect_menu.collidepoint(mouse_pos), border_btn)

        # Move History Container
        hist_panel = pygame.Rect(600, 430, 344, 200)
        pygame.draw.rect(self.screen, (38, 45, 62), hist_panel, border_radius=8)
        pygame.draw.rect(self.screen, (45, 55, 72), hist_panel, 1, border_radius=8)
        
        hist_title = self.small_font.render("Move History", True, (156, 163, 175))
        self.screen.blit(hist_title, (615, 440))
        
        # Pair moves (White / Black)
        history = self.board.move_history
        pairs = []
        for i in range(0, len(history), 2):
            w = history[i]
            b = history[i+1] if i+1 < len(history) else ""
            pairs.append((i//2 + 1, w, b))
            
        # Draw the last 5 pairs
        latest_pairs = pairs[-5:]
        for idx, (move_num, w_move, b_move) in enumerate(latest_pairs):
            y_pos = 470 + idx * 24
            
            num_surf = self.small_font.render(f"{move_num}.", True, (156, 163, 175))
            self.screen.blit(num_surf, (620, y_pos))
            
            w_surf = self.small_font.render(w_move, True, (243, 244, 246))
            self.screen.blit(w_surf, (670, y_pos))
            
            if b_move:
                b_surf = self.small_font.render(b_move, True, (243, 244, 246))
                self.screen.blit(b_surf, (780, y_pos))

    def undo_move(self):
        """Roll back the board state permanently by 1 move (or 2 if playing AI)"""
        if len(self.board.move_states) <= 1:
            return
            
        steps = 2 if self.game_mode == GameMode.VS_COMPUTER else 1
        for _ in range(steps):
            if len(self.board.move_states) > 1:
                self.board.move_states.pop()
                self.board.move_history.pop()
                if self.board.position_history:
                    self.board.position_history.pop()
                
                last_state = self.board.move_states[-1]
                self.board.load_board_state(last_state)
                self.board.current_move_index = len(self.board.move_states) - 1
                
        # Re-initialize statuses
        self.board.game_over = False
        self.board.winner = None
        self.board.checkmate = False
        self.board.stalemate = False
        self.board.in_check = self.board.is_in_check(self.board.current_player)

    def restart_game(self):
        """Restart the current game match"""
        self.board = ChessBoard()
        self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
        self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
        self.promotion_pending = False
        self.pending_promotion_pos = None
        if self.game_mode == GameMode.VS_COMPUTER:
            self.ai = ChessAI("hard")
    
    def get_square_from_mouse(self, pos):
        """Convert mouse position to board coordinates"""
        x, y = pos
        if BOARD_X <= x < BOARD_X + BOARD_SIZE and BOARD_Y <= y < BOARD_Y + BOARD_SIZE:
            col = (x - BOARD_X) // SQUARE_SIZE
            row = (y - BOARD_Y) // SQUARE_SIZE
            return row, col
        return None
    
    def handle_click(self, pos):
        """Handle mouse click events"""
        # Handle promotion selection if pending
        if self.promotion_pending:
            row, col = self.pending_promotion_pos
            cx = BOARD_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = BOARD_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2

            options = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
            for i, opt in enumerate(options):
                rect = pygame.Rect(cx - 100 + i * 50, cy - 25, 50, 50)
                if rect.collidepoint(pos):
                    self.board.complete_promotion(row, col, opt)
                    self.promotion_pending = False
                    self.pending_promotion_pos = None

                    # If playing against AI and it's AI's turn
                    if self.game_mode == GameMode.VS_COMPUTER and self.board.current_player == Color.BLACK:
                        self.ai_move()
                    return

        # If in main menu, handle settings and mode select clicks
        if not self.game_mode:
            # Two Player button: x=302, y=190, w=420, h=45
            if 302 <= pos[0] <= 722 and 190 <= pos[1] <= 235:
                self.game_mode = GameMode.TWO_PLAYER
                self.board = ChessBoard()
                self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                return
                
            # vs Computer button: x=302, y=245, w=420, h=45
            if 302 <= pos[0] <= 722 and 245 <= pos[1] <= 290:
                self.game_mode = GameMode.VS_COMPUTER
                self.board = ChessBoard()
                self.ai = ChessAI(self.ai_difficulties[self.current_difficulty_index])
                self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                return
                
            # Difficulty button: x=302, y=310, w=420, h=45
            if 302 <= pos[0] <= 722 and 310 <= pos[1] <= 355:
                self.current_difficulty_index = (self.current_difficulty_index + 1) % len(self.ai_difficulties)
                return
                
            # Time limit button: x=302, y=375, w=420, h=45
            if 302 <= pos[0] <= 722 and 375 <= pos[1] <= 420:
                self.current_time_limit_index = (self.current_time_limit_index + 1) % len(TIME_LIMITS)
                self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                return
                
            # Theme button: x=302, y=440, w=420, h=45
            if 302 <= pos[0] <= 722 and 440 <= pos[1] <= 485:
                self.current_theme_index = (self.current_theme_index + 1) % len(THEMES)
                return
                
            # Play / Start button: x=302, y=520, w=420, h=55
            if 302 <= pos[0] <= 722 and 520 <= pos[1] <= 575:
                self.game_mode = GameMode.VS_COMPUTER
                self.board = ChessBoard()
                self.ai = ChessAI(self.ai_difficulties[self.current_difficulty_index])
                self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                return
                
        # If in active game, handle sidebar clicks
        else:
            # Back to menu: (600, 375, 344, 40)
            if 600 <= pos[0] <= 944 and 375 <= pos[1] <= 415:
                self.game_mode = None
                self.board = ChessBoard()
                return
                
            # Restart game: (784, 275, 160, 40)
            if 784 <= pos[0] <= 944 and 275 <= pos[1] <= 315:
                self.restart_game()
                return
                
            # Undo move: (600, 275, 160, 40)
            if 600 <= pos[0] <= 760 and 275 <= pos[1] <= 315:
                self.undo_move()
                return
                
            # Previous move: (600, 325, 160, 40)
            if 600 <= pos[0] <= 760 and 325 <= pos[1] <= 365:
                if len(self.board.move_states) > 1 and self.board.current_move_index > 0:
                    self.board.current_move_index -= 1
                    self.board.load_board_state(self.board.move_states[self.board.current_move_index])
                return
                
            # Next move: (784, 325, 160, 40)
            if 784 <= pos[0] <= 944 and 325 <= pos[1] <= 365:
                if len(self.board.move_states) > 1 and self.board.current_move_index < len(self.board.move_states) - 1:
                    self.board.current_move_index += 1
                    self.board.load_board_state(self.board.move_states[self.board.current_move_index])
                return

        if self.board.game_over:
            return
            
        square = self.get_square_from_mouse(pos)
        if not square:
            return
            
        row, col = square
        clicked_piece = self.board.get_piece(row, col)
        
        # If a piece is already selected
        if self.board.selected_piece:
            # If clicking on a valid move square, make the move
            if (row, col) in self.board.valid_moves:
                is_capture = self.board.board[row][col] is not None
                success, status = self.board.execute_move(self.board.selected_piece.row,
                                                     self.board.selected_piece.col,
                                                     row, col)

                if success:
                    if is_capture:
                        self.sound_manager.play("capture")
                    else:
                        self.sound_manager.play("move")

                    if self.board.in_check:
                        self.sound_manager.play("check")

                    if status == "promotion":
                        self.promotion_pending = True
                        self.pending_promotion_pos = (row, col)
                    else:
                        self.board.selected_piece = None
                        self.board.valid_moves = []

                        # If playing against AI and it's AI's turn
                        if self.game_mode == GameMode.VS_COMPUTER and self.board.current_player == Color.BLACK:
                            self.ai_move()
                else:
                    self.board.selected_piece = None
                    self.board.valid_moves = []
            # If clicking on another piece of the same color, select that piece instead
            elif clicked_piece and clicked_piece.color == self.board.current_player:
                self.board.selected_piece = clicked_piece
                self.board.valid_moves = self.board.get_valid_moves(clicked_piece)
            # If clicking on an empty square or enemy piece, deselect current piece
            else:
                self.board.selected_piece = None
                self.board.valid_moves = []
        # If no piece is selected, select a piece if it belongs to current player
        elif clicked_piece and clicked_piece.color == self.board.current_player:
            self.board.selected_piece = clicked_piece
            self.board.valid_moves = self.board.get_valid_moves(clicked_piece)
    
    def ai_move(self):
        """Make AI move"""
        if (self.game_mode == GameMode.VS_COMPUTER and 
            self.board.current_player == Color.BLACK and not self.board.game_over):
            
            move = self.ai.get_move(self.board)
            if move:
                piece, (to_row, to_col) = move
                is_capture = self.board.board[to_row][to_col] is not None
                self.board.execute_move(piece.row, piece.col, to_row, to_col)

                if is_capture:
                    self.sound_manager.play("capture")
                else:
                    self.sound_manager.play("move")

                if self.board.in_check:
                    self.sound_manager.play("check")

                self.board.current_player = Color.WHITE
    
    async def run(self):
        """Main game loop"""
        running = True
        while running:
            # Update timers
            if self.game_mode and not self.board.game_over:
                dt = self.clock.get_time() / 1000.0
                if self.board.current_player == Color.WHITE:
                    self.white_time = max(0, self.white_time - dt)
                else:
                    self.black_time = max(0, self.black_time - dt)

                if self.white_time <= 0 or self.black_time <= 0:
                    self.board.game_over = True
                    self.board.winner = Color.BLACK if self.white_time <= 0 else Color.WHITE
                    self.sound_manager.play("game_over")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_mode:
                        self.restart_game()
                    elif event.key == pygame.K_1 and not self.game_mode:
                        self.game_mode = GameMode.TWO_PLAYER
                        self.board = ChessBoard()
                        self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                        self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                    elif event.key == pygame.K_2 and not self.game_mode:
                        self.game_mode = GameMode.VS_COMPUTER
                        self.board = ChessBoard()
                        self.ai = ChessAI(self.ai_difficulties[self.current_difficulty_index])
                        self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                        self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                    elif event.key == pygame.K_SPACE and not self.game_mode:
                        self.game_mode = GameMode.VS_COMPUTER
                        self.board = ChessBoard()
                        self.ai = ChessAI(self.ai_difficulties[self.current_difficulty_index])
                        self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                        self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                    elif event.key == pygame.K_b and self.game_mode:
                        self.game_mode = None
                        self.board = ChessBoard()
                    elif event.key == pygame.K_t:
                        self.current_theme_index = (self.current_theme_index + 1) % len(THEMES)
                    elif event.key == pygame.K_c and not self.game_mode:
                        self.current_time_limit_index = (self.current_time_limit_index + 1) % len(TIME_LIMITS)
                        self.white_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                        self.black_time = TIME_LIMITS[self.current_time_limit_index]["val"]
                    elif event.key == pygame.K_d and not self.game_mode:
                        self.current_difficulty_index = (self.current_difficulty_index + 1) % len(self.ai_difficulties)
                    elif event.key == pygame.K_u and self.game_mode and not self.board.game_over:
                        self.undo_move()
                    elif event.key == pygame.K_LEFT and len(self.board.move_states) > 1:
                        if self.board.current_move_index > 0:
                            self.board.current_move_index -= 1
                            self.board.load_board_state(self.board.move_states[self.board.current_move_index])
                    elif event.key == pygame.K_RIGHT and len(self.board.move_states) > 1:
                        if self.board.current_move_index < len(self.board.move_states) - 1:
                            self.board.current_move_index += 1
                            self.board.load_board_state(self.board.move_states[self.board.current_move_index])
 
            self.screen.fill((18, 22, 30))
 
            if not self.game_mode:
                self.draw_menu()
            else:
                self.draw_board()
                self.draw_pieces()
                self.draw_game_info()
                if self.promotion_pending:
                    self.draw_promotion_menu()

            pygame.display.flip()
            self.clock.tick(60)
            await asyncio.sleep(0)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    asyncio.run(game.run())

