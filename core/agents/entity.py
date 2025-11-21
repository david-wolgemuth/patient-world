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
    health: int = 100
    reproduction_cooldown: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Entity":
        return cls(
            id=int(data["id"]),
            type=str(data["type"]),
            x=int(data["x"]),
            y=int(data["y"]),
            hunger=int(data.get("hunger", 0)),
            age=int(data.get("age", 0)),
            health=int(data.get("health", 100)),
            reproduction_cooldown=int(data.get("reproduction_cooldown", 0)),
        )

    def to_dict(self) -> dict:
        return {
            "id": int(self.id),
            "type": self.type,
            "x": int(self.x),
            "y": int(self.y),
            "hunger": int(self.hunger),
            "age": int(self.age),
            "health": int(self.health),
            "reproduction_cooldown": int(self.reproduction_cooldown),
        }

    def is_starving(self) -> bool:
        return self.hunger >= 8

    def is_dead(self) -> bool:
        return self.hunger >= 10 or self.health <= 0
