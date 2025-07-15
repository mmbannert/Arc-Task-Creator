from src.visualize import render_grid, render_grids_together
from src.templates.occlusion import generate_occlusion_reversal_rectangles
from src.util import get_output_path
from pathlib import Path
from PIL import Image

N_EXAMPLES = 18

COLOR_PAIRS = [
    ("red", "green"),
    ("blue", "yellow"),
    ("red", "blue"),
    ("green", "yellow"),
    ("red", "yellow"),
    ("blue", "green"),
]

OUTDIR = "out/examples"

n_color_pairs = len(COLOR_PAIRS)

def main():

    for i in range(N_EXAMPLES):

        cur_color_pair = COLOR_PAIRS[i % n_color_pairs]
        cur_input_path = OUTDIR / Path(f"stim{i:03d}_{cur_color_pair[0]}" \
                               f"-{cur_color_pair[1]}_input.png")
        cur_output_path = OUTDIR / Path(f"stim{i:03d}_{cur_color_pair[0]}" \
                               f"-{cur_color_pair[1]}_output.png")

        if not cur_output_path.exists():
            cur_output_path.parent.mkdir(parents=True, exist_ok=True)

        input_grid, output_grid = generate_occlusion_reversal_rectangles(
            colors=cur_color_pair)

        render_grid(input_grid, save_path=cur_input_path)
        render_grid(output_grid, save_path=cur_output_path)
        
        # Load the input image
        input_img = Image.open(cur_input_path)

        # Output names for my own "simple", non-ARC transformations
        vflip_output_path = OUTDIR / Path(f"stim{i:03d}_{cur_color_pair[0]}" \
                                 f"-{cur_color_pair[1]}_vflip.png")
        hflip_output_path = OUTDIR / Path(f"stim{i:03d}_{cur_color_pair[0]}" \
                                 f"-{cur_color_pair[1]}_hflip.png")
        cw_output_path = OUTDIR / Path(f"stim{i:03d}_{cur_color_pair[0]}" \
                                 f"-{cur_color_pair[1]}_cw.png")
        ccw_output_path = OUTDIR / Path(f"stim{i:03d}_{cur_color_pair[0]}" \
                                 f"-{cur_color_pair[1]}_ccw.png")

        # Vertical flip
        vflip_img = input_img.transpose(Image.FLIP_TOP_BOTTOM)
        vflip_img.save(vflip_output_path)

        # Horizontal flip
        hflip_img = input_img.transpose(Image.FLIP_LEFT_RIGHT)
        hflip_img.save(hflip_output_path)

        # Clockwise rotation
        cw_img = input_img.transpose(Image.ROTATE_270)  # 90 degrees clockwise
        cw_img.save(cw_output_path)

        # Counter-clockwise rotation
        ccw_img = input_img.transpose(Image.ROTATE_90)  # 90 degrees counter-clockwise
        ccw_img.save(ccw_output_path)


if __name__ == '__main__':
    main()
