# ARC-fMRI

Code and materials for an fMRI experiment investigating **rule inference** using ARC-like matrix transformations.

The repository consists of two main components:

- **ARC Rule Generator**: Python framework for generating visual stimuli representing ARC-like transformation rules.
- **Experiment**: Code and materials for the fMRI experiment and pilot studies.

---

## ARC Rule Generator

The rule generator creates pairs of grids, an **input** and its corresponding **output**, according to different transformation rule families:

- **Arithmetic** (e.g. majority/minority takeover, equalization, increment)
- **Attraction** (e.g. attraction, repulsion, falling, floating)
- **Recoloring** (e.g. color inversion, shape-based recoloring)
- **Expansion** (e.g. plus, star, diagonal growth)
- **Occlusion** (e.g. occlusion reversal, mirroring, rotation)

Each rule is implemented as a separate function, with rule families organized into individual Python modules.

## Experiment

The experiment investigates how people infer abstract transformation rules and judge whether the current rule is the same as or different from a reference rule, either the previous rule or a rule memorized at the start of the block. Each trial presents two input-output examples of the same hidden rule.

Counterbalanced participant sessions are generated as JSON files with a Python script and run separately in MATLAB using Psychtoolbox. The MATLAB runner handles stimulus presentation, responses and timing, scanner synchronization, EyeLink recording, and experiment logging.

---

## Repository Structure

```
arc-fmri/
├── arc_rule_generator/          # Generate ARC-like stimulus pairs
│   ├── rules/                   # Rule implementations, grouped by rule family
│   ├── grid.py                  # Grid representation and transformations
│   ├── stimulus.py              # Stimulus metadata representation
│   ├── visualize.py             # Render input/output grids as images
│   └── main.py                  # Entry point for stimulus generation
│
├── experiment/
│   ├── docs/                    # Questionnaires and experiment-related documents
│   ├── fMRI/                    # Scanner version of the experiment
│   │   ├── +utilities/          # MATLAB utilities for display, logging, EyeLink, etc.
│   │   ├── stimuli/             # Stimulus images used in the fMRI experiment
│   │   ├── build_session.py     # Build counterbalanced session JSON files
│   │   └── run_experiment.m     # Main MATLAB/Psychtoolbox experiment runner
│   └── pilot/                   # Online/behavioral pilot experiment
```

## Author & Acknowledgments

**Yavuz Karaca**, **Dr. Michael Bannert**

Special thanks to **Prof. Dr. Martin V. Butz** and **Prof. Dr. Andreas Bartels** for designing the experimental paradigm, their constructive feedback and ideas during the development.



