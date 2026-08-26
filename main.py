import random
from pathlib import Path

from src.visualize import save_grid, save_combined_grids
from src.stimulus import Stimulus
from src.util import append_jsonl, next_idx

from src.rules.recolor import (
    generate_shape_color_mapping,
    generate_touching_edges_recolor,
    generate_color_inversion
)

from src.rules.arithmetic import (
    generate_minority_takeover,
    generate_majority_takeover,
    generate_equalize_colors,
    generate_increment_majority_color,
    generate_increment_minority_color
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
        "occlusion.mirror_x": generate_occlusion_mirror_x,
        "occlusion.mirror_y": generate_occlusion_mirror_y,
        "occlusion.rotate_90": generate_occlusion_rotate_90,
        "occlusion.rotate_180": generate_occlusion_rotate_180,
        "attraction.color_attraction": generate_color_attraction,
        "attraction.size_attraction": generate_size_attraction,
        "attraction.falling_blocks": generate_falling_blocks,
        "attraction.float": generate_float,
        "attraction.color_repulsion": generate_color_repulsion,
        "expansion.star_step": generate_star_expansion_single_step,
        "expansion.star_ray": generate_star_expansion_ray,
        "expansion.plus_step": generate_plus_expansion_single_step,
        "expansion.plus_ray": generate_plus_expansion_ray,
        "expansion.3_arm_star_ray": generate_3arm_star_expansion_ray,
        "arithmetic.minority_takeover": generate_minority_takeover,
        "arithmetic.majority_takeover": generate_majority_takeover,
        "arithmetic.equalize_colors": generate_equalize_colors,
        "arithmetic.increment_majority_color": generate_increment_majority_color,
        "arithmetic.increment_minority_color": generate_increment_minority_color,
        "recolor.shape_color_mapping": generate_shape_color_mapping,
        "recolor.touching_edges_recolor": generate_touching_edges_recolor,
        "recolor.color_inversion": generate_color_inversion,
    }

    for name, gen in rules.items():
        for _ in range(N):
            _generate_stimulus(name, gen)


def _generate_stimulus(rule: str, gen, out_root: str = "out") -> None:
    base = Path(out_root) / rule
    base.mkdir(parents=True, exist_ok=True)
    jsonl_path = base / "stimuli.jsonl"

    idx = next_idx(jsonl_path)

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
        params=params
    )

    rec = stim.to_json_dict()
    append_jsonl(jsonl_path, rec)


if __name__ == "__main__":
    main(40)
