from pathlib import Path
import pandas as pd
import numpy as np


STIM_DIR = Path("out/examples")

TRANSFORMATIONS = ["occlusion", "rotate_90", "rotate_270", "flip_h", "flip_v"]

N_REPETITIONS = 10

# Where stimuli are stored in PsychoPy project
PREFIX_DIR = Path("images")

n_transformations = len(TRANSFORMATIONS)
df = pd.DataFrame(columns=[
    "sample_transformation", "probe_transformation", "correct",
    "sample1_in", "sample1_out", "sample2_in", "sample2_out", "sample3_in",
    "sample3_out", "probe_in", "probe_out", "probe_target", "probe_distractor1",
    "probe_distractor2", "probe_distractor3"
])

n_distractors = len([col_name for col_name in df.columns if "probe_distractor" \
                     in col_name])

# How many unique input stimuli exist in the stimulus directory?
input_stim = [str(inps) for inps in STIM_DIR.glob("stim*input.png")]

# Put together sets of stimuli for each trial. Each "repetition" consists of a
# trial where sample and probe transformations match and a trial where the probe
# transformation is randomly selected from the rest of the transformations.
for rep in range(N_REPETITIONS):
    for trf in TRANSFORMATIONS:
        for match in [True, False]:

            # Randomly choose 2 sample inputs and 1 probe input
            sample1_in_id, sample2_in_id, sample3_in_id, probe_in_id = \
                np.random.permutation(len(input_stim))[:4]
            
            sample1_in = input_stim[sample1_in_id]
            sample2_in = input_stim[sample2_in_id]
            sample3_in = input_stim[sample3_in_id]
            probe_in = input_stim[probe_in_id]
            
            if trf == "occlusion":
                # For occlusion, we use the same input for both sample and probe
                sample1_out = str(sample1_in).replace("_input.png", "_output.png")
                sample2_out = str(sample2_in).replace("_input.png", "_output.png")
                sample3_out = str(sample3_in).replace("_input.png", "_output.png")
                probe_target = str(probe_in).replace("_input.png", "_output.png")
                
            elif trf == "rotate_90":
                sample1_out = str(sample1_in).replace("_input.png", "_ccw.png")
                sample2_out = str(sample2_in).replace("_input.png", "_ccw.png")
                sample3_out = str(sample3_in).replace("_input.png", "_ccw.png")
                probe_target = str(probe_in).replace("_input.png", "_ccw.png")

            elif trf == "rotate_270":
                sample1_out = str(sample1_in).replace("_input.png", "_cw.png")
                sample2_out = str(sample2_in).replace("_input.png", "_cw.png")
                sample3_out = str(sample3_in).replace("_input.png", "_cw.png")
                probe_target = str(probe_in).replace("_input.png", "_cw.png")

            elif trf == "flip_h":
                sample1_out = str(sample1_in).replace("_input.png", "_hflip.png")
                sample2_out = str(sample2_in).replace("_input.png", "_hflip.png")
                sample3_out = str(sample3_in).replace("_input.png", "_hflip.png")
                probe_target = str(probe_in).replace("_input.png", "_hflip.png")

            elif trf == "flip_v":
                sample1_out = str(sample1_in).replace("_input.png", "_vflip.png")
                sample2_out = str(sample2_in).replace("_input.png", "_vflip.png")
                sample3_out = str(sample3_in).replace("_input.png", "_vflip.png")
                probe_target = str(probe_in).replace("_input.png", "_vflip.png")

            else:
                raise ValueError(f"Unknown sample transformation: {trf}")


            if match:
                probe_trf = trf
            else:
                probe_trf = np.random.choice(
                    [t for t in TRANSFORMATIONS if t != trf])
                
            if probe_trf == "occlusion":
                probe_out = str(probe_in).replace("_input.png", "_output.png")
            elif probe_trf == "rotate_90":
                probe_out = str(probe_in).replace("_input.png", "_ccw.png")
            elif probe_trf == "rotate_270":
                probe_out = str(probe_in).replace("_input.png", "_cw.png")
            elif probe_trf == "flip_h":
                probe_out = str(probe_in).replace("_input.png", "_hflip.png")
            elif probe_trf == "flip_v":
                probe_out = str(probe_in).replace("_input.png", "_vflip.png")
            else:
                raise ValueError(f"Unknown probe transformation: {probe_trf}")
            
            distractor_trf = np.random.choice(
                [t for t in TRANSFORMATIONS if t != trf], size=n_distractors,
                replace=False)
            probe_distractors = []
            for d_trf in distractor_trf:
                if d_trf == "occlusion":
                    probe_distractors.append(
                        str(probe_in).replace("_input.png", "_output.png"))
                elif d_trf == "rotate_90":
                    probe_distractors.append(
                        str(probe_in).replace("_input.png", "_ccw.png"))
                elif d_trf == "rotate_270":
                    probe_distractors.append(
                        str(probe_in).replace("_input.png", "_cw.png"))
                elif d_trf == "flip_h":
                    probe_distractors.append(
                        str(probe_in).replace("_input.png", "_hflip.png"))
                elif d_trf == "flip_v":
                    probe_distractors.append(
                        str(probe_in).replace("_input.png", "_vflip.png"))
                else:
                    raise ValueError(f"Unknown distractor transformation: {d_trf}")

            # Convert all paths to Path objects
            sample1_in = Path(sample1_in)
            sample2_in = Path(sample2_in)
            sample3_in = Path(sample3_in)
            sample1_out = Path(sample1_out)
            sample2_out = Path(sample2_out)
            sample3_out = Path(sample3_out)
            probe_in = Path(probe_in)
            probe_out = Path(probe_out)
            probe_target = Path(probe_target)
            probe_distractors = [Path(d) for d in probe_distractors]

            # Add the trial to the DataFrame
            df.loc[len(df)] = [
                trf, probe_trf,
                int(match), 
                PREFIX_DIR / sample1_in.name, 
                PREFIX_DIR / sample1_out.name,
                PREFIX_DIR / sample2_in.name, 
                PREFIX_DIR / sample2_out.name,
                PREFIX_DIR / sample3_in.name, 
                PREFIX_DIR / sample3_out.name,
                PREFIX_DIR / probe_in.name, 
                PREFIX_DIR / probe_out.name,
                PREFIX_DIR / probe_target.name,
            ] + [PREFIX_DIR / d.name for d in probe_distractors]

# Save the DataFrame to a CSV file
df.to_csv("out/examples/conditions.csv", index=False)
   

    
