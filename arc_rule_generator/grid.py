class Grid:
    def __init__(self, rows, cols, background="black"):
        self.rows = rows
        self.cols = cols
        self.grid = [[background for _ in range(cols)] for _ in range(rows)]

    # Getters

    def get_cell(self, row, col):
        return self.grid[row][col]

    def get_grid(self):
        return self.grid

    def copy(self):
        """Return an independent copy of the grid."""
        new_grid = Grid(self.rows, self.cols)
        new_grid.grid = [row.copy() for row in self.grid]
        return new_grid

    def get_coordinates(self):
        """Returns a flat list of all cell coordinates as (row, col) tuples."""
        return [
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
        ]

    def get_interior_cells(self):
        """Return all non-border cells as (row, col) coordinates."""
        return [
            (row, col)
            for row in range(1, self.rows - 1)
            for col in range(1, self.cols - 1)
        ]

    def get_occupied_bounding_box(self, background="black"):
        """Return the bounding box of non-background cells as: (row_min, row_max, col_min, col_max)."""
        row_min, row_max = self.rows, -1
        col_min, col_max = self.cols, -1

        for row in range(self.rows):
            for col in range(self.cols):
                if self.get_cell(row, col) != background:
                    row_min = min(row_min, row)
                    row_max = max(row_max, row)
                    col_min = min(col_min, col)
                    col_max = max(col_max, col)

        return row_min, row_max, col_min, col_max

    def get_rect(self, row_min, row_max, col_min, col_max):
        """Return a new Grid containing the selected inclusive bounding box."""
        new_rows = row_max - row_min + 1
        new_cols = col_max - col_min + 1
        out = Grid(new_rows, new_cols)

        for row in range(new_rows):
            for col in range(new_cols):
                out.set_cell(
                    row,
                    col,
                    self.get_cell(row_min + row, col_min + col),
                )

        return out

    # Setters

    def set_cell(self, row, col, color):
        self.grid[row][col] = color

    def set_multi_cells(self, cells, color):
        """Fill multiple (row, col) cells with the same color."""
        for row, col in cells:
            self.set_cell(row, col, color)

    def set_rect(self, row_min, row_max, col_min, col_max, color):
        """Fill a rectangular area using inclusive row/column bounds."""
        for row in range(row_min, row_max + 1):
            for col in range(col_min, col_max + 1):
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    self.set_cell(row, col, color)

    def set_all(self, color):
        """Fill the entire grid."""
        for row in range(self.rows):
            for col in range(self.cols):
                self.set_cell(row, col, color)

    def set_grid_at(self, other, row_offset, col_offset):
        """Paste another grid using a (row, col) offset."""
        for row in range(other.rows):
            for col in range(other.cols):
                self.set_cell(
                    row_offset + row,
                    col_offset + col,
                    other.get_cell(row, col),
                )

    # Mutating geometric transformations

    def rotate_ccw_90(self):
        """Rotate 90° counterclockwise. Mutates the grid and swaps rows/cols."""
        out = [[None] * self.rows for _ in range(self.cols)]

        for row in range(self.rows):
            for col in range(self.cols):
                out[self.cols - 1 - col][row] = self.grid[row][col]

        self.grid = out
        self.rows, self.cols = self.cols, self.rows

    def rotate_180(self):
        """Rotate 180°. Mutates the grid."""
        self.rotate_ccw_90()
        self.rotate_ccw_90()

    def mirror_x(self):
        """Mirror across the x-axis: top ↔ bottom."""
        self.grid = self.grid[::-1]

    def mirror_y(self):
        """Mirror across the y-axis: left ↔ right."""
        self.grid = [row[::-1] for row in self.grid]
