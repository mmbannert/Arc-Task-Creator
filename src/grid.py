class Grid:
    def __init__(self, rows, cols, background="black"):
        self.rows = rows
        self.cols = cols
        self.grid = [[background for _ in range(cols)] for _ in range(rows)]

    def set(self, row, col, color):
        self.grid[row][col] = color

    def get(self, row, col):
        return self.grid[row][col]

    def fill_cell(self, row, col, color):
        """Alias for set() — for semantic clarity."""
        self.set(row, col, color)

    def fill_multiple_cells(self, cells, color):
        """Fill multiple cells with the same color."""
        for row, col in cells:
            self.fill_cell(row, col, color)

    def fill_rect(self, col_min, col_max, row_min, row_max, color):
        """
        Fill a rectangular area with `color`.
        Args:
            col_min, col_max: horizontal range (columns)
            row_min, row_max: vertical range (rows)
        """
        for r in range(row_min, row_max + 1):
            for c in range(col_min, col_max + 1):
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.grid[r][c] = color

    def fill_all(self, color):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = color

    def as_list(self):
        return self.grid

    def cells(self):
        """Return coordinates of all cells in the grid."""
        return [
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
        ]

    def interior_cells(self):
        """Return coordinates of all non-border cells in the grid."""
        return [
            (row, col)
            for row in range(1, self.rows - 1)
            for col in range(1, self.cols - 1)
        ]

    def copy(self):
        new_grid = Grid(self.rows, self.cols)
        new_grid.grid = [row.copy() for row in self.grid]
        return new_grid

    def rotate_ccw_90(self):
        """Rotate 90° counterclockwise (rows↔cols). Mutates self."""
        out = [[None] * self.rows for _ in range(self.cols)]
        for r in range(self.rows):
            for c in range(self.cols):
                out[self.cols - 1 - c][r] = self.grid[r][c]
        self.grid = out
        self.rows, self.cols = self.cols, self.rows  # swap

    def rotate_180(self):
        self.rotate_ccw_90()
        self.rotate_ccw_90()

    def mirror_x(self):
        """Mirror along the x-axis (horizontal axis): top ↔ bottom. Mutates self."""
        out = [[None] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                out[self.rows - 1 - r][c] = self.grid[r][c]
        self.grid = out

    def mirror_y(self):
        """Mirror along the y-axis (vertical axis): left ↔ right. Mutates self."""
        out = [[None] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                out[r][self.cols - 1 - c] = self.grid[r][c]
        self.grid = out

    def get_occupied_bounding_box(self, background="black"):
        """
        Return the tight bounding box of all non-background cells as:
        (row_min, row_max, col_min, col_max)
        """
        row_min, row_max = self.rows, -1
        col_min, col_max = self.cols, -1

        for r in range(self.rows):
            for c in range(self.cols):
                if self.get(r, c) != background:
                    row_min = min(row_min, r)
                    row_max = max(row_max, r)
                    col_min = min(col_min, c)
                    col_max = max(col_max, c)

        return row_min, row_max, col_min, col_max

    def extract_box(self, row_min, row_max, col_min, col_max):
        """
        Return a new Grid containing only the selected bbox.
        """
        new_rows = row_max - row_min + 1
        new_cols = col_max - col_min + 1
        out = Grid(new_rows, new_cols)

        for r in range(new_rows):
            for c in range(new_cols):
                out.set(r, c, self.get(row_min + r, col_min + c))

        return out

    def paste_at(self, other, row_offset, col_offset):
        """
        Paste another grid into self at the given top-left offset.
        """
        for r in range(other.rows):
            for c in range(other.cols):
                self.set(row_offset + r, col_offset + c, other.get(r, c))
