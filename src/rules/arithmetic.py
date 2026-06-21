import random

from rules._common import make_grids, make_params
from src.config import COLORS
from src.util import rand_between


def generate_dot_majority_recolor(block_num=(1, 6)):
    return _generate_dot_counting_recolor(
        target="majority",
        block_num=block_num
    )


def generate_dot_minority_recolor(block_num=(1, 6)):
    return _generate_dot_counting_recolor(
        target="minority",
        block_num=block_num
    )


def _generate_dot_counting_recolor(target="majority", block_num=(1, 6)):
    grid_input, grid_output = make_grids()

    color1, color2 = random.sample(COLORS[:2], 2)
    n1, n2 = _sample_two_unique_counts(block_num)

    n_majority = max(n1, n2)
    n_minority = min(n1, n2)
    majority_color = color1
    minority_color = color2

    all_positions = random.sample(
        grid_input.cells(),
        n_majority + n_minority
    )

    majority_positions = all_positions[:n_majority]
    minority_positions = all_positions[n_majority:]

    grid_input.fill_multiple_cells(majority_positions, majority_color)
    grid_input.fill_multiple_cells(minority_positions, minority_color)

    target_color = majority_color if target == "majority" else minority_color
    grid_output.fill_multiple_cells(all_positions, target_color)

    params = make_params(
        event="recoloring",
        condition=["color", "counting"],
        stimulus="dots",
        colors=(majority_color, minority_color),
        n_objects=n_majority + n_minority,
        counting_type=_counting_type(n_majority, n_minority),
        target=target,
    )

    return grid_input, grid_output, params


def generate_cross_plus_majority_recolor(stamp_num=(1, 3)):
    return _generate_cross_plus_counting_recolor(
        target="majority",
        stamp_num=stamp_num,
    )


def generate_cross_plus_minority_recolor(stamp_num=(1, 3)):
    return _generate_cross_plus_counting_recolor(
        target="minority",
        stamp_num=stamp_num,
    )


def _generate_cross_plus_counting_recolor(target="majority", stamp_num=(1, 3)):
    grid_input, grid_output = make_grids()

    n_cross, n_plus = _sample_two_unique_counts(stamp_num)
    while n_cross + n_plus > 4:  # don't want too many objects at once
        n_cross, n_plus = _sample_two_unique_counts(stamp_num)

    placed = _place_non_overlapping_shapes(
        grid_input,
        {"cross": n_cross, "plus": n_plus}
    )

    n_majority = max(n_cross, n_plus)
    n_minority = min(n_cross, n_plus)

    majority_shape = "cross" if n_cross > n_plus else "plus"
    minority_shape = "plus" if majority_shape == "cross" else "cross"

    target_shape = majority_shape if target == "majority" else minority_shape

    for shape, cells in placed:
        input_color = random.choice(COLORS[:2])

        grid_input.fill_multiple_cells(cells, input_color)

        output_color = COLORS[2] if shape == target_shape else input_color
        grid_output.fill_multiple_cells(cells, output_color)

    params = make_params(
        event="recoloring",
        condition=["shape", "counting"],
        stimulus="cross_plus",
        colors=COLORS,
        n_objects=len(placed),
        counting_type=_counting_type(n_majority, n_minority, threshold=0.5),
        target=target,
        target_shape=target_shape,
        majority_shape=majority_shape,
    )

    return grid_input, grid_output, params


SHAPE_DIRECTIONS = {
    "plus": ((1, 0), (-1, 0), (0, 1), (0, -1)),
    "cross": ((1, 1), (1, -1), (-1, 1), (-1, -1)),
}


def _shape_cells(center, directions):
    row, col = center
    return [(row, col)] + [
        (row + dr, col + dc)
        for dr, dc in directions
    ]


def _place_non_overlapping_shapes(grid, shape_counts):
    candidates = grid.interior_cells()
    random.shuffle(candidates)

    shapes = [
        shape
        for shape, n in shape_counts.items()
        for _ in range(n)
    ]
    random.shuffle(shapes)

    used = set()
    placed = []

    for shape in shapes:
        for center in candidates:
            cells = _shape_cells(center, SHAPE_DIRECTIONS[shape])

            if any(cell in used for cell in cells):
                continue

            used.update(cells)
            placed.append((shape, cells))
            break

    return placed


def _sample_two_unique_counts(block_num):
    n1 = rand_between(*block_num)
    n2 = rand_between(*block_num)

    while n1 == n2:
        n2 = rand_between(*block_num)

    return n1, n2


def _counting_type(n_majority, n_minority, threshold=0.4):
    easiness = (n_majority - n_minority) / n_majority
    return "soft" if easiness >= threshold else "hard"
