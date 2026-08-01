import pygame
import os

# Initialize Pygame
pygame.init()

# Constants
PIECE_SIZE = 50
COLORS = {
    'white': (255, 255, 255),
    'black': (50, 50, 50),
    'outline': (0, 0, 0),
    'highlight': (200, 200, 200)
}

def create_king(color):
    """Create a king piece image"""
    surface = pygame.Surface((PIECE_SIZE, PIECE_SIZE), pygame.SRCALPHA)
    main_color = COLORS[color]
    outline_color = COLORS['outline']
    
    # Crown base
    pygame.draw.ellipse(surface, main_color, (10, 30, 30, 15))
    pygame.draw.ellipse(surface, outline_color, (10, 30, 30, 15), 2)
    
    # Crown points
    points = [(15, 15), (20, 5), (25, 15), (30, 5), (35, 15), (40, 30), (10, 30)]
    pygame.draw.polygon(surface, main_color, points)
    pygame.draw.polygon(surface, outline_color, points, 2)
    
    # Cross on top
    pygame.draw.line(surface, outline_color, (25, 5), (25, 15), 2)
    pygame.draw.line(surface, outline_color, (20, 10), (30, 10), 2)
    
    return surface

def create_queen(color):
    """Create a queen piece image"""
    surface = pygame.Surface((PIECE_SIZE, PIECE_SIZE), pygame.SRCALPHA)
    main_color = COLORS[color]
    outline_color = COLORS['outline']
    
    # Crown base
    pygame.draw.ellipse(surface, main_color, (10, 25, 30, 20))
    pygame.draw.ellipse(surface, outline_color, (10, 25, 30, 20), 2)
    
    # Crown spikes
    points = [(10, 25), (15, 10), (20, 20), (25, 5), (30, 20), (35, 10), (40, 25)]
    for i in range(len(points) - 1):
        pygame.draw.line(surface, outline_color, points[i], points[i + 1], 2)
    
    # Fill crown
    crown_points = [(10, 25), (15, 10), (20, 20), (25, 5), (30, 20), (35, 10), (40, 25), (40, 35), (10, 35)]
    pygame.draw.polygon(surface, main_color, crown_points)
    pygame.draw.polygon(surface, outline_color, crown_points, 2)
    
    return surface

def create_rook(color):
    """Create a rook piece image"""
    surface = pygame.Surface((PIECE_SIZE, PIECE_SIZE), pygame.SRCALPHA)
    main_color = COLORS[color]
    outline_color = COLORS['outline']
    
    # Castle body
    pygame.draw.rect(surface, main_color, (15, 15, 20, 30))
    pygame.draw.rect(surface, outline_color, (15, 15, 20, 30), 2)
    
    # Castle battlements
    pygame.draw.rect(surface, main_color, (12, 10, 26, 10))
    pygame.draw.rect(surface, outline_color, (12, 10, 26, 10), 2)
    
    # Battlements details
    pygame.draw.line(surface, outline_color, (17, 10), (17, 20), 2)
    pygame.draw.line(surface, outline_color, (25, 10), (25, 20), 2)
    pygame.draw.line(surface, outline_color, (33, 10), (33, 20), 2)
    
    return surface

def create_bishop(color):
    """Create a bishop piece image"""
    surface = pygame.Surface((PIECE_SIZE, PIECE_SIZE), pygame.SRCALPHA)
    main_color = COLORS[color]
    outline_color = COLORS['outline']
    
    # Bishop body (teardrop shape)
    pygame.draw.ellipse(surface, main_color, (15, 20, 20, 25))
    pygame.draw.ellipse(surface, outline_color, (15, 20, 20, 25), 2)
    
    # Bishop head
    pygame.draw.circle(surface, main_color, (25, 15), 8)
    pygame.draw.circle(surface, outline_color, (25, 15), 8, 2)
    
    # Bishop hat
    pygame.draw.circle(surface, main_color, (25, 10), 4)
    pygame.draw.circle(surface, outline_color, (25, 10), 4, 2)
    
    # Cross cut
    pygame.draw.line(surface, outline_color, (20, 25), (30, 35), 2)
    
    return surface

def create_knight(color):
    """Create a knight piece image"""
    surface = pygame.Surface((PIECE_SIZE, PIECE_SIZE), pygame.SRCALPHA)
    main_color = COLORS[color]
    outline_color = COLORS['outline']
    
    # Horse head shape
    points = [(15, 40), (20, 30), (18, 20), (22, 15), (28, 12), (35, 15), (38, 25), (35, 35), (30, 40)]
    pygame.draw.polygon(surface, main_color, points)
    pygame.draw.polygon(surface, outline_color, points, 2)
    
    # Horse ear
    pygame.draw.polygon(surface, main_color, [(28, 12), (30, 8), (32, 12)])
    pygame.draw.polygon(surface, outline_color, [(28, 12), (30, 8), (32, 12)], 2)
    
    # Eye
    pygame.draw.circle(surface, outline_color, (30, 20), 2)
    
    # Mane
    pygame.draw.line(surface, outline_color, (22, 15), (25, 25), 2)
    
    return surface

def create_pawn(color):
    """Create a pawn piece image"""
    surface = pygame.Surface((PIECE_SIZE, PIECE_SIZE), pygame.SRCALPHA)
    main_color = COLORS[color]
    outline_color = COLORS['outline']
    
    # Pawn head
    pygame.draw.circle(surface, main_color, (25, 20), 8)
    pygame.draw.circle(surface, outline_color, (25, 20), 8, 2)
    
    # Pawn body
    pygame.draw.ellipse(surface, main_color, (18, 28, 14, 17))
    pygame.draw.ellipse(surface, outline_color, (18, 28, 14, 17), 2)
    
    return surface

def create_all_pieces():
    """Create all chess piece images"""
    # Create assets directory
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    piece_functions = {
        'king': create_king,
        'queen': create_queen,
        'rook': create_rook,
        'bishop': create_bishop,
        'knight': create_knight,
        'pawn': create_pawn
    }
    
    colors = ['white', 'black']
    
    for color in colors:
        for piece_name, piece_func in piece_functions.items():
            surface = piece_func(color)
            filename = f"{color}_{piece_name}.png"
            filepath = os.path.join(assets_dir, filename)
            pygame.image.save(surface, filepath)
            print(f"Created {filepath}")
    
    print("All chess piece images created successfully!")

if __name__ == "__main__":
    create_all_pieces()
    pygame.quit()

