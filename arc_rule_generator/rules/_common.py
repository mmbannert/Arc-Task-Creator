from arc_rule_generator.grid import Grid
from arc_rule_generator.config import GRID_SIZE


def make_grids():
    rows, cols = GRID_SIZE
    return Grid(rows, cols), Grid(rows, cols)


def make_params(event, condition, stimulus, colors, n_objects, **extra):
    return {
        "event": event,
        "condition": condition,
        "stimulus": stimulus,
        "colors": colors,
        "n_objects": n_objects,
        **extra
    }
