"""Entity movement helpers."""
from __future__ import annotations

import random

from core.agents import HERBIVORE_TYPES
from core.model import GridState

_HERBIVORE_SET = set(HERBIVORE_TYPES)


def apply_entity_diffusion(state: GridState, move_chance: float = 0.3) -> None:
    """Move individual carnivores/neutral entities to neighboring cells."""
    for entity in list(state.entities.values()):
        if entity.type in _HERBIVORE_SET:
            continue
        neighbors = state.neighbors(entity.x, entity.y)
        if not neighbors:
            continue
        if random.random() >= move_chance:
            continue
        new_x, new_y = random.choice(neighbors)
        state.move_entity(entity.id, new_x, new_y)
