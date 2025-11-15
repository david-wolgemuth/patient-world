"""Grid state container."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple

from .cell import Cell
from .entity import Entity


@dataclass
class GridState:
    """Canonical grid-based world state."""

    day: int
    grid_width: int
    grid_height: int
    cells: List[Cell] = field(default_factory=list)
    entities: Dict[int, Entity] = field(default_factory=dict)
    next_entity_id: int = 1
    migration_version: int = 2

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
        entities_raw = data.get("entities", {})
        entities: Dict[int, Entity] = {}
        if isinstance(entities_raw, dict):
            source_iter = entities_raw.items()
        else:
            source_iter = ((entry.get("id"), entry) for entry in entities_raw)
        for eid, edata in source_iter:
            if eid is None:
                continue
            entities[int(eid)] = Entity.from_dict(edata)
        next_entity_id = int(data.get("next_entity_id", (max(entities.keys()) + 1) if entities else 1))
        version = int(data.get("_migration_version", 0))
        return cls(
            day=int(data.get("day", 0)),
            grid_width=width,
            grid_height=height,
            cells=cells,
            entities=entities,
            next_entity_id=next_entity_id,
            migration_version=version,
        )

    def to_dict(self) -> dict:
        return {
            "day": int(self.day),
            "grid_width": int(self.grid_width),
            "grid_height": int(self.grid_height),
            "cells": [cell.to_dict() for cell in self.cells],
            "entities": {eid: entity.to_dict() for eid, entity in self.entities.items()},
            "next_entity_id": int(self.next_entity_id),
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
        return sum(1 for entity in self.entities.values() if entity.type == "rabbit")

    def total_foxes(self) -> int:
        return sum(1 for entity in self.entities.values() if entity.type == "fox")

    def clone(self) -> "GridState":
        return GridState(
            day=int(self.day),
            grid_width=int(self.grid_width),
            grid_height=int(self.grid_height),
            cells=[cell.copy() for cell in self.cells],
            entities={eid: Entity.from_dict(entity.to_dict()) for eid, entity in self.entities.items()},
            next_entity_id=int(self.next_entity_id),
            migration_version=int(self.migration_version),
        )

    def iter_coords(self) -> Iterable[Tuple[int, int]]:
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                yield x, y

    def spawn_entity(self, entity_type: str, x: int, y: int, *, hunger: int = 0, age: int = 0) -> Entity:
        entity = Entity(id=self.next_entity_id, type=entity_type, x=x, y=y, hunger=hunger, age=age)
        self.entities[entity.id] = entity
        self.get_cell(x, y).add_entity(entity.id)
        self.next_entity_id += 1
        return entity

    def remove_entity(self, entity_id: int) -> None:
        entity = self.entities.get(entity_id)
        if not entity:
            return
        self.get_cell(entity.x, entity.y).remove_entity(entity_id)
        del self.entities[entity_id]

    def move_entity(self, entity_id: int, new_x: int, new_y: int) -> None:
        entity = self.entities.get(entity_id)
        if not entity:
            return
        self.get_cell(entity.x, entity.y).remove_entity(entity_id)
        entity.x = new_x
        entity.y = new_y
        self.get_cell(new_x, new_y).add_entity(entity_id)

    def entities_in_cell(self, x: int, y: int) -> List[Entity]:
        cell = self.get_cell(x, y)
        return list(cell.iter_entities(self.entities))

    def entities_by_type(self, x: int, y: int, entity_type: str) -> List[Entity]:
        return [entity for entity in self.entities_in_cell(x, y) if entity.type == entity_type]
