"""Grid tick logic."""
from __future__ import annotations

from .cell import Cell
from .diffusion import apply_diffusion
from .state import GridState


def tick_cell(cell: Cell) -> Cell:
    """Compute next cell state using local-only interactions."""
    grass = min(100, cell.grass * 1.1)

    grass_needed = cell.rabbits * 2
    if grass >= grass_needed:
        grass -= grass_needed
        food_ok = True
    else:
        grass = 0
        food_ok = False

    rabbits = cell.rabbits * (1.2 if food_ok else 0.7)

    rabbits_eaten = min(rabbits, cell.foxes * 0.3)
    rabbits -= rabbits_eaten

    foxes = cell.foxes * (1.1 if rabbits_eaten > cell.foxes * 0.15 else 0.9)

    return Cell(
        grass=_clamp_int(grass),
        rabbits=_clamp_int(rabbits),
        foxes=_clamp_int(foxes),
    )


def tick_grid(state: GridState) -> GridState:
    """Apply one tick (local interactions + diffusion)."""
    new_cells = []
    for y in range(state.grid_height):
        for x in range(state.grid_width):
            new_cells.append(tick_cell(state.get_cell(x, y)))
    next_state = GridState(
        day=state.day + 1,
        grid_width=state.grid_width,
        grid_height=state.grid_height,
        cells=new_cells,
    )
    return apply_diffusion(next_state)


def _clamp_int(value: float) -> int:
    return max(0, int(round(value)))
