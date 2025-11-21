"""Herbivore archetype metadata."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence


@dataclass(frozen=True)
class HerbivoreProfile:
    """Configures herbivore feeding, reproduction, and movement traits."""

    type: str
    emoji: str
    diet: Sequence[str]
    intake: int
    hunger_rate: int
    satiation_threshold: int
    hunger_relief: int
    health_gain: int
    starvation_penalty: int
    reproduction_age: int
    reproduction_hunger: int
    reproduction_cooldown: int
    reproduction_chance: float
    herd_bonus: float
    herd_scan: int
    min_population: int
    spawn_batch: int


HERBIVORE_PROFILES: Dict[str, HerbivoreProfile] = {
    "rabbit": HerbivoreProfile(
        type="rabbit",
        emoji="🐇",
        diet=("seasonal_annuals", "fast_grass", "slow_shrubs"),
        intake=6,
        hunger_rate=1,
        satiation_threshold=4,
        hunger_relief=3,
        health_gain=4,
        starvation_penalty=4,
        reproduction_age=5,
        reproduction_hunger=2,
        reproduction_cooldown=5,
        reproduction_chance=0.22,
        herd_bonus=4.0,
        herd_scan=1,
        min_population=18,
        spawn_batch=6,
    ),
    "grazer": HerbivoreProfile(
        type="grazer",
        emoji="🐏",
        diet=("fast_grass", "seasonal_annuals", "slow_shrubs"),
        intake=9,
        hunger_rate=2,
        satiation_threshold=6,
        hunger_relief=4,
        health_gain=5,
        starvation_penalty=6,
        reproduction_age=12,
        reproduction_hunger=3,
        reproduction_cooldown=8,
        reproduction_chance=0.18,
        herd_bonus=6.0,
        herd_scan=1,
        min_population=10,
        spawn_batch=4,
    ),
    "browser": HerbivoreProfile(
        type="browser",
        emoji="🦌",
        diet=("slow_shrubs", "deep_roots", "fast_grass", "seasonal_annuals"),
        intake=7,
        hunger_rate=2,
        satiation_threshold=5,
        hunger_relief=4,
        health_gain=6,
        starvation_penalty=7,
        reproduction_age=10,
        reproduction_hunger=3,
        reproduction_cooldown=7,
        reproduction_chance=0.16,
        herd_bonus=5.0,
        herd_scan=1,
        min_population=8,
        spawn_batch=3,
    ),
}


HERBIVORE_TYPES = tuple(HERBIVORE_PROFILES.keys())
