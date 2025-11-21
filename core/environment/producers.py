"""Metadata and helpers for vegetation producer guilds."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

GROUND_LAYER = "ground"
CANOPY_LAYER = "canopy"
SEASON_LENGTH = 120


@dataclass(frozen=True)
class ProducerProfile:
    """Defines growth traits and presentation of a producer guild."""

    key: str
    emoji: str
    layer: str
    max_density: int
    growth_rate: float
    seed_floor: int
    seasonal_window: Tuple[float, float] | None = None
    dormancy_decay: float = 0.35
    seeding_dependency: str | None = None
    seeding_threshold: int = 0
    seeding_amount: int = 0
    water_optimum: float = 0.6
    water_tolerance: Tuple[float, float] = (0.2, 0.95)


PRODUCER_PROFILES: Dict[str, ProducerProfile] = {
    "fast_grass": ProducerProfile(
        key="fast_grass",
        emoji="🌱",
        layer=GROUND_LAYER,
        max_density=85,
        growth_rate=0.25,
        seed_floor=8,
        water_optimum=0.68,
        water_tolerance=(0.32, 0.95),
    ),
    "seasonal_annuals": ProducerProfile(
        key="seasonal_annuals",
        emoji="🌼",
        layer=GROUND_LAYER,
        max_density=55,
        growth_rate=0.35,
        seed_floor=5,
        seasonal_window=(0.15, 0.55),
        dormancy_decay=0.55,
        water_optimum=0.72,
        water_tolerance=(0.38, 0.98),
    ),
    "forb_wildflowers": ProducerProfile(
        key="forb_wildflowers",
        emoji="🌺",
        layer=GROUND_LAYER,
        max_density=50,
        growth_rate=0.23,
        seed_floor=5,
        seasonal_window=(0.2, 0.7),
        dormancy_decay=0.52,
        seeding_dependency="fast_grass",
        seeding_threshold=32,
        seeding_amount=5,
        water_optimum=0.66,
        water_tolerance=(0.32, 0.92),
    ),
    "lichen_crust": ProducerProfile(
        key="lichen_crust",
        emoji="🪨",
        layer=GROUND_LAYER,
        max_density=28,
        growth_rate=0.13,
        seed_floor=3,
        water_optimum=0.24,
        water_tolerance=(0.03, 0.55),
    ),
    "slow_shrubs": ProducerProfile(
        key="slow_shrubs",
        emoji="🌿",
        layer=CANOPY_LAYER,
        max_density=65,
        growth_rate=0.12,
        seed_floor=4,
        seeding_dependency="fast_grass",
        seeding_threshold=40,
        seeding_amount=6,
        water_optimum=0.46,
        water_tolerance=(0.18, 0.88),
    ),
    "deep_roots": ProducerProfile(
        key="deep_roots",
        emoji="🌳",
        layer=CANOPY_LAYER,
        max_density=70,
        growth_rate=0.08,
        seed_floor=3,
        seeding_dependency="slow_shrubs",
        seeding_threshold=25,
        seeding_amount=4,
        water_optimum=0.34,
        water_tolerance=(0.08, 0.9),
    ),
    "moss_carpet": ProducerProfile(
        key="moss_carpet",
        emoji="🍀",
        layer=GROUND_LAYER,
        max_density=50,
        growth_rate=0.2,
        seed_floor=6,
        water_optimum=0.82,
        water_tolerance=(0.5, 1.0),
    ),
    "reed_beds": ProducerProfile(
        key="reed_beds",
        emoji="🎋",
        layer=GROUND_LAYER,
        max_density=45,
        growth_rate=0.22,
        seed_floor=4,
        water_optimum=0.9,
        water_tolerance=(0.6, 1.0),
    ),
    "bog_sedges": ProducerProfile(
        key="bog_sedges",
        emoji="🪷",
        layer=GROUND_LAYER,
        max_density=60,
        growth_rate=0.24,
        seed_floor=4,
        water_optimum=0.88,
        water_tolerance=(0.55, 1.0),
    ),
    "fungal_mat": ProducerProfile(
        key="fungal_mat",
        emoji="🍄",
        layer=GROUND_LAYER,
        max_density=25,
        growth_rate=0.27,
        seed_floor=5,
        seasonal_window=(0.4, 0.9),
        dormancy_decay=0.7,
        seeding_dependency="moss_carpet",
        seeding_threshold=20,
        seeding_amount=5,
        water_optimum=0.78,
        water_tolerance=(0.45, 0.99),
    ),
    "succulent_cluster": ProducerProfile(
        key="succulent_cluster",
        emoji="🌵",
        layer=GROUND_LAYER,
        max_density=35,
        growth_rate=0.16,
        seed_floor=4,
        water_optimum=0.28,
        water_tolerance=(0.05, 0.55),
    ),
    "desert_bloomers": ProducerProfile(
        key="desert_bloomers",
        emoji="🌻",
        layer=GROUND_LAYER,
        max_density=40,
        growth_rate=0.21,
        seed_floor=3,
        seasonal_window=(0.05, 0.45),
        dormancy_decay=0.6,
        seeding_dependency="succulent_cluster",
        seeding_threshold=18,
        seeding_amount=3,
        water_optimum=0.33,
        water_tolerance=(0.08, 0.62),
    ),
    "fruit_trees": ProducerProfile(
        key="fruit_trees",
        emoji="🍎",
        layer=CANOPY_LAYER,
        max_density=55,
        growth_rate=0.1,
        seed_floor=3,
        seeding_dependency="slow_shrubs",
        seeding_threshold=35,
        seeding_amount=4,
        water_optimum=0.58,
        water_tolerance=(0.3, 0.9),
    ),
    "needle_conifers": ProducerProfile(
        key="needle_conifers",
        emoji="🌲",
        layer=CANOPY_LAYER,
        max_density=60,
        growth_rate=0.09,
        seed_floor=3,
        seeding_dependency="deep_roots",
        seeding_threshold=25,
        seeding_amount=4,
        water_optimum=0.4,
        water_tolerance=(0.15, 0.85),
    ),
    "pioneer_brush": ProducerProfile(
        key="pioneer_brush",
        emoji="🍂",
        layer=CANOPY_LAYER,
        max_density=50,
        growth_rate=0.13,
        seed_floor=3,
        seeding_dependency="fast_grass",
        seeding_threshold=45,
        seeding_amount=4,
        water_optimum=0.54,
        water_tolerance=(0.2, 0.85),
    ),
    "vine_canopy": ProducerProfile(
        key="vine_canopy",
        emoji="🌸",
        layer=CANOPY_LAYER,
        max_density=45,
        growth_rate=0.14,
        seed_floor=4,
        seasonal_window=(0.2, 0.8),
        dormancy_decay=0.5,
        seeding_dependency="slow_shrubs",
        seeding_threshold=20,
        seeding_amount=5,
        water_optimum=0.65,
        water_tolerance=(0.3, 0.95),
    ),
    "palm_crowns": ProducerProfile(
        key="palm_crowns",
        emoji="🌴",
        layer=CANOPY_LAYER,
        max_density=48,
        growth_rate=0.11,
        seed_floor=2,
        seeding_dependency="fruit_trees",
        seeding_threshold=28,
        seeding_amount=3,
        water_optimum=0.76,
        water_tolerance=(0.48, 0.98),
    ),
    "mangrove_canopy": ProducerProfile(
        key="mangrove_canopy",
        emoji="🍃",
        layer=CANOPY_LAYER,
        max_density=52,
        growth_rate=0.12,
        seed_floor=3,
        seeding_dependency="bog_sedges",
        seeding_threshold=35,
        seeding_amount=4,
        water_optimum=0.9,
        water_tolerance=(0.6, 1.0),
    ),
}

PRODUCER_TYPES = tuple(PRODUCER_PROFILES.keys())
LAYER_CAPS = {
    GROUND_LAYER: 200,
    CANOPY_LAYER: 150,
}
LAYER_MEMBERS: Dict[str, Tuple[str, ...]] = {
    GROUND_LAYER: tuple(key for key, profile in PRODUCER_PROFILES.items() if profile.layer == GROUND_LAYER),
    CANOPY_LAYER: tuple(key for key, profile in PRODUCER_PROFILES.items() if profile.layer == CANOPY_LAYER),
}


def empty_producer_map() -> Dict[str, int]:
    """Create a zeroed dict for every producer type."""
    return {ptype: 0 for ptype in PRODUCER_TYPES}


def normalize_producers(raw: Dict[str, int] | None) -> Dict[str, int]:
    """Ensure a mapping contains every producer key with integer values."""
    normalized = empty_producer_map()
    if not raw:
        return normalized
    for key, value in raw.items():
        if key in normalized:
            normalized[key] = max(0, int(value))
    return normalized


def layer_total(producers: Dict[str, int], layer: str) -> int:
    return sum(producers[name] for name in LAYER_MEMBERS[layer])


def total_producers(producers: Dict[str, int]) -> int:
    return sum(producers.values())


def clamp_layer(producers: Dict[str, int], layer: str) -> None:
    """Scale down producer amounts if they exceed the layer cap."""
    cap = LAYER_CAPS[layer]
    members = LAYER_MEMBERS[layer]
    total = sum(producers[name] for name in members)
    if total <= cap or total <= 0:
        return
    scale = cap / total
    for name in members:
        producers[name] = int(round(producers[name] * scale))


def clamp_all_layers(producers: Dict[str, int]) -> None:
    for layer in LAYER_CAPS:
        clamp_layer(producers, layer)


def season_phase(day: int) -> float:
    """Relative position in the vegetative season [0, 1)."""
    return (day % SEASON_LENGTH) / SEASON_LENGTH


def within_season_window(day: int, window: Tuple[float, float]) -> bool:
    """Return True if the normalized season falls inside the window."""
    start, end = window
    phase = season_phase(day)
    if start <= end:
        return start <= phase <= end
    # window wraps end of the year
    return phase >= start or phase <= end


def producer_emoji(name: str) -> str:
    return PRODUCER_PROFILES[name].emoji


def dominant_producer(producers: Dict[str, int]) -> str | None:
    """Return the key of the densest producer in the mapping."""
    best_key: str | None = None
    best_value = 0
    for key, value in producers.items():
        if value > best_value:
            best_value = value
            best_key = key
    return best_key if best_value > 0 else None


def water_response(profile: ProducerProfile, water_value: float) -> float:
    """Return a [0, 1] growth multiplier based on species-specific water needs."""

    water_value = max(0.0, min(1.0, water_value))
    min_t, max_t = profile.water_tolerance
    min_t = max(0.0, min(min_t, max_t - 1e-3))
    max_t = min(1.0, max(max_t, min_t + 1e-3))
    optimum = min(max(profile.water_optimum, min_t), max_t)
    if water_value <= min_t or water_value >= max_t:
        return 0.0
    if water_value == optimum:
        return 1.0
    if water_value < optimum:
        span = max(optimum - min_t, 1e-3)
        normalized = (water_value - min_t) / span
    else:
        span = max(max_t - optimum, 1e-3)
        normalized = (max_t - water_value) / span
    # Keep a low baseline so stressed plants still eke out growth instead of instant death.
    return max(0.0, min(1.0, 0.15 + 0.85 * normalized))
