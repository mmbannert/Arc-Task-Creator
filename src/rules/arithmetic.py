import random
from src.util import rand_between
from src.grid import Grid
from typing import Dict, Tuple, Any, List

import random


def generate_dot_majority_recolor(grid_size=(12, 12), block_num=(1, 6), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    color1, color2 = random.sample(colors, 2)
    n1 = rand_between(*block_num)
    n2 = rand_between(*block_num)

    # avoid ties
    while n1 == n2:
        n2 = rand_between(*block_num)

    # determine majority cleanly
    if n1 > n2:
        majority_color = color1
        minority_color = color2
        n_majority = n1
        n_minority = n2
    else:
        majority_color = color2
        minority_color = color1
        n_majority = n2
        n_minority = n1

    all_positions = random.sample(
        [(x, y) for x in range(cols) for y in range(rows)],
        n_majority + n_minority
    )

    majority_positions = all_positions[:n_majority]
    minority_positions = all_positions[n_majority:]

    for x, y in majority_positions:
        grid_input.fill_cell(x, y, majority_color)

    for x, y in minority_positions:
        grid_input.fill_cell(x, y, minority_color)

    for x, y in all_positions:
        grid_output.fill_cell(x, y, majority_color)

    # fixed threshold (no param)
    difficulty = (n_majority - n_minority) / n_majority
    counting_type = "soft" if difficulty >= 0.4 else "hard"

    params = {
        "event": "recoloring",
        "condition": ["color", "counting"],
        "stimulus": "dots",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": n_majority + n_minority,
        "counting_type": counting_type,
    }

    return grid_input, grid_output, params


def generate_dot_minority_recolor(grid_size=(12, 12), block_num=(1, 6), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    color1, color2 = random.sample(colors, 2)
    n1 = rand_between(*block_num)
    n2 = rand_between(*block_num)

    # avoid ties
    while n1 == n2:
        n2 = rand_between(*block_num)

    # determine majority cleanly
    if n1 < n2:
        majority_color = color1
        minority_color = color2
        n_majority = n1
        n_minority = n2
    else:
        majority_color = color2
        minority_color = color1
        n_majority = n2
        n_minority = n1

    all_positions = random.sample(
        [(x, y) for x in range(cols) for y in range(rows)],
        n_majority + n_minority
    )

    majority_positions = all_positions[:n_majority]
    minority_positions = all_positions[n_majority:]

    for x, y in majority_positions:
        grid_input.fill_cell(x, y, majority_color)

    for x, y in minority_positions:
        grid_input.fill_cell(x, y, minority_color)

    for x, y in all_positions:
        grid_output.fill_cell(x, y, majority_color)

    difficulty = (n_majority - n_minority) / n_majority
    counting_type = "soft" if difficulty >= 0.4 else "hard"

    params = {
        "event": "recoloring",
        "condition": ["color", "counting"],
        "stimulus": "dots",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": n_majority + n_minority,
        "counting_type": counting_type,
    }

    return grid_input, grid_output, params


# Needed for cross plus count
OFFSETS = {
    "plus": [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],  # 2,4,5,6,8
    "cross": [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],  # 1,3,5,7,9
}


def generate_cross_plus_majority_recolor(grid_size=(12, 12), stamp_num=(1, 6), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    k = rand_between(*stamp_num)

    candidates = [(r, c) for r in range(rows - 2) for c in range(cols - 2)]
    random.shuffle(candidates)

    used = set()
    placed: List[Tuple[str, List[Tuple[int, int]]]] = []

    for top_r, top_c in candidates:
        shape = random.choice(("cross", "plus"))
        cells = [(top_r + dr, top_c + dc) for dr, dc in OFFSETS[shape]]
        if any(cell in used for cell in cells):
            continue
        used.update(cells)
        placed.append((shape, cells))
        if len(placed) == k:
            break

    n_cross = sum(1 for shape, _ in placed if shape == "cross")
    n_plus = sum(1 for shape, _ in placed if shape == "plus")

    while n_cross == n_plus:
        return generate_cross_plus_majority_recolor(grid_size, stamp_num, colors)

    if n_cross > n_plus:
        majority_shape = "cross"
        minority_shape = "plus"
    else:
        majority_shape = "plus"
        minority_shape = "cross"

    out_map = {
        majority_shape: colors[0],
        minority_shape: colors[1],
    }

    for shape, cells in placed:
        input_color = random.choice(colors)
        for r, c in cells:
            grid_input.fill_cell(r, c, input_color)
            grid_output.fill_cell(r, c, out_map[shape])

    difficulty = abs(n_cross - n_plus) / max(n_cross, n_plus)
    counting_type = "soft" if difficulty >= 0.5 else "hard"

    params = {
        "event": "recoloring",
        "condition": ["shape", "counting"],
        "stimulus": "cross_plus",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": len(placed),
        "counting_type": counting_type,
    }

    return grid_input, grid_output, params
