import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt


def save_grid(grid, save_path="output.png"):
    rows, cols = grid.rows, grid.cols
    color_grid = grid.as_list()

    # Convert color names/hex to normalized RGB
    rgb_grid = np.array([
        [mcolors.to_rgb(color_grid[r][c]) for c in range(cols)]
        for r in range(rows)
    ])

    fig, ax = plt.subplots(figsize=(cols, rows))
    fig.patch.set_facecolor("gray")
    ax.imshow(rgb_grid, interpolation='none', extent=(0, cols, rows, 0))

    # Draw vertical and horizontal gridlines
    for x in range(cols + 1):
        ax.axvline(x, color='gray', linewidth=2)
    for y in range(rows + 1):
        ax.axhline(y, color='gray', linewidth=2)

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.savefig(save_path, dpi=100, bbox_inches='tight', pad_inches=0.03)

    plt.close()


def save_combined_grids(grid1, grid2, save_path="combined.png"):
    rows1, cols1 = grid1.rows, grid1.cols
    rows2, cols2 = grid2.rows, grid2.cols

    rgb_grid1 = np.array([
        [mcolors.to_rgb(grid1.as_list()[r][c]) for c in range(cols1)]
        for r in range(rows1)
    ])
    rgb_grid2 = np.array([
        [mcolors.to_rgb(grid2.as_list()[r][c]) for c in range(cols2)]
        for r in range(rows2)
    ])

    fig, axs = plt.subplots(
        1, 2,
        figsize=(cols1 + cols2 + 2, max(rows1, rows2)),  # extra horizontal room
        gridspec_kw={'wspace': 0.25}  # space for arrow
    )
    fig.patch.set_facecolor("gray")

    fig.text(
        0.51,  # horizontal center of figure
        0.5,  # vertical center
        "→",
        ha="center",
        va="center",
        fontsize=140,
        color="white",
        fontweight="bold"
    )

    # First grid
    axs[0].imshow(rgb_grid1, interpolation='none', extent=(0, cols1, rows1, 0))
    for x in range(cols1 + 1):
        axs[0].axvline(x, color='dimgray', linewidth=2)
    for y in range(rows1 + 1):
        axs[0].axhline(y, color='dimgray', linewidth=2)
    axs[0].set_xlim(0, cols1)
    axs[0].set_ylim(0, rows1)
    axs[0].set_aspect('equal')
    axs[0].axis('off')

    # Second grid
    axs[1].imshow(rgb_grid2, interpolation='none', extent=(0, cols2, rows2, 0))
    for x in range(cols2 + 1):
        axs[1].axvline(x, color='dimgray', linewidth=2)
    for y in range(rows2 + 1):
        axs[1].axhline(y, color='dimgray', linewidth=2)
    axs[1].set_xlim(0, cols2)
    axs[1].set_ylim(0, rows2)
    axs[1].set_aspect('equal')
    axs[1].axis('off')

    plt.savefig(save_path, dpi=100, bbox_inches='tight', pad_inches=0.03)
    plt.close()
