"""Grid tick logic for entity actors."""
from __future__ import annotations

import random
from typing import Iterable

from core.environment import apply_entity_diffusion
from core.agents import Entity
from core.model import GridState


def tick_grid(state: GridState) -> GridState:
    """Apply one tick over the grid using entity behaviors."""
    next_state = state.clone()
    _grow_grass(next_state)
    _tick_rabbits(next_state)
    _tick_foxes(next_state)
    apply_entity_diffusion(next_state)
    _remove_dead_entities(next_state)
    next_state.day += 1
    return next_state


def _grow_grass(state: GridState) -> None:
    for cell in state.cells:
        cell.grass = min(100, int(cell.grass * 1.1))


def _tick_rabbits(state: GridState) -> None:
    for entity in list(_entities_of_type(state, "rabbit")):
        entity.hunger += 1
        entity.age += 1
        cell = state.get_cell(entity.x, entity.y)
        if cell.grass >= 2:
            cell.grass -= 2
            entity.hunger = max(0, entity.hunger - 3)
        if entity.hunger <= 2 and entity.age > 5:
            if random.random() < 0.2:
                state.spawn_entity("rabbit", entity.x, entity.y)


def _tick_foxes(state: GridState) -> None:
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


def _remove_dead_entities(state: GridState) -> None:
    for entity_id in [eid for eid, entity in state.entities.items() if entity.is_dead()]:
        state.remove_entity(entity_id)


def _entities_of_type(state: GridState, entity_type: str) -> Iterable[Entity]:
    for entity in state.entities.values():
        if entity.type == entity_type:
            yield entity
