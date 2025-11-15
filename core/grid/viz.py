"""Grid visualization helpers."""
from __future__ import annotations

from .cell import Cell
from .state import GridState


def cell_to_emoji(cell: Cell) -> str:
    if cell.foxes > 0:
        return "🦊"
    if cell.rabbits > 0:
        return "🐇"
    if cell.grass > 70:
        return "🌲"
    if cell.grass > 20:
        return "🌱"
    return "▫️"


def render_grid(state: GridState) -> str:
    lines = []
    for y in range(state.grid_height):
        row = ""
        for x in range(state.grid_width):
            row += cell_to_emoji(state.get_cell(x, y))
        lines.append(row)
    return "\n".join(lines)
