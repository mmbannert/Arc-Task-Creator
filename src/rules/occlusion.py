import random
from src.grid import Grid


def generate_occlusion_mirror_x(grid_size=(12, 12), size_range=(2, 5), colors=("red", "blue")):
    grid_input, _, _ = generate_occlusion_reversal(
        grid_size=grid_size, size_range=size_range, colors=colors
    )

    grid_output = grid_input.copy()
    _transform_occupied_box(grid_output, lambda f: f.mirror_x())

    params = {
        "event": "mirror",
        "condition": "shape",
        "stimulus": "occluding_blocks",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": 2
    }

    return grid_input, grid_output, params


def generate_occlusion_mirror_y(grid_size=(12, 12), size_range=(2, 5), colors=("red", "blue")):
    grid_input, _, _ = generate_occlusion_reversal(
        grid_size=grid_size, size_range=size_range, colors=colors
    )

    grid_output = grid_input.copy()
    _transform_occupied_box(grid_output, lambda f: f.mirror_y())

    params = {
        "event": "mirror",
        "condition": "shape",
        "stimulus": "occluding_blocks",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": 2
    }

    return grid_input, grid_output, params


def generate_occlusion_rotate_90(grid_size=(12, 12), size_range=(2, 5), colors=("red", "blue")):
    grid_input, _, _ = generate_occlusion_reversal(
        grid_size=grid_size, size_range=size_range, colors=colors
    )

    grid_output = grid_input.copy()
    _transform_occupied_square_box(grid_output, lambda f: f.rotate_ccw_90())

    params = {
        "event": "rotation",
        "condition": "shape",
        "stimulus": "occluding_blocks",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": 2
    }

    return grid_input, grid_output, params


def generate_occlusion_rotate_180(grid_size=(12, 12), size_range=(2, 5), colors=("red", "blue")):
    grid_input, _, _ = generate_occlusion_reversal(
        grid_size=grid_size, size_range=size_range, colors=colors
    )

    grid_output = grid_input.copy()
    _transform_occupied_box(grid_output, lambda f: f.rotate_180())

    params = {
        "event": "rotation",
        "condition": "shape",
        "stimulus": "occluding_blocks",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": 2
    }

    return grid_input, grid_output, params


def _transform_occupied_box(grid, transform_fn):
    row_min, row_max, col_min, col_max = grid.get_occupied_bounding_box()
    box = grid.extract_box(row_min, row_max, col_min, col_max)
    transform_fn(box)
    grid.paste_at(box, row_min, col_min)


def _transform_occupied_square_box(grid, transform_fn):
    # Needed for rotate 90 because otherwise the dimensions do not fit
    row_min, row_max, col_min, col_max = grid.get_occupied_bounding_box()
    row_min, row_max, col_min, col_max = _make_square_box(
        row_min, row_max, col_min, col_max, grid.rows, grid.cols
    )
    box = grid.extract_box(row_min, row_max, col_min, col_max)
    transform_fn(box)
    grid.paste_at(box, row_min, col_min)


def _make_square_box(row_min, row_max, col_min, col_max, max_rows, max_cols):
    h = row_max - row_min + 1
    w = col_max - col_min + 1
    side = max(h, w)

    row_max = min(row_min + side - 1, max_rows - 1)
    col_max = min(col_min + side - 1, max_cols - 1)

    row_min = row_max - side + 1
    col_min = col_max - side + 1

    return row_min, row_max, col_min, col_max


def generate_occlusion_reversal(grid_size=(12, 12), size_range=(2, 5), colors=("red", "blue")):
    rows, cols = grid_size
    grid_input = Grid(rows, cols)
    grid_output = Grid(rows, cols)

    w, h = random.randint(*size_range), random.randint(*size_range)

    # Random position for back block (x and y of bottom left corner of the back block)
    x1 = random.randint(min(size_range), cols - w - min(size_range))
    y1 = random.randint(min(size_range), rows - h - min(size_range))
    back_block = {"col_min": x1, "row_min": y1, "col_max": x1 + w, "row_max": y1 + h, "color": colors[0]}

    min_x2 = x1 + 1
    max_x2 = x1 + w - 1
    min_y2 = y1 + 1
    max_y2 = y1 + h - 1

    x2 = random.randint(min_x2, max_x2)
    y2 = random.randint(min_y2, max_y2)

    front_block = {"col_min": x2, "row_min": y2, "col_max": x2 + w, "row_max": y2 + h, "color": colors[1]}

    # Input: back first, front second
    grid_input.fill_rect(**back_block)
    grid_input.fill_rect(**front_block)

    # Output: front first, back second (reversed)
    grid_output.fill_rect(**front_block)
    grid_output.fill_rect(**back_block)

    for _ in range(random.randrange(4)):  # Rotate few times to generate all variations
        grid_input.rotate_ccw_90()
        grid_output.rotate_ccw_90()

    params = {
        "event": "occlusion_reversal",
        "condition": "shape",
        "stimulus": "occluding_blocks",
        "grid_size": grid_size,
        "colors": colors,
        "n_objects": 2
    }

    return grid_input, grid_output, params
