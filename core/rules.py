"""Simulation rules governing entities and environment changes."""
from __future__ import annotations

import math
import random
from typing import Iterable, Sequence

from core.agents import Entity
from core.environment import apply_entity_diffusion
from core.environment.producers import (
    GROUND_LAYER,
    LAYER_CAPS,
    PRODUCER_PROFILES,
    water_response,
    within_season_window,
)
from core.model import GridState

GROUND_CAP = LAYER_CAPS[GROUND_LAYER]
SEASON_LENGTH = 120
FACTOR_BLOCK_THRESHOLD = 0.15
MULTIPLIER_BLOCK_THRESHOLD = 0.1
MULTIPLIER_MIN = 0.35
MULTIPLIER_MAX = 1.6
NOISE_SCALE = 0.10
RABBIT_DIET: Sequence[str] = (
    "seasonal_annuals",
    "fast_grass",
    "forb_wildflowers",
    "reed_beds",
    "bog_sedges",
    "moss_carpet",
    "succulent_cluster",
    "desert_bloomers",
    "slow_shrubs",
)


def apply_all(state: GridState, *, log_capacity: bool = True) -> None:
    """Run all rule steps in canonical order."""
    state.capacity_events.clear()
    grow_producers(state)
    tick_rabbits(state)
    tick_foxes(state)
    apply_entity_diffusion(state)
    remove_dead_entities(state)
    if log_capacity and state.capacity_events:
        _log_capacity_summary(state)


def grow_producers(state: GridState) -> None:
    """Advance every cell's producer guilds."""
    season_factor = _season_factor(state.day)
    for y in range(state.grid_height):
        for x in range(state.grid_width):
            cell = state.get_cell(x, y)
            multiplier, limiting_key, limiting_value = _resource_multiplier(state, cell, x, y, season_factor)
            cell.set_limiting_resource(limiting_key, limiting_value)
            _grow_cell_producers(state, cell, x, y, state.day, multiplier)


def _grow_cell_producers(state: GridState, cell, x: int, y: int, day: int, resource_multiplier: float) -> None:
    producers = cell.producers
    for name, profile in PRODUCER_PROFILES.items():
        amount = producers.get(name, 0)
        if amount <= 0 and profile.seeding_dependency:
            if cell.producer_amount(profile.seeding_dependency) >= profile.seeding_threshold:
                amount = profile.seeding_amount
        if profile.seasonal_window and not within_season_window(day, profile.seasonal_window):
            if amount > 0:
                retain = max(0.0, 1.0 - profile.dormancy_decay)
                amount = int(round(amount * retain))
            producers[name] = amount
            continue
        crowding = _layer_crowding(cell, profile.layer)
        crowd_penalty = _crowding_penalty(crowding)
        growth_source = max(amount, profile.seed_floor)
        layer_bias = 1.0 if profile.layer == GROUND_LAYER else 1.12
        base_rate = profile.growth_rate * layer_bias
        water_factor = max(0.0, water_response(profile, cell.water_average()))
        if water_factor <= FACTOR_BLOCK_THRESHOLD:
            # Drought or waterlogging stress trims existing biomass slightly.
            stress_decay = 0.82 if cell.get_water() < profile.water_optimum else 0.88
            amount = int(round(amount * stress_decay))
            producers[name] = amount
            continue
        growth_rate = base_rate * max(0.2, resource_multiplier) * max(0.1, water_factor) * crowd_penalty
        delta = int(round(growth_source * growth_rate))
        if delta <= 0 and amount == 0:
            delta = max(1, int(profile.seed_floor * 0.25))
        amount = min(profile.max_density, amount + max(delta, 0))
        producers[name] = amount
    limited = cell.clamp_layers()
    for layer, total, cap in limited:
        state.record_capacity_event(x=x, y=y, layer=layer, total=total, capacity=cap)


def _layer_crowding(cell, layer: str) -> float:
    total = cell.ground_cover() if layer == GROUND_LAYER else cell.canopy_cover()
    cap = max(1, cell.layer_capacity(layer))
    return min(1.5, total / cap)


def _crowding_penalty(ratio: float) -> float:
    logistic = 1.0 / (1.0 + math.exp(6.0 * (ratio - 0.85)))
    return max(0.08, logistic)


def tick_rabbits(state: GridState) -> None:
    for entity in list(_entities_of_type(state, "rabbit")):
        entity.hunger += 1
        entity.age += 1
        cell = state.get_cell(entity.x, entity.y)
        eaten = _graze(cell, 6, RABBIT_DIET)
        if eaten >= 4:
            entity.hunger = max(0, entity.hunger - 3)
        elif eaten > 0:
            entity.hunger = max(0, entity.hunger - 1)
        if entity.hunger <= 2 and entity.age > 5:
            crowd_bonus = min(0.25, cell.ground_cover() / max(1, GROUND_CAP) * 0.1)
            if random.random() < (0.2 + crowd_bonus):
                state.spawn_entity("rabbit", entity.x, entity.y)


