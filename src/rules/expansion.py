
import random

from src.grid import Grid
from src.util import rand_between



def generate_star_expansion_single_step(grid_size=(12, 12), star_num=(1, 4), colors=("red", "blue")):
    """
    Careful, random.sample crashes if n > grid size. Same goes for n = 0.
    """
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    n = rand_between(*star_num)

    centers = random.sample(
        [(x, y) for x in range(1, cols - 1) for y in range(1, rows - 1)],
        n
    )

    for x, y in centers:
        grid_input.fill_cell(x, y, colors[0])

        grid_output.fill_cell(x + 1, y + 1, colors[1])
        grid_output.fill_cell(x + 1, y - 1, colors[1])
        grid_output.fill_cell(x - 1, y + 1, colors[1])
        grid_output.fill_cell(x - 1, y - 1, colors[1])

    for x, y in centers:
        grid_output.fill_cell(x, y, colors[0])  # refill the center cells that might have been over-colored

    params = {
        "event": "expansion",
        "condition": "shape",
        "stimulus": ["dots", "star"],
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": n
    }

    return grid_input, grid_output, params


def generate_star_expansion_full(grid_size=(12, 12), star_num=(1, 3), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    n = rand_between(*star_num)

    centers = random.sample(
        [(x, y) for x in range(1, cols - 1) for y in range(1, rows - 1)],
        n
    )

    for x, y in centers:
        grid_input.fill_cell(x, y, colors[0])

    dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))

    for x0, y0 in centers:
        for dx, dy in dirs:
            x, y = x0 + dx, y0 + dy
            while 0 <= x < cols and 0 <= y < rows:
                grid_output.fill_cell(x, y, colors[1])
                x += dx
                y += dy

    for x0, y0 in centers:
        grid_output.fill_cell(x0, y0, colors[0])  # refill the center cells that might have been over-colored

    params = {
        "event": "expansion",
        "condition": "shape",
        "stimulus": ["dots", "star"],
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": n
    }

    return grid_input, grid_output, params


def generate_plus_expansion_single_step(grid_size=(12, 12), plus_num=(1, 4), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    n = rand_between(*plus_num)
    centers = random.sample(
        [(x, y) for x in range(1, cols - 1) for y in range(1, rows - 1)],
        n
    )

    for x, y in centers:
        grid_input.fill_cell(x, y, colors[0])  # Center

        grid_output.fill_cell(x + 1, y, colors[1])  # Right
        grid_output.fill_cell(x - 1, y, colors[1])  # Left
        grid_output.fill_cell(x, y + 1, colors[1])  # Top
        grid_output.fill_cell(x, y - 1, colors[1])  # Bottom

    for x, y in centers:
        grid_output.fill_cell(x, y, colors[0])  # refill the center cells that might have been over-colored

    params = {
        "event": "expansion",
        "condition": "shape",
        "stimulus": ["dots", "plus"],
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": n
    }

    return grid_input, grid_output, params


def generate_plus_expansion_full(grid_size=(12, 12), plus_num=(1, 3), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    n = rand_between(*plus_num)

    centers = random.sample(
        [(x, y) for x in range(1, cols - 1) for y in range(1, rows - 1)],
        n
    )

    for x, y in centers:
        grid_input.fill_cell(x, y, colors[0])

    dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

    for x0, y0 in centers:
        for dx, dy in dirs:
            x, y = x0 + dx, y0 + dy
            while 0 <= x < cols and 0 <= y < rows:
                grid_output.fill_cell(x, y, colors[1])
                x += dx
                y += dy

    for x0, y0 in centers:
        grid_output.fill_cell(x0, y0, colors[0])  # refill the origin points that might have been over-colored

    params = {
        "event": "expansion",
        "condition": "shape",
        "stimulus": ["dots", "plus"],
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": n
    }

    return grid_input, grid_output, params


def generate_3arm_star_expansion_full(grid_size=(12, 12), star_num=(1, 3), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    n = rand_between(*star_num)

    centers = random.sample(
        [(x, y) for x in range(1, cols - 1) for y in range(1, rows - 1)],
        n
    )

    # mark centers on input
    for x, y in centers:
        grid_input.fill_cell(x, y, colors[0])

    # four diagonal directions
    dirs_all = ((1, 1), (1, -1), (-1, 1), (-1, -1))

    for x0, y0 in centers:
        # randomly choose one diagonal to *omit*
        dirs = list(dirs_all)
        skip_dir = random.choice(dirs)
        dirs.remove(skip_dir)

        for dx, dy in dirs:
            x, y = x0 + dx, y0 + dy
            while 0 <= x < cols and 0 <= y < rows:
                grid_output.fill_cell(x, y, colors[1])
                x += dx
                y += dy

    for x0, y0 in centers:
        grid_output.fill_cell(x0, y0, colors[0])  # refill the origin points that might have been over-colored

    params = {
        "event": "expansion",
        "condition": "shape",
        "stimulus": ["dots", "star"],
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": n
    }

    return grid_input, grid_output, params
