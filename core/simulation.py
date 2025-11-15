"""Core simulation logic."""
from __future__ import annotations

from typing import Dict


def tick(state: Dict[str, float]) -> Dict[str, float]:
    """Pure function: state → new_state."""
    grass = min(state["grass"] * 1.1, 1000)

    demand = state["rabbits"] * 5 or 1
    food_ratio = min(grass / demand, 1.0)
    rabbit_growth = 0.8 + 0.5 * food_ratio
    rabbits = state["rabbits"] * rabbit_growth
    rabbits -= state["rabbits"] * (1 - food_ratio) * 0.4

    foxes = state["foxes"] * 1.15 if rabbits > state["foxes"] * 2 else state["foxes"] * 0.9

    grass -= state["rabbits"] * (0.3 + 0.2 * food_ratio)

    rabbits -= state["foxes"] * 0.3

    return {
        "day": state["day"] + 1,
        "grass": max(0, grass),
        "rabbits": max(0, rabbits),
        "foxes": max(0, foxes),
    }
