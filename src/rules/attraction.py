import random

from src.config import COLORS
from src.rules._common import make_grids, make_params
from src.grid import Grid
from src.util import rand_between


def generate_color_attraction(size_range=(2, 5)):
    grid_input, grid_output = make_grids()
    rows, cols = grid_input.rows, grid_input.cols

    w1, h1, w2, h2 = (rand_between(*size_range) for _ in range(4))
    while max(_block_area(w1, h1), _block_area(w2, h2)) < 1.3 * min(_block_area(w1, h1), _block_area(w2, h2)):
        w1, h1, w2, h2 = (rand_between(*size_range) for _ in range(4))

    # Always assume left to right movement direction
    x1 = rand_between(0, cols - w1 - w2 - 1)
    y1 = rand_between(0, rows - h1 - 1)

    x2 = rand_between(x1 + w1 + 1, cols - w2)
    y2 = rand_between(max(0, y1 - h2 + 1), min(rows - h2, y1 + h1 - 1))

    grid_input.fill_rect(col_min=x1, row_min=y1, col_max=x1 + w1 - 1, row_max=y1 + h1 - 1, color=COLORS[0])
    grid_input.fill_rect(col_min=x2, row_min=y2, col_max=x2 + w2 - 1, row_max=y2 + h2 - 1, color=COLORS[1])

    grid_output.fill_rect(col_min=x1, row_min=y1, col_max=x1 + w1 - 1, row_max=y1 + h1 - 1, color=COLORS[0])
    grid_output.fill_rect(col_min=x1 + w1, row_min=y2, col_max=x1 + w1 + w2 - 1, row_max=y2 + h2 - 1, color=COLORS[1])

    # Rotate to generate all movement directions
    _random_rotate_pair(grid_input, grid_output)

    params = make_params(
        event="attraction",
        condition=["color", "movement"],
        stimulus="big_blocks",
        colors=COLORS[:2],
        n_objects=2,
        bigger_block=COLORS[0] if _block_area(w1, h1) > _block_area(w2, h2) else COLORS[1],
    )

    return grid_input, grid_output, params


def generate_size_attraction(size_range=(3, 6)):
    grid_input, grid_output = make_grids()
    rows, cols = grid_input.rows, grid_input.cols

    w1, h1 = (rand_between(*size_range) for _ in range(2))
    w2 = rand_between(2, w1 - 1)
    h2 = rand_between(2, h1 - 1)

    x1 = rand_between(0, cols - w1 - w2 - 1)
    y1 = rand_between(0, rows - h1 - 1)

    x2 = rand_between(x1 + w1 + 1, cols - w2)
    y2 = rand_between(max(0, y1 - h2 + 1), min(rows - h2, y1 + h1 - 1))

    color_big, color_small = random.sample(COLORS[:2], 2)

    grid_input.fill_rect(col_min=x1, row_min=y1, col_max=x1 + w1 - 1, row_max=y1 + h1 - 1, color=color_big)
    grid_input.fill_rect(col_min=x2, row_min=y2, col_max=x2 + w2 - 1, row_max=y2 + h2 - 1, color=color_small)

    grid_output.fill_rect(col_min=x1, row_min=y1, col_max=x1 + w1 - 1, row_max=y1 + h1 - 1, color=color_big)
    grid_output.fill_rect(col_min=x1 + w1, row_min=y2, col_max=x1 + w1 + w2 - 1, row_max=y2 + h2 - 1, color=color_small)

    _random_rotate_pair(grid_input, grid_output)

    params = make_params(
        event="attraction",
        condition=["shape", "movement"],
        stimulus="big_blocks",
        colors=COLORS[:2],
        n_objects=2,
        bigger_block=color_big,
    )

    return grid_input, grid_output, params


