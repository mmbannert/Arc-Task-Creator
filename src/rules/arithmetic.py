import random

from src.rules._common import make_grids, make_params
from src.config import COLORS
from src.util import rand_between


def generate_majority_takeover(block_num=(1, 6)):
    return _generate_dot_counting_recolor(
        target="majority",
        block_num=block_num
    )


def generate_minority_takeover(block_num=(1, 6)):
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
        grid_input.get_coordinates(),
        n_majority + n_minority
    )

    majority_positions = all_positions[:n_majority]
    minority_positions = all_positions[n_majority:]

    grid_input.set_multi_cells(majority_positions, majority_color)
    grid_input.set_multi_cells(minority_positions, minority_color)

    target_color = majority_color if target == "majority" else minority_color
    grid_output.set_multi_cells(all_positions, target_color)

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

def generate_equalize_colors(block_num=(1, 4)):
    return _generate_dot_arithmetic_recolor(
        operation="equalize",
        block_num=block_num,
    )


def generate_increment_majority_color(block_num=(2, 3)):
    return _generate_dot_arithmetic_recolor(
        operation="majority_increment",
        block_num=block_num,
    )


def generate_increment_minority_color(block_num=(2, 3)):
    return _generate_dot_arithmetic_recolor(
        operation="minority_increment",
        block_num=block_num,
    )


def _generate_dot_arithmetic_recolor(operation, block_num):
    grid_input, _ = make_grids()

    n1, n2 = _sample_two_unique_counts(block_num)

    if operation == "equalize":
        while (n1 + n2) % 2 != 0:
            n1, n2 = _sample_two_unique_counts(block_num)

    n_majority = max(n1, n2)
    n_minority = min(n1, n2)

    majority_color, minority_color = random.sample(COLORS[:2], 2)

    all_positions = random.sample(
        grid_input.get_coordinates(),
        n_majority + n_minority,
    )

    majority_positions = all_positions[:n_majority]
    minority_positions = all_positions[n_majority:]

    grid_input.set_multi_cells(majority_positions, majority_color)
    grid_input.set_multi_cells(minority_positions, minority_color)

    grid_output = grid_input.copy()

    if operation == "equalize":
        n_to_flip = (n_majority - n_minority) // 2
        source_positions = majority_positions
        target_color = minority_color

    elif operation == "majority_increment":
        n_to_flip = 1
        source_positions = minority_positions
        target_color = majority_color

    elif operation == "minority_increment":
        n_to_flip = 1
        source_positions = majority_positions
        target_color = minority_color

    flip_positions = _bottom_left_first(source_positions)[:n_to_flip]
    grid_output.set_multi_cells(flip_positions, target_color)

    params = make_params(
        event="recoloring",
        condition=["color", "counting"],
        stimulus="dots",
        colors=(majority_color, minority_color),
        n_objects=n_majority + n_minority,
        counting_type=_counting_type(n_majority, n_minority),
        target=operation,
        n_recolored=n_to_flip,
    )

    return grid_input, grid_output, params

def _bottom_left_first(positions):
    """Sort (row, col) positions bottommost first, then leftmost."""
    return sorted(positions)


def _sample_two_unique_counts(block_num):
    n1 = rand_between(*block_num)
    n2 = rand_between(*block_num)

    while n1 == n2:
        n2 = rand_between(*block_num)

    return n1, n2


def _counting_type(n_majority, n_minority, threshold=0.4):
    easiness = (n_majority - n_minority) / n_majority
    return "soft" if easiness >= threshold else "hard"
