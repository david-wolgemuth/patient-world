"""Grid cell representation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from core.agents import Entity


@dataclass
class Cell:
    """Single grid cell with grass and entity references."""

    grass: int
    entity_ids: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Cell":
        ids = [int(eid) for eid in data.get("entity_ids", [])]
        return cls(grass=int(data.get("grass", 0)), entity_ids=ids)

    def to_dict(self) -> dict:
        return {"grass": int(self.grass), "entity_ids": [int(eid) for eid in self.entity_ids]}

    def copy(self) -> "Cell":
        return Cell(grass=self.grass, entity_ids=list(self.entity_ids))

    def add_entity(self, entity_id: int) -> None:
        if entity_id not in self.entity_ids:
            self.entity_ids.append(entity_id)

    def remove_entity(self, entity_id: int) -> None:
        try:
            self.entity_ids.remove(entity_id)
        except ValueError:
            pass

    def count_type(self, entities: Dict[int, Entity], entity_type: str) -> int:
        total = 0
        for eid in self.entity_ids:
            entity = entities.get(eid)
            if entity and entity.type == entity_type:
                total += 1
        return total

    def rabbits(self, entities: Dict[int, Entity]) -> int:
        return self.count_type(entities, "rabbit")

    def foxes(self, entities: Dict[int, Entity]) -> int:
        return self.count_type(entities, "fox")

    def iter_entities(self, entities: Dict[int, Entity]) -> Iterable[Entity]:
        for eid in self.entity_ids:
            entity = entities.get(eid)
            if entity is not None:
                yield entity
