import numpy as np


TRANSFORMATIONS = ["occlusion", "rotate_90", "rotate_270", "flip_h", "flip_v"]

N_TRIALS = 64
SWITCH_PROB = 1/3
MINIMUM_BLOCK_LENGTH = 3

INPUT_CSV_PATH = "out/examples/conditions.csv"
OUTPUT_CSV_PATH = "out/examples/opt5_conditions.csv"

conds = np.loadtxt(INPUT_CSV_PATH, delimiter=",", dtype=str, skiprows=1)

# Columns for the output file
trial_number = []
input_matrix = []
output_matrix = []
transformation = []
is_switch_trial = []

candidate_sample_ids = []
cur_transformation = None

# The very first trial is always a switch trial so that a new transition is
# picked randomly.
switch_trial = True

# Count the number of trials in current block. Make sure that each block has at 
# least MINIMUM_BLOCK_LENGTH trials of the same transformation.
cur_block_length = MINIMUM_BLOCK_LENGTH + 1

cur_transformation 

for trial_n in range(N_TRIALS):
    if (cur_block_length > MINIMUM_BLOCK_LENGTH and switch_trial) or len(candidate_sample_ids) == 0:
        cur_transformation = str(np.random.choice([trf for trf in TRANSFORMATIONS if not trf == cur_transformation]))
        cur_block_length = 0

        # Filter out samples with the current transformation
        candidate_samples = conds[conds[:, 0] == cur_transformation, :]

        # How many samples do we have?
        n_samples = candidate_samples.shape[0]

        # Create a list of all possible sample ids
        candidate_sample_ids = list(range(n_samples))

    # Pick one example at random
    sample_idx = np.random.randint(0, len(candidate_sample_ids))
    
    # Make sure that the same task will not be picked twice per block
    sample_idx = candidate_sample_ids.pop(sample_idx)

    # Get the input matrix of the chosen example
    input_matrix.append(str(candidate_samples[sample_idx, 3]))

    # Get the output matrix of the chosen example
    output_matrix.append(str(candidate_samples[sample_idx, 4]))

    trial_number.append(str(trial_n + 1))
    transformation.append(cur_transformation)
    is_switch_trial.append(str(int(switch_trial)))

    # Determine if the next trial will be a switch trial
    if np.random.rand() < SWITCH_PROB:
        switch_trial = True
    else:
        switch_trial = False

    cur_block_length += 1


# Create an array for the output CSV
output_conds = np.array([
    trial_number,
    input_matrix,
    output_matrix,
    transformation,
    is_switch_trial
]).T

# Save the output conditions to a CSV file
np.savetxt(
    OUTPUT_CSV_PATH, output_conds, delimiter=",", fmt="%s",
    header="trial_number,input_matrix,output_matrix,transformation,is_switch_trial",
    comments='')

    







    