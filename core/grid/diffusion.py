"""Population diffusion helpers."""
from __future__ import annotations

from .state import GridState


def apply_diffusion(state: GridState, rabbit_rate: float = 0.1, fox_rate: float = 0.15) -> GridState:
    """Spread rabbits and foxes across orthogonal neighbors."""
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

    rabbit_share, rabbit_remainder = divmod(moving_rabbits, len(neighbors))
    fox_share, fox_remainder = divmod(moving_foxes, len(neighbors))

    for idx, (nx, ny) in enumerate(neighbors):
        neighbor = target.get_cell(nx, ny)
        rabbits_to_add = rabbit_share + (1 if idx < rabbit_remainder else 0)
        foxes_to_add = fox_share + (1 if idx < fox_remainder else 0)
        if rabbits_to_add:
            neighbor.rabbits = max(0, neighbor.rabbits + rabbits_to_add)
        if foxes_to_add:
            neighbor.foxes = max(0, neighbor.foxes + foxes_to_add)

    source_new.rabbits = max(
        0,
        source_new.rabbits - rabbit_share * len(neighbors) - rabbit_remainder,
    )
    source_new.foxes = max(
        0,
        source_new.foxes - fox_share * len(neighbors) - fox_remainder,
    )
