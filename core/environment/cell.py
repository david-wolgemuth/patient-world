"""Grid cell representation."""
from __future__ import annotations

import os
import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence

from core.agents import Entity
from core.environment.producers import (
    CANOPY_LAYER,
    GROUND_LAYER,
    LAYER_CAPS,
    LAYER_MEMBERS,
    dominant_producer,
    empty_producer_map,
    normalize_producers,
    producer_emoji,
    total_producers,
)

_WATER_RANGE = (0.25, 0.95)
_FERTILITY_RANGE = (0.25, 0.9)
_TEMPERATURE_RANGE = (0.2, 0.85)


def _history_window() -> int:
    raw = os.environ.get("PW_WATER_HISTORY_WINDOW", "14")
    try:
        size = int(raw)
    except ValueError:
        size = 14
    return max(1, size)


WATER_HISTORY_WINDOW = _history_window()


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def random_environment_profile(seed: int | None = None) -> tuple[float, float, float]:
    rng = random.Random(seed)
    water = rng.uniform(*_WATER_RANGE)
    fertility = rng.uniform(*_FERTILITY_RANGE)
    temperature = rng.uniform(*_TEMPERATURE_RANGE)
    return water, fertility, temperature


def generate_water_distribution(
    width: int,
    height: int,
    *,
    seed: int | str | None = None,
    smooth_passes: int = 2,
) -> List[float]:
    """Generate a flattened, smoothed noise map for water initialization."""

    if width <= 0 or height <= 0:
        return []
    rng = random.Random(seed)
    grid: List[List[float]] = [[rng.random() for _ in range(width)] for _ in range(height)]
    for _ in range(max(0, smooth_passes)):
        smoothed: List[List[float]] = []
        for y in range(height):
            row: List[float] = []
            for x in range(width):
                total = 0.0
                count = 0
                for ny in range(max(0, y - 1), min(height, y + 2)):
                    for nx in range(max(0, x - 1), min(width, x + 2)):
                        total += grid[ny][nx]
                        count += 1
                row.append(total / count if count else grid[y][x])
            smoothed.append(row)
        grid = smoothed
    scale = _WATER_RANGE[1] - _WATER_RANGE[0]
    flattened: List[float] = []
    for row in grid:
        for value in row:
            scaled = _clamp(_WATER_RANGE[0] + value * scale, 0.0, 1.0)
            flattened.append(scaled)
    return flattened


