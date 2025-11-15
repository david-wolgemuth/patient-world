"""Population diffusion helpers."""
from __future__ import annotations

from .state import GridState


def apply_diffusion(state: GridState, rabbit_rate: float = 0.1, fox_rate: float = 0.15) -> GridState:
    """Spread rabbits and foxes to adjacent cells."""
    new_state = state.clone()
    for y in range(state.grid_height):
        for x in range(state.grid_width):
            _diffuse_cell(state, new_state, x, y, rabbit_rate, fox_rate)
    return new_state


def _diffuse_cell(
    original: GridState,
    target: GridState,
    x: int,
    y: int,
    rabbit_rate: float,
    fox_rate: float,
) -> None:
    neighbors = original.neighbors(x, y)
    if not neighbors:
        return
    source_orig = original.get_cell(x, y)
    source_new = target.get_cell(x, y)

    moving_rabbits = int(source_orig.rabbits * rabbit_rate)
    moving_foxes = int(source_orig.foxes * fox_rate)

    rabbit_share = moving_rabbits // len(neighbors)
    fox_share = moving_foxes // len(neighbors)

    for nx, ny in neighbors:
        neighbor = target.get_cell(nx, ny)
        neighbor.rabbits = max(0, neighbor.rabbits + rabbit_share)
        neighbor.foxes = max(0, neighbor.foxes + fox_share)

    source_new.rabbits = max(0, source_new.rabbits - rabbit_share * len(neighbors))
    source_new.foxes = max(0, source_new.foxes - fox_share * len(neighbors))