def tick_foxes(state: GridState) -> None:
    for entity in list(_entities_of_type(state, "fox")):
        entity.hunger += 1
        entity.age += 1
        rabbits = state.entities_by_type(entity.x, entity.y, "rabbit")
        if rabbits:
            prey = max(rabbits, key=lambda r: r.hunger)
            state.remove_entity(prey.id)
            entity.hunger = max(0, entity.hunger - 5)
        if entity.hunger <= 3 and entity.age > 10:
            if random.random() < 0.15:
                state.spawn_entity("fox", entity.x, entity.y)


def remove_dead_entities(state: GridState) -> None:
    for entity_id in [eid for eid, entity in state.entities.items() if entity.is_dead()]:
        state.remove_entity(entity_id)


def _log_capacity_summary(state: GridState) -> None:
    events = state.capacity_events
    if not events:
        return
    hotspot: dict[tuple[int, int], int] = {}
    for event in events:
        key = (event["x"], event["y"])
        hotspot[key] = hotspot.get(key, 0) + 1
    top = sorted(hotspot.items(), key=lambda item: item[1], reverse=True)[:3]
    preview = ", ".join(f"({x},{y})" for (x, y), _ in top)
    print(
        f"[capacity] Day {state.day} limited {len(events)} layers; hotspots: {preview}",
        flush=True,
    )


def _resource_multiplier(state: GridState, cell, x: int, y: int, season_factor: float) -> tuple[float, str | None, float]:
    factors = {
        "fertility": _clamp01(cell.fertility),
        "temperature": _temperature_factor(cell, state.day),
        "season": season_factor,
        "facilitation": _facilitation_factor(state, cell, x, y),
    }
    water_factor = _clamp01(cell.water_average())
    limiting_key, limiting_value = _detect_limiting_factor({**factors, "water": water_factor})
    if any(value <= FACTOR_BLOCK_THRESHOLD for value in factors.values()):
        return 0.0, limiting_key, limiting_value
    multiplier = 1.0
    for value in factors.values():
        multiplier *= _clamp_multiplier(0.5 + value * 0.9)
        if multiplier <= MULTIPLIER_BLOCK_THRESHOLD:
            return 0.0, limiting_key, limiting_value
    return multiplier * _growth_noise(), limiting_key, limiting_value


def _detect_limiting_factor(values: dict[str, float]) -> tuple[str | None, float]:
    if not values:
        return None, 1.0
    limiting_key = None
    limiting_value = 1.0
    for key, value in values.items():
        if limiting_key is None or value < limiting_value or (value == limiting_value and key < limiting_key):
            limiting_key = key
            limiting_value = value
    return limiting_key, limiting_value


def _growth_noise() -> float:
    if NOISE_SCALE <= 0:
        return 1.0
    return 1.0 + random.uniform(-NOISE_SCALE, NOISE_SCALE)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _clamp_multiplier(value: float) -> float:
    return max(MULTIPLIER_MIN, min(MULTIPLIER_MAX, value))


def _season_factor(day: int) -> float:
    cycle = (day % SEASON_LENGTH) / SEASON_LENGTH
    return _clamp01(0.25 + 0.75 * (0.5 + 0.5 * math.sin(2 * math.pi * cycle - math.pi / 2)))


def _season_temperature(day: int) -> float:
    cycle = (day % SEASON_LENGTH) / SEASON_LENGTH
    return _clamp01(0.4 + 0.6 * (0.5 + 0.5 * math.sin(2 * math.pi * cycle)))


def _temperature_factor(cell, day: int) -> float:
    ambient = _season_temperature(day)
    delta = abs(ambient - _clamp01(cell.temperature))
    return _clamp01(1.0 - delta * 1.5)


def _facilitation_factor(state: GridState, cell, x: int, y: int) -> float:
    neighbors = state.neighbors(x, y)
    if not neighbors:
        return 0.5
    neighbor_total = 0.0
    for nx, ny in neighbors:
        neighbor_total += state.get_cell(nx, ny).ground_cover()
    neighbor_capacity = len(neighbors) * GROUND_CAP
    neighbor_density = neighbor_total / neighbor_capacity if neighbor_capacity else 0.0
    local_density = cell.ground_cover() / GROUND_CAP if GROUND_CAP else 0.0
    return _clamp01(0.2 + 0.5 * neighbor_density + 0.3 * local_density)


def _graze(cell, amount: int, diet: Sequence[str]) -> int:
    consumed = 0
    remaining = amount
    for producer in diet:
        available = cell.producer_amount(producer)
        if available <= 0:
            continue
        take = min(available, remaining)
        cell.adjust_producer(producer, -take)
        consumed += take
        remaining -= take
        if remaining <= 0:
            break
    return consumed


def _entities_of_type(state: GridState, entity_type: str) -> Iterable[Entity]:
    for entity in state.entities.values():
        if entity.type == entity_type:
            yield entity