def generate_color_repulsion(size_range=(2, 5)):
    grid_input, grid_output = make_grids()
    rows, cols = grid_input.rows, grid_input.cols

    w1, h1, w2, h2 = (rand_between(*size_range) for _ in range(4))

    x1 = rand_between(0, cols - w1 - w2 - 1)
    y1 = rand_between(h2, rows - h1 - 1)

    x2 = x1 + w1
    y2 = rand_between(y1 - h2 // 2 + 1, y1 + h2 // 2 - 1)

    grid_input.fill_rect(col_min=x1, row_min=y1, col_max=x1 + w1 - 1, row_max=y1 + h1 - 1, color=COLORS[0])
    grid_input.fill_rect(col_min=x2, row_min=y2, col_max=x2 + w2 - 1, row_max=y2 + h2 - 1, color=COLORS[1])

    grid_output.fill_rect(col_min=x1, row_min=y1, col_max=x1 + w1 - 1, row_max=y1 + h1 - 1, color=COLORS[0])
    grid_output.fill_rect(col_min=cols - w2, row_min=y2, col_max=cols, row_max=y2 + h2 - 1, color=COLORS[1])

    _random_rotate_pair(grid_input, grid_output)

    params = make_params(
        event="repulsion",
        condition=["color", "movement"],
        stimulus="big_blocks",
        colors=COLORS[:2],
        n_objects=2,
    )

    return grid_input, grid_output, params


def generate_falling_blocks(size_range=(2, 6)):
    grid_input, grid_output = make_grids()
    rows, cols = grid_input.rows, grid_input.cols

    w1, h1, w2, h2 = (rand_between(*size_range) for _ in range(4))

    x1 = rand_between(0, cols - w1 - w2 - 1)
    y1 = rand_between(1, rows - h1 - 1)

    x2 = rand_between(x1 + w1 + 1, cols - w2)
    y2 = rand_between(1, rows - h2 - 1)

    grid_input.fill_rect(col_min=x1, row_min=y1, col_max=x1 + w1 - 1, row_max=y1 + h1 - 1, color=COLORS[0])
    grid_input.fill_rect(col_min=x2, row_min=y2, col_max=x2 + w2 - 1, row_max=y2 + h2 - 1, color=COLORS[1])

    grid_output.fill_rect(col_min=x1, row_min=0, col_max=x1 + w1 - 1, row_max=0 + h1 - 1, color=COLORS[0])
    grid_output.fill_rect(col_min=x2, row_min=0, col_max=x2 + w2 - 1, row_max=0 + h2 - 1, color=COLORS[1])

    params = make_params(
        event="falling",
        condition="movement",
        stimulus="big_blocks",
        colors=COLORS[:2],
        n_objects=2,
    )

    return grid_input, grid_output, params


def generate_float(size_range=(2, 6)):
    grid_input, grid_output, params = generate_falling_blocks(size_range)
    # funny idea: floating is opposite direction falling
    grid_input.rotate_180()
    grid_output.rotate_180()

    params = make_params(
        event="floating",
        condition="movement",
        stimulus="big_blocks",
        colors=COLORS[:2],
        n_objects=2,
    )

    return grid_input, grid_output, params


def generate_falling_dots(n_objects=(3, 10)):
    """    Unused in experiment    """
    grid_input, _ = make_grids()

    n = rand_between(*n_objects)
    positions = random.sample(grid_input.cells(), n)

    for row, col in positions:
        grid_input.fill_cell(row, col, random.choice(COLORS[:2]))

    grid_output = _apply_gravity(grid_input)

    params = make_params(
        event="falling",
        condition="movement",
        stimulus="dots",
        colors=COLORS[:2],
        n_objects=n,
    )

    return grid_input, grid_output, params


def _apply_gravity(grid: Grid) -> Grid:
    rows, cols = grid.rows, grid.cols
    out = Grid(rows, cols)

    for c in range(cols):
        col = [grid.get(r, c) for r in range(rows) if grid.get(r, c) != "black"]
        r = 0  # bottom is row 0 in coordinate system
        for color in col:  # keep order stable
            out.fill_cell(r, c, color)
            r += 1

    return out


def _random_rotate_pair(grid_input, grid_output):
    for _ in range(random.randrange(4)):
        grid_input.rotate_ccw_90()
        grid_output.rotate_ccw_90()


def _block_area(w, h):
    return w * h


