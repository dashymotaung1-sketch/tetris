class GameBoard:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def clear_lines(self):
        """Clear completed lines and return count"""
        lines_cleared = 0
        y = self.height - 1

        while y >= 0:
            if all(self.grid[y][x] is not None for x in range(self.width)):
                # Remove this line
                del self.grid[y]
                # Insert new empty line at top
                self.grid.insert(0, [None for _ in range(self.width)])
                lines_cleared += 1
            else:
                y -= 1

        return lines_cleared

    def check_collision(self, piece, x, y):
        """Check if piece collides with board at given position"""
        for r, row in enumerate(piece):
            for c, cell in enumerate(row):
                if cell:
                    new_x = x + c
                    new_y = y + r

                    # Check boundaries
                    if new_x < 0 or new_x >= self.width:
                        return True
                    if new_y >= self.height:
                        return True

                    # Check collision with existing blocks
                    if new_y >= 0 and self.grid[new_y][new_x] is not None:
                        return True
        return False