"""Grid visualization helpers."""
from __future__ import annotations

from typing import Dict

from .cell import Cell
from core.agents import Entity
from .state import GridState


def cell_to_emoji(cell: Cell, entities: Dict[int, Entity]) -> str:
    rabbits = cell.rabbits(entities)
    foxes = cell.foxes(entities)
    if foxes > 0:
        return "🦊"
    if rabbits > 0:
        return "🐇"
    if cell.grass > 70:
        return "🌲"
    if cell.grass > 20:
        return "🌱"
    return "▫️"


def render_grid(state: GridState) -> str:
    lines = []
    entities = state.entities
    for y in range(state.grid_height):
        row = ""
        for x in range(state.grid_width):
            row += cell_to_emoji(state.get_cell(x, y), entities)
        lines.append(row)
    return "\n".join(lines)
