import random
from typing import Dict, Tuple, Any, List
from src.grid import Grid
from src.util import rand_between


def generate_dot_inversion_recolor(grid_size=(12, 12), block_num=(1, 6), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    n1 = rand_between(*block_num)
    n2 = rand_between(*block_num)

    color1, color2 = random.sample(colors, 2)

    all_positions = random.sample([(x, y) for x in range(cols) for y in range(rows)], n1 + n2)
    color1_positions = all_positions[:n1]
    color2_positions = all_positions[n1:]

    for x, y in color1_positions:
        grid_input.fill_cell(x, y, color1)
    for x, y in color2_positions:
        grid_input.fill_cell(x, y, color2)

    for x, y in color1_positions:
        grid_output.fill_cell(x, y, color2)
    for x, y in color2_positions:
        grid_output.fill_cell(x, y, color1)

    params = {
        "event": "recoloring",
        "condition": "color",
        "stimulus": "dots",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": n1 + n2
    }

    return grid_input, grid_output, params


def generate_dot_neighbor_recolor(grid_size=(12, 12), block_num=(4, 8), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    n_objects = rand_between(*block_num)

    def neighbors(x, y):
        return [
            (x + dx, y + dy)
            for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            if (dx, dy) != (0, 0) and 0 <= x + dx < cols and 0 <= y + dy < rows
        ]

    all_positions = [(x, y) for x in range(cols) for y in range(rows)]
    random.shuffle(all_positions)

    # Pick one guaranteed adjacent pair and one guaranteed isolated dot
    pairs = [(a, b) for a in all_positions for b in neighbors(*a) if a < b]
    guaranteed_pair = random.choice(pairs)

    isolated = [p for p in all_positions if p not in guaranteed_pair
                and not any(n in set(guaranteed_pair) for n in neighbors(*p))]
    guaranteed_isolated = random.choice(isolated)

    occupied = set(guaranteed_pair) | {guaranteed_isolated}
    positions = list(occupied)

    # Fill remaining freely
    for pos in all_positions:
        if len(positions) >= n_objects:
            break
        if pos not in occupied:
            positions.append(pos)
            occupied.add(pos)

    for x, y in positions:
        grid_input.fill_cell(x, y, random.choice(colors))

    for x, y in positions:
        has_neighbor = any(n in occupied for n in neighbors(x, y))
        grid_output.fill_cell(x, y, colors[0] if has_neighbor else colors[1])

    params = {
        "event": "recoloring",
        "condition": ["shape", "neighbor"],
        "stimulus": "dots",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": len(positions)
    }

    return grid_input, grid_output, params


# Needed for cross plus recolor
OFFSETS = {
    "plus": [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],  # 2,4,5,6,8
    "cross": [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],  # 1,3,5,7,9
}


def generate_cross_plus_shape_fixed_recolor(grid_size=(12, 12), stamp_num=(3, 4), colors=("gray", "red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    k = rand_between(*stamp_num)
    out_map = {"cross": colors[1], "plus": colors[2]}

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

    for shape, cells in placed:
        for r, c in cells:
            grid_input.fill_cell(r, c, colors[0])
            grid_output.fill_cell(r, c, out_map[shape])

    params = {
        "event": "recoloring",
        "condition": "shape",
        "stimulus": "cross_plus",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": len(placed)
    }

    return grid_input, grid_output, params


def generate_cross_plus_cyclic_recolor(grid_size=(12, 12), stamp_num=(3, 4), colors=("gray", "red", "blue")):
    rows, cols = grid_size
    grid_input, grid_output = Grid(rows, cols), Grid(rows, cols)

    k = rand_between(*stamp_num)
    recolor_map = {
        colors[2]: colors[0],  # blue -> gray
        colors[0]: colors[1],  # gray -> red
        colors[1]: colors[2],  # red -> blue
    }

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

    for shape, cells in placed:
        input_color = random.choice(colors)
        output_color = recolor_map[input_color]

        for r, c in cells:
            grid_input.fill_cell(r, c, input_color)
            grid_output.fill_cell(r, c, output_color)

    params = {
        "event": "recoloring",
        "condition": "color",
        "stimulus": "cross_plus",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": len(placed)
    }

    return grid_input, grid_output, params
