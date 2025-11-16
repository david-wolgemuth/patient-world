"""Entity model for grid actors."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Entity:
    """Individual actor that occupies a grid cell."""

    id: int
    type: str
    x: int
    y: int
    hunger: int = 0
    age: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Entity":
        return cls(
            id=int(data["id"]),
            type=str(data["type"]),
            x=int(data["x"]),
            y=int(data["y"]),
            hunger=int(data.get("hunger", 0)),
            age=int(data.get("age", 0)),
        )

    def to_dict(self) -> dict:
        return {
            "id": int(self.id),
            "type": self.type,
            "x": int(self.x),
            "y": int(self.y),
            "hunger": int(self.hunger),
            "age": int(self.age),
        }

    def is_starving(self) -> bool:
        return self.hunger >= 8

    def is_dead(self) -> bool:
        return self.hunger >= 10
