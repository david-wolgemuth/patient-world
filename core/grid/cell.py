"""Grid cell representation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Cell:
    """Single grid cell with local populations."""

    grass: int
    rabbits: int
    foxes: int

    @classmethod
    def from_dict(cls, data: dict) -> "Cell":
        return cls(
            grass=int(data.get("grass", 0)),
            rabbits=int(data.get("rabbits", 0)),
            foxes=int(data.get("foxes", 0)),
        )

    def to_dict(self) -> dict:
        return {"grass": int(self.grass), "rabbits": int(self.rabbits), "foxes": int(self.foxes)}

    def copy(self) -> "Cell":
        return Cell(grass=self.grass, rabbits=self.rabbits, foxes=self.foxes)

    def dominant_entity(self) -> str:
        if self.foxes > 0:
            return "fox"
        if self.rabbits > 0:
            return "rabbit"
        if self.grass > 70:
            return "grass_high"
        if self.grass > 20:
            return "grass_low"
        return "empty"
