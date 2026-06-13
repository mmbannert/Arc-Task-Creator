# Arc Rule Generator

Python-based framework for generating **ARC-like matrix transformation rules**. 
These matrices are used as visual stimuli for research on **rule inference and rule application** processes in humans.

---

## Overview

The project generates pairs of grids (an **input** and its corresponding **output**) based on specific transformation rule families such as:

- **Expansion** (e.g. star, plus, diagonal, single-step / infinite growth)
- **Attraction/repulsion** (e.g. pull, push, fall, float)
- **Occlusion** (e.g. occlusion reversal, or mirroring/rotation on occluding objects)
- **Recolor** (e.g. shape based recoloring)
- **Arithmetic** (e.g. inversion, counting, majority/minority, parity)

Each rule is implemented as a separate function, and families of rules are organized within .py modules.

---

## Repository Structure

```
ArcRuleGenerator/
├── experiment/                # fMRI experiment, pilot experiment design, data, analysis, source files
├── out/                       # Generated examples organized by rule type
└── src/
    ├── rules/    
    │   ├── attraction.py
    │   ├── attraction.py
    │   ├── recolor.py
    │   ├── expansion.py
    │   └── occlusion.py
    ├── grid.py                # Grid logic and data structure
    ├── stimulus.py            # Stimulus dataclass for JSON dataset overview
    ├── util.py                # Helper functions
    ├── visualize.py           # Visualization i.e. figure generation
    └── main.py                # Main entry point for task generation
```

## Author & Acknowledgments

**Yavuz Karaca**, **Dr. Michael Bannert**

Special thanks to **Prof. Dr. Martin V. Butz** and **Prof. Dr. Andreas Bartels** for designing the experimental paradigm in which these tasks are used, but also for their constructive feedback and ideas during the development.



