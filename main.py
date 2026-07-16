import random
from pathlib import Path

from src.visualize import save_grid, save_combined_grids
from src.stimulus import Stimulus
from src.util import append_jsonl, next_idx, new_seed

from src.rules.recolor import (
    generate_cross_plus_shape_fixed_recolor,
    generate_dot_inversion_recolor,
    generate_dot_neighbor_recolor,
    generate_cross_plus_cyclic_recolor,
)

from src.rules.arithmetic import (
    generate_dot_majority_recolor,
    generate_dot_minority_recolor,
    generate_cross_plus_majority_recolor, generate_cross_plus_minority_recolor,
)

from src.rules.expansion import (
    generate_star_expansion_single_step,
    generate_star_expansion_ray,
    generate_plus_expansion_single_step,
    generate_plus_expansion_ray,
    generate_3arm_star_expansion_ray,
    generate_8_arm_star_expansion_ray
)

from src.rules.occlusion import (
    generate_occlusion_reversal,
    generate_occlusion_mirror_x,
    generate_occlusion_mirror_y,
    generate_occlusion_rotate_90,
    generate_occlusion_rotate_180,
)

from src.rules.attraction import (
    generate_color_attraction,
    generate_size_attraction,
    generate_color_repulsion,
    generate_falling_blocks,
    generate_float,
    generate_falling_dots,
)


def main(N):
    rules = {
        "occlusion.occlusion_reversal": generate_occlusion_reversal,
        "occlusion.occlusion_mirror_x": generate_occlusion_mirror_x,
        "occlusion.occlusion_mirror_y": generate_occlusion_mirror_y,
        "occlusion.occlusion_rotate_90": generate_occlusion_rotate_90,
        "occlusion.occlusion_rotate_180": generate_occlusion_rotate_180,
        "attraction.color_attraction": generate_color_attraction,
        "attraction.size_attraction": generate_size_attraction,
        "attraction.falling_blocks": generate_falling_blocks,
        "attraction.float": generate_float,
        "attraction.color_repulsion": generate_color_repulsion,
        "expansion.star_step": generate_star_expansion_single_step,
        "expansion.star_ray": generate_star_expansion_ray,
        "expansion.plus_step": generate_plus_expansion_single_step,
        "expansion.plus_ray": generate_plus_expansion_ray,
        "expansion.3arm_star_ray": generate_3arm_star_expansion_ray,
        "arithmetic.dot_majority_recolor": generate_dot_majority_recolor,
        "arithmetic.dot_minority_recolor": generate_dot_minority_recolor,
        "arithmetic.cross_plus_majority_recolor": generate_cross_plus_majority_recolor,
        "arithmetic.cross_plus_minority_recolor": generate_cross_plus_minority_recolor,
        "recoloring.dot_inversion_recolor": generate_dot_inversion_recolor,
        "recoloring.dot_neighbor_recolor": generate_dot_neighbor_recolor,
        "recoloring.cross_plus_shape_fixed_recolor": generate_cross_plus_shape_fixed_recolor,
        "recoloring.cross_plus_cyclic_recolor": generate_cross_plus_cyclic_recolor,
    }

    for name, gen in rules.items():
        for _ in range(N):
            _generate_stimulus(name, gen)


def _generate_stimulus(rule: str, gen, out_root: str = "out") -> None:
    base = Path(out_root) / rule
    base.mkdir(parents=True, exist_ok=True)
    jsonl_path = base / "stimuli.jsonl"

    idx = next_idx(jsonl_path)
    seed = new_seed()
    random.seed(seed)

    produced = gen()
    inp, out, params = (*produced, {})[:3]

    stim_id = f"{rule}.t{idx}"
    p_in = base / f"{stim_id}.input.png"
    p_out = base / f"{stim_id}.output.png"
    p_comb = base / f"{stim_id}.combined.png"

    # Separate stimuli currently not needed. Useful when participant picks correct output from multiple options.
    # save_grid(inp, str(p_in))
    # save_grid(out, str(p_out))

    save_combined_grids(inp, out, str(p_comb))

    family = rule.split(".", 1)[0]
    rule_name = rule.rsplit(".", 1)[-1]

    stim = Stimulus(
        id=stim_id,
        rule=rule_name,
        family=family,
        seed=seed,
        params=params
    )

    rec = stim.to_json_dict()
    append_jsonl(jsonl_path, rec)


if __name__ == "__main__":
    main(40)
