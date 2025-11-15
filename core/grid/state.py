"""Grid state container."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence, Tuple

from .cell import Cell


@dataclass
class GridState:
    """Canonical grid-based world state."""

    day: int
    grid_width: int
    grid_height: int
    cells: List[Cell] = field(default_factory=list)
    migration_version: int = 1

    def __post_init__(self) -> None:
        expected = self.grid_width * self.grid_height
        if len(self.cells) != expected:
            raise ValueError(f"Expected {expected} cells (got {len(self.cells)})")

    @classmethod
    def from_dict(cls, data: dict) -> "GridState":
        if "grid_width" not in data or "grid_height" not in data or "cells" not in data:
            raise ValueError("Legacy state format detected. Run: python migrations/0001_grid_state.py <world>")
        width = int(data["grid_width"])
        height = int(data["grid_height"])
        cells_raw: Sequence[dict] = data["cells"]
        cells = [Cell.from_dict(cell) for cell in cells_raw]
        version = int(data.get("_migration_version", 0))
        return cls(day=int(data.get("day", 0)), grid_width=width, grid_height=height, cells=cells, migration_version=version)

    def to_dict(self) -> dict:
        return {
            "day": int(self.day),
            "grid_width": int(self.grid_width),
            "grid_height": int(self.grid_height),
            "cells": [cell.to_dict() for cell in self.cells],
            "_migration_version": int(self.migration_version),
        }

    def _index(self, x: int, y: int) -> int:
        if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
            raise IndexError(f"Cell ({x}, {y}) out of bounds")
        return y * self.grid_width + x

    def get_cell(self, x: int, y: int) -> Cell:
        return self.cells[self._index(x, y)]

    def set_cell(self, x: int, y: int, cell: Cell) -> None:
        self.cells[self._index(x, y)] = cell

    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        coords: List[Tuple[int, int]] = []
        if y > 0:
            coords.append((x, y - 1))
        if y < self.grid_height - 1:
            coords.append((x, y + 1))
        if x > 0:
            coords.append((x - 1, y))
        if x < self.grid_width - 1:
            coords.append((x + 1, y))
        return coords

    def _total(self, attr: str) -> int:
        return int(sum(getattr(cell, attr) for cell in self.cells))

    def total_grass(self) -> int:
        return self._total("grass")

    def total_rabbits(self) -> int:
        return self._total("rabbits")

    def total_foxes(self) -> int:
        return self._total("foxes")

    def clone(self) -> "GridState":
        return GridState(
            day=int(self.day),
            grid_width=int(self.grid_width),
            grid_height=int(self.grid_height),
            cells=[cell.copy() for cell in self.cells],
            migration_version=int(self.migration_version),
        )

    def iter_coords(self) -> Iterable[Tuple[int, int]]:
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                yield x, y
