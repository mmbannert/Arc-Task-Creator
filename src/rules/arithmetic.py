import random

from src.rules._common import make_grids, make_params
from src.config import COLORS
from src.util import rand_between


def generate_dot_majority_takeover_recolor(block_num=(1, 6)):
    return _generate_dot_counting_recolor(
        target="majority",
        block_num=block_num
    )


def generate_dot_minority_takeover_recolor(block_num=(1, 6)):
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


def generate_dot_equalize_recolor(block_num=(1, 4)):
    """
    Recolor FROM (majority) color INTO the minority color so both group shave same count.

    Choosing dots to recolor: bottom-most first, then left-most among ties
    """
    grid_input, grid_output = make_grids()

    color1, color2 = random.sample(COLORS[:2], 2)
    n1, n2 = _sample_two_unique_counts(block_num)

    while (n1 + n2) % 2 != 0:  # need an even total for an exact 50/50 split
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

    n_to_flip = (n_majority - n_minority) // 2  # exact, since n_majority+n_minority is even

    flip_positions = _bottom_left_first(majority_positions)[:n_to_flip]
    flip_set = set(flip_positions)
    kept_majority_positions = [p for p in majority_positions if p not in flip_set]

    grid_output.fill_multiple_cells(kept_majority_positions, majority_color)
    grid_output.fill_multiple_cells(flip_positions, minority_color)
    grid_output.fill_multiple_cells(minority_positions, minority_color)

    params = make_params(
        event="recoloring",
        condition=["color", "counting"],
        stimulus="dots",
        colors=(majority_color, minority_color),
        n_objects=n_majority + n_minority,
        counting_type=_counting_type(n_majority, n_minority),
        target="equalize",
        n_recolored=n_to_flip,
    )

    return grid_input, grid_output, params


def generate_dot_majority_increment_recolor(block_num=(2, 3)):
    """
    Recolor one minority-color dot into the majority color,
    increasing the difference between the two color counts by 2.

    The recolored dot is chosen deterministically:
    bottommost first, then leftmost among ties.
    """
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

    flip_position = _bottom_left_first(minority_positions)[0]

    kept_minority_positions = [
        pos for pos in minority_positions
        if pos != flip_position
    ]

    grid_output.fill_multiple_cells(majority_positions, majority_color)
    grid_output.fill_cell(*flip_position, majority_color)
    grid_output.fill_multiple_cells(kept_minority_positions, minority_color)

    params = make_params(
        event="recoloring",
        condition=["color", "counting"],
        stimulus="dots",
        colors=(majority_color, minority_color),
        n_objects=n_majority + n_minority,
        counting_type=_counting_type(n_majority, n_minority),
        target="diff_two",
        n_recolored=1,
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
