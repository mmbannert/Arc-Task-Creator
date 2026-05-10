import random

from src.util import rand_between
from src.rules._common import make_grids, make_params
from src.config import COLORS, GRID_SIZE


def generate_cross_expansion_single_step(star_num=(1, 4)):
    """
    Careful, random.sample crashes if n > grid size. Same goes for n = 0.
    """
    grid_input, grid_output = make_grids()
    n = rand_between(*star_num)
    centers = random.sample(grid_input.interior_cells(), n)

    grid_input.fill_multiple_cells(centers, COLORS[0])
    directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    _apply_single_step(grid_output, centers, directions)
    grid_output.fill_multiple_cells(centers, COLORS[0])  # refill the center cells that might have been over-colored

    params = make_params(
        event="expansion",
        condition="shape",
        stimulus="step_expansion",
        colors=COLORS[:2],
        n_objects=n,
    )

    return grid_input, grid_output, params


def generate_cross_expansion_ray(star_num=(1, 3)):
    grid_input, grid_output = make_grids()
    n = rand_between(*star_num)
    centers = random.sample(grid_input.interior_cells(), n)

    grid_input.fill_multiple_cells(centers, COLORS[0])
    directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    _apply_ray(grid_output, centers, directions)
    grid_output.fill_multiple_cells(centers, COLORS[0])

    params = make_params(
        event="expansion",
        condition="shape",
        stimulus="ray_expansion",
        colors=COLORS[:2],
        n_objects=n,
    )

    return grid_input, grid_output, params


def generate_plus_expansion_single_step(plus_num=(1, 4)):
    grid_input, grid_output = make_grids()
    n = rand_between(*plus_num)
    centers = random.sample(grid_input.interior_cells(), n)

    grid_input.fill_multiple_cells(centers, COLORS[0])
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    _apply_single_step(grid_output, centers, directions)
    grid_output.fill_multiple_cells(centers, COLORS[0])

    params = make_params(
        event="expansion",
        condition="shape",
        stimulus="step_expansion",
        colors=COLORS[:2],
        n_objects=n,
    )

    return grid_input, grid_output, params


def generate_plus_expansion_ray(plus_num=(1, 3)):
    grid_input, grid_output = make_grids()
    n = rand_between(*plus_num)
    centers = random.sample(grid_input.interior_cells(), n)

    grid_input.fill_multiple_cells(centers, COLORS[0])
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    _apply_ray(grid_output, centers, directions)
    grid_output.fill_multiple_cells(centers, COLORS[0])

    params = make_params(
        event="expansion",
        condition="shape",
        stimulus="ray_expansion",
        colors=COLORS[:2],
        n_objects=n,
    )

    return grid_input, grid_output, params


def generate_3arm_star_expansion_ray(star_num=(1, 3)):
    grid_input, grid_output = make_grids()
    n = rand_between(*star_num)
    centers = random.sample(grid_input.interior_cells(), n)

    grid_input.fill_multiple_cells(centers, COLORS[0])
    directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))

    # Remove one arm randomly
    selected_directions = list(directions)
    skip_direction = random.choice(selected_directions)
    selected_directions.remove(skip_direction)

    _apply_ray(grid_output, centers, selected_directions)
    grid_output.fill_multiple_cells(centers, COLORS[0])

    params = make_params(
        event="expansion",
        condition="shape",
        stimulus="ray_expansion",
        colors=COLORS[:2],
        n_objects=n,
    )

    return grid_input, grid_output, params


def generate_star_expansion_ray(star_num=(1, 2)):
    grid_input, grid_output = make_grids()
    n = rand_between(*star_num)
    centers = random.sample(grid_input.interior_cells(), n)

    grid_input.fill_multiple_cells(centers, COLORS[0])
    directions = ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1))
    _apply_ray(grid_output, centers, directions)
    grid_output.fill_multiple_cells(centers, COLORS[0])

    params = make_params(
        event="expansion",
        condition="shape",
        stimulus="ray_expansion",
        colors=COLORS[:2],
        n_objects=n,
    )

    return grid_input, grid_output, params


def _apply_single_step(grid_output, centers, directions):
    for x0, y0 in centers:
        for dx, dy in directions:
            grid_output.fill_cell(x0 + dx, y0 + dy, COLORS[1])


def _apply_ray(grid_output, centers, directions):
    rows, cols = GRID_SIZE
    for x0, y0 in centers:
        for dx, dy in directions:
            x, y = x0 + dx, y0 + dy
            while 0 <= x < cols and 0 <= y < rows:
                grid_output.fill_cell(x, y, COLORS[1])
                x += dx
                y += dy