@dataclass
class Cell:
    """Single grid cell with vegetation strata, environment metrics, and entity references."""

    producers: Dict[str, int] = field(default_factory=empty_producer_map)
    entity_ids: List[int] = field(default_factory=list)
    water: float = field(default=0.6)
    fertility: float = field(default=0.6)
    temperature: float = field(default=0.5)
    water_history: List[float] = field(default_factory=list)
    limiting_factor: str | None = None
    limiting_value: float = 1.0

    def __post_init__(self) -> None:
        self.water = _clamp(float(self.water), 0.0, 1.0)
        self.fertility = _clamp(float(self.fertility), 0.0, 1.0)
        self.temperature = _clamp(float(self.temperature), 0.0, 1.0)
        cleaned: List[float] = []
        for value in self.water_history:
            try:
                cleaned.append(_clamp(float(value), 0.0, 1.0))
            except (TypeError, ValueError):
                continue
        if not cleaned:
            cleaned = [self.water]
        elif cleaned[-1] != self.water:
            cleaned.append(self.water)
        self.water_history = cleaned[-WATER_HISTORY_WINDOW:]
        try:
            self.limiting_value = _clamp(float(self.limiting_value), 0.0, 1.0)
        except (TypeError, ValueError):
            self.limiting_value = 1.0
        if self.limiting_factor is not None:
            self.limiting_factor = str(self.limiting_factor)

    @classmethod
    def with_uniform_producers(cls, *, fast_grass: int = 0, shrubs: int = 0) -> "Cell":
        mapping = empty_producer_map()
        mapping["fast_grass"] = max(0, fast_grass)
        mapping["slow_shrubs"] = max(0, shrubs)
        cell = cls(producers=mapping)
        cell.clamp_layers()
        return cell

    @classmethod
    def from_dict(cls, data: dict, *, seed: int | None = None) -> "Cell":
        ids = [int(eid) for eid in data.get("entity_ids", [])]
        defaults = random_environment_profile(seed)
        water = float(data.get("water", defaults[0]))
        fertility = float(data.get("fertility", defaults[1]))
        temperature = float(data.get("temperature", defaults[2]))
        history_values: Sequence[float] | None = data.get("water_history")
        history: List[float] = []
        if history_values:
            for value in history_values:
                try:
                    history.append(_clamp(float(value), 0.0, 1.0))
                except (TypeError, ValueError):
                    continue

        producers_raw = data.get("producers")
        if producers_raw is None:
            producers = empty_producer_map()
            producers["fast_grass"] = int(data.get("grass", 0))
        else:
            producers = normalize_producers({key: int(value) for key, value in producers_raw.items()})

        limiting_factor = data.get("limiting_factor")
        limiting_value = data.get("limiting_value", 1.0)
        try:
            limiting_value_f = _clamp(float(limiting_value), 0.0, 1.0)
        except (TypeError, ValueError):
            limiting_value_f = 1.0

        cell = cls(
            producers=producers,
            entity_ids=ids,
            water=water,
            fertility=fertility,
            temperature=temperature,
            water_history=history,
            limiting_factor=limiting_factor,
            limiting_value=limiting_value_f,
        )
        cell.clamp_layers()
        return cell

    def to_dict(self) -> dict:
        return {
            "producers": {name: int(amount) for name, amount in self.producers.items()},
            "entity_ids": [int(eid) for eid in self.entity_ids],
            "water": float(self.water),
            "fertility": float(self.fertility),
            "temperature": float(self.temperature),
            "water_history": [float(value) for value in self.water_history],
            "limiting_factor": self.limiting_factor,
            "limiting_value": float(_clamp(self.limiting_value, 0.0, 1.0)),
        }

    def copy(self) -> "Cell":
        return Cell(
            producers=dict(self.producers),
            entity_ids=list(self.entity_ids),
            water=self.water,
            fertility=self.fertility,
            temperature=self.temperature,
            water_history=list(self.water_history),
            limiting_factor=self.limiting_factor,
            limiting_value=self.limiting_value,
        )

    @property
    def grass(self) -> int:
        """Compatibility accessor for fast grass biomass."""

        return int(self.producers.get("fast_grass", 0))

    @grass.setter
    def grass(self, value: int) -> None:
        self.producers["fast_grass"] = max(0, int(value))
        self.clamp_layers()

    def add_entity(self, entity_id: int) -> None:
        if entity_id not in self.entity_ids:
            self.entity_ids.append(entity_id)

    def remove_entity(self, entity_id: int) -> None:
        try:
            self.entity_ids.remove(entity_id)
        except ValueError:
            pass

    def clamp_layers(self) -> List[tuple[str, int, int]]:
        limited: List[tuple[str, int, int]] = []
        for layer, members in LAYER_MEMBERS.items():
            cap = self.layer_capacity(layer)
            total = sum(self.producers[name] for name in members)
            if total <= cap:
                continue
            if cap <= 0 or total <= 0:
                for name in members:
                    self.producers[name] = 0
            else:
                scale = cap / total
                for name in members:
                    self.producers[name] = int(round(self.producers[name] * scale))
            limited.append((layer, int(total), int(cap)))
        return limited

    def adjust_producer(self, name: str, delta: int) -> int:
        """Increment a producer bucket and return the new value."""
        if name not in self.producers:
            return 0
        self.producers[name] = max(0, self.producers[name] + int(delta))
        self.clamp_layers()
        return self.producers[name]

    def set_producer(self, name: str, value: int) -> None:
        if name not in self.producers:
            return
        self.producers[name] = max(0, int(value))
        self.clamp_layers()

    def producer_amount(self, name: str) -> int:
        return int(self.producers.get(name, 0))

    def total_producer_biomass(self) -> int:
        return total_producers(self.producers)

    def ground_cover(self) -> int:
        return sum(self.producers[name] for name in LAYER_MEMBERS[GROUND_LAYER])

    def canopy_cover(self) -> int:
        return sum(self.producers[name] for name in LAYER_MEMBERS[CANOPY_LAYER])

    def layer_capacity(self, layer: str) -> int:
        base = max(1, int(LAYER_CAPS.get(layer, 100)))
        moisture = 0.45 + 0.55 * self.water_average()
        fertility = 0.4 + 0.6 * self.fertility
        preferred_temp = 0.55 if layer == GROUND_LAYER else 0.68
        delta = abs(self.temperature - preferred_temp)
        temp_alignment = max(0.0, 1.0 - min(1.0, delta * 1.35))
        temp_factor = 0.5 + 0.5 * temp_alignment
        limiting = self.limiting_value if self.limiting_factor else 1.0
        limiting_factor = 0.6 + 0.4 * limiting
        resilience = 0.85 + 0.3 * self.water
        layer_bias = 1.0 if layer == GROUND_LAYER else 0.9 + 0.2 * self.fertility
        factor = _clamp(moisture * fertility * temp_factor * resilience * limiting_factor * layer_bias, 0.3, 1.4)
        return max(8, int(round(base * factor)))

    def dominant_producer(self) -> str | None:
        return dominant_producer(self.producers)

    def producer_emoji(self) -> str | None:
        key = self.dominant_producer()
        return producer_emoji(key) if key else None

    def get_water(self) -> float:
        return float(self.water)

    def set_water(self, value: float, *, track_history: bool = True) -> float:
        self.water = _clamp(float(value), 0.0, 1.0)
        if track_history:
            self._push_water_sample(self.water)
        return self.water

    def set_limiting_resource(self, name: str | None, value: float | None) -> None:
        """Store the most limiting resource factor and its normalized value."""
        self.limiting_factor = name if name is None else str(name)
        if value is None:
            self.limiting_value = 1.0
        else:
            try:
                self.limiting_value = _clamp(float(value), 0.0, 1.0)
            except (TypeError, ValueError):
                self.limiting_value = 1.0

    def water_average(self) -> float:
        history = self.water_history or [self.water]
        return float(sum(history) / len(history))

    def _push_water_sample(self, value: float) -> None:
        self.water_history.append(value)
        overflow = len(self.water_history) - WATER_HISTORY_WINDOW
        if overflow > 0:
            del self.water_history[:overflow]

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
