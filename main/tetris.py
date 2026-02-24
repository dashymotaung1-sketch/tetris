import pygame
import random
import sys
from pieces import PIECES, PIECE_COLORS
from gameboard import GameBoard

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 150

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Movement timing constants
MOVE_DELAY = 150
INITIAL_MOVE_DELAY = 200

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + SIDEBAR_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Movement timing variables
        self.last_move_time = 0
        self.move_cooldown = 0
        self.key_held = False
        self.last_key = None

        self.reset_game()

    def reset_game(self):
        """Reset game state"""
        self.board = GameBoard(GRID_WIDTH, GRID_HEIGHT)
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds per drop (decreases with level)

    def new_piece(self):
        """Create a new random tetromino"""
        piece_type = random.choice(list(PIECES.keys()))
        return {
            'type': piece_type,
            'shape': [row[:] for row in PIECES[piece_type]],
            'x': GRID_WIDTH // 2 - len(PIECES[piece_type][0]) // 2,
            'y': 0,
            'color': PIECE_COLORS[piece_type]
        }

    def rotate_piece(self, piece, direction=1):
        """Rotate the piece 90 degrees clockwise"""
        # Transpose then reverse each row for clockwise rotation
        rotated = list(zip(*piece['shape'][::-1]))
        return [list(row) for row in rotated]

    def valid_move(self, piece, x, y, shape=None):
        """Check if piece move is valid"""
        if shape is None:
            shape = piece['shape']

        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell:
                    new_x = x + c
                    new_y = y + r

                    # Check boundaries
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False

                    # Check collision with board
                    if new_y >= 0 and self.board.grid[new_y][new_x]:
                        return False
        return True

    def lock_piece(self):
        """Lock current piece in place and spawn next piece"""
        # Add piece to board grid
        for r, row in enumerate(self.current_piece['shape']):
            for c, cell in enumerate(row):
                if cell:
                    y = self.current_piece['y'] + r
                    x = self.current_piece['x'] + c
                    if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                        self.board.grid[y][x] = self.current_piece['color']

        # Check for completed lines
        lines = self.board.clear_lines()
        if lines > 0:
            self.update_score(lines)

        # Spawn next piece
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

        # Check if game over
        if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
            self.game_over = True

    def update_score(self, lines):
        """Update score based on lines cleared"""
        # Classic Tetris scoring
        line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
        self.lines_cleared += lines
        self.score += line_scores[lines] * self.level

        # Level up every 10 lines
        self.level = self.lines_cleared // 10 + 1
        self.fall_speed = max(100, 500 - (self.level - 1) * 50)

    def handle_input(self):
        """Handle keyboard input with proper timing"""
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # Handle initial key press and repeats
        if keys[pygame.K_LEFT]:
            if self.last_key != pygame.K_LEFT or not self.key_held:
                # First press - move immediately
                if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                    self.current_piece['x'] -= 1
                self.last_key = pygame.K_LEFT
                self.key_held = True
                self.last_move_time = current_time
                self.move_cooldown = INITIAL_MOVE_DELAY
            elif current_time - self.last_move_time > self.move_cooldown:
                # Repeat move after delay
                if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                    self.current_piece['x'] -= 1
                self.last_move_time = current_time
                self.move_cooldown = MOVE_DELAY

        elif keys[pygame.K_RIGHT]:
            if self.last_key != pygame.K_RIGHT or not self.key_held:
                # First press - move immediately
                if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                    self.current_piece['x'] += 1
                self.last_key = pygame.K_RIGHT
                self.key_held = True
                self.last_move_time = current_time
                self.move_cooldown = INITIAL_MOVE_DELAY
            elif current_time - self.last_move_time > self.move_cooldown:
                # Repeat move after delay
                if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                    self.current_piece['x'] += 1
                self.last_move_time = current_time
                self.move_cooldown = MOVE_DELAY

        elif keys[pygame.K_DOWN]:
            if self.last_key != pygame.K_DOWN or not self.key_held:
                # First press - move immediately
                if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                    self.current_piece['y'] += 1
                    self.score += 1  # Soft drop bonus
                self.last_key = pygame.K_DOWN
                self.key_held = True
                self.last_move_time = current_time
                self.move_cooldown = INITIAL_MOVE_DELAY
            elif current_time - self.last_move_time > self.move_cooldown:
                # Repeat move after delay
                if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                    self.current_piece['y'] += 1
                    self.score += 1  # Soft drop bonus
                self.last_move_time = current_time
                self.move_cooldown = MOVE_DELAY

        else:
            # No keys pressed - reset tracking
            self.key_held = False
            self.last_key = None

        # Handle rotation (always immediate, no repeat needed)
        if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            # Check if rotation key was just pressed (not held)
            if not hasattr(self, 'rotation_pressed') or not self.rotation_pressed:
                rotated = self.rotate_piece(self.current_piece)
                if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'], rotated):
                    self.current_piece['shape'] = rotated
                self.rotation_pressed = True
        else:
            self.rotation_pressed = False

    def update(self):
        """Update game state"""
        if self.game_over:
            return

        # Handle automatic falling
        self.fall_time += self.clock.get_rawtime()
        self.clock.tick()

        if self.fall_time >= self.fall_speed:
            self.fall_time = 0

            # Move piece down
            if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                self.current_piece['y'] += 1
            else:
                self.lock_piece()

    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)

        # Draw game grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1)

                if self.board.grid[y][x]:
                    # Draw placed piece
                    pygame.draw.rect(self.screen, self.board.grid[y][x], rect)
                else:
                    # Draw empty cell
                    pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)

        # Draw current piece
        if self.current_piece and not self.game_over:
            for r, row in enumerate(self.current_piece['shape']):
                for c, cell in enumerate(row):
                    if cell:
                        x = (self.current_piece['x'] + c) * GRID_SIZE
                        y = (self.current_piece['y'] + r) * GRID_SIZE
                        rect = pygame.Rect(x, y, GRID_SIZE - 1, GRID_SIZE - 1)
                        pygame.draw.rect(self.screen, self.current_piece['color'], rect)

        # Draw sidebar
        sidebar_x = SCREEN_WIDTH + 10

        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (sidebar_x, 20))

        # Level
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (sidebar_x, 50))

        # Lines
        lines_text = self.small_font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (sidebar_x, 80))

        # Next piece
        next_text = self.small_font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (sidebar_x, 120))

        # Draw next piece
        if self.next_piece:
            for r, row in enumerate(self.next_piece['shape']):
                for c, cell in enumerate(row):
                    if cell:
                        x = sidebar_x + c * 20
                        y = 150 + r * 20
                        rect = pygame.Rect(x, y, 19, 19)
                        pygame.draw.rect(self.screen, self.next_piece['color'], rect)

        # Game over message
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)

            restart_text = self.small_font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(restart_text, restart_rect)

        # Controls
        controls = [
            "Controls:",
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft drop",
            "Space : Rotate",
            "R : Restart"
        ]

        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, GRAY)
            self.screen.blit(text, (sidebar_x, 300 + i * 25))

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()

            self.handle_input()
            self.update()
            self.draw()

if __name__ == "__main__":
    game = Tetris()
    game.run()