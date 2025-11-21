"""World state management."""
from __future__ import annotations

import json
import random
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from core.environment import Cell, generate_water_distribution, random_environment_profile
from core.environment.producers import PRODUCER_PROFILES, PRODUCER_TYPES, empty_producer_map
from core.model import GridState

PRODUCER_HISTORY_FIELDS = [f"producer_{name}" for name in PRODUCER_TYPES]
HISTORY_HEADER = "timestamp,day,grass,rabbits,foxes"
if PRODUCER_HISTORY_FIELDS:
    HISTORY_HEADER = HISTORY_HEADER + "," + ",".join(PRODUCER_HISTORY_FIELDS)
WORLDS_DIR = Path("worlds")
DEFAULT_CELL_GRASS = 50
EXPECTED_MIGRATION_VERSION = 2


@dataclass
class WorldPaths:
    name: str
    directory: Path
    state: Path
    history: Path
    snapshot: Path


def get_paths(world_name: str) -> WorldPaths:
    directory = WORLDS_DIR / world_name
    return WorldPaths(
        name=world_name,
        directory=directory,
        state=directory / "state.json",
        history=directory / "history.csv",
        snapshot=directory / "snapshot.md",
    )


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_world(world_name: str) -> GridState:
    paths = get_paths(world_name)
    if not paths.state.exists():
        raise FileNotFoundError(f"No grid state for '{world_name}'. Run: ./sim.py init-grid {world_name}")
    with paths.state.open() as fh:
        data = json.load(fh)
    current_version = int(data.get("_migration_version", 0))
    if current_version < EXPECTED_MIGRATION_VERSION:
        raise ValueError(
            f"World '{world_name}' is at migration v{current_version}, expected v{EXPECTED_MIGRATION_VERSION}. "
            f"Run: ./sim.py migrate {world_name}"
        )
    return GridState.from_dict(data)


def save_world(world_name: str, state: GridState) -> None:
    paths = get_paths(world_name)
    ensure_directory(paths.directory)
    with paths.state.open("w") as fh:
        json.dump(state.to_dict(), fh, indent=2)


def ensure_history_file(world_name: str) -> Path:
    paths = get_paths(world_name)
    ensure_directory(paths.directory)
    if not paths.history.exists():
        paths.history.write_text(HISTORY_HEADER + "\n")
    else:
        with paths.history.open("r+") as fh:
            header = fh.readline().strip()
            if not header:
                fh.seek(0)
                fh.write(HISTORY_HEADER + "\n")
                fh.truncate()
            elif header != HISTORY_HEADER:
                remainder = fh.read()
                fh.seek(0)
                fh.write(HISTORY_HEADER + "\n")
                if remainder:
                    fh.write(remainder)
                fh.truncate()
    return paths.history


def log_history(world_name: str, state: GridState) -> None:
    """Append the current state snapshot with a UTC ISO8601 timestamp."""

    history_file = ensure_history_file(world_name)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    producers = state.producer_totals()
    producer_segment = ""
    if PRODUCER_HISTORY_FIELDS:
        ordered = ",".join(str(producers.get(name, 0)) for name in PRODUCER_TYPES)
        producer_segment = f",{ordered}"
    line = (
        f"{timestamp},{state.day},{state.total_grass():.0f},{state.total_rabbits():.0f},"
        f"{state.total_foxes():.0f}{producer_segment}\n"
    )
    with history_file.open("a") as fh:
        fh.write(line)


def init_grid_world(
    world_name: str,
    *,
    width: int = 10,
    height: int = 10,
    total_grass: int | None = None,
    total_rabbits: int = 20,
    total_foxes: int = 5,
) -> GridState:
    ensure_directory(get_paths(world_name).directory)
    base_grass = DEFAULT_CELL_GRASS if total_grass is None else int(total_grass)
    rng = random.Random()
    water_noise = generate_water_distribution(width, height, seed=f"{world_name}-water")
    cells = []
    for idx in range(width * height):
        env_water, fertility, temperature = random_environment_profile(rng.randrange(1_000_000_000))
        water = water_noise[idx] if idx < len(water_noise) else env_water
        producers = empty_producer_map()
        fast_factor = 0.75 + fertility * 0.35
        producers["fast_grass"] = max(4, int(base_grass * fast_factor))
        seasonal_factor = max(0.1, fertility * 0.5) + max(0.0, water - 0.4) * 0.4
        producers["seasonal_annuals"] = int(base_grass * seasonal_factor)
        producers["forb_wildflowers"] = int(producers["fast_grass"] * (0.25 + fertility * 0.4))
        shrub_seed = int(base_grass * (0.18 + fertility * 0.3))
        producers["slow_shrubs"] = max(0, shrub_seed)
        producers["deep_roots"] = max(0, int(shrub_seed * 0.55))
        wet_bonus = max(0.0, water - 0.55)
        very_wet = max(0.0, water - 0.75)
        dry_bonus = max(0.0, 0.45 - water)
        producers["moss_carpet"] = int(base_grass * wet_bonus * 0.6)
        producers["reed_beds"] = int(base_grass * very_wet * 0.8)
        producers["bog_sedges"] = int(base_grass * very_wet * 0.7)
        producers["fungal_mat"] = int(base_grass * min(fertility, wet_bonus) * 0.5)
        producers["succulent_cluster"] = int(base_grass * dry_bonus * 0.9)
        producers["desert_bloomers"] = int(producers["succulent_cluster"] * 0.6)
        producers["lichen_crust"] = int(base_grass * dry_bonus * 0.65)
        if producers["slow_shrubs"] > 0:
            producers["fruit_trees"] = int(producers["slow_shrubs"] * fertility * 0.6)
            producers["vine_canopy"] = int(producers["slow_shrubs"] * wet_bonus * 0.8)
            producers["pioneer_brush"] = int(producers["slow_shrubs"] * (0.25 + fertility * 0.4))
            producers["palm_crowns"] = int(producers["fruit_trees"] * (0.2 + wet_bonus * 0.8))
        if producers["deep_roots"] > 0:
            producers["needle_conifers"] = int(producers["deep_roots"] * (0.5 + dry_bonus * 0.8))
        if producers["bog_sedges"] > 0:
            producers["mangrove_canopy"] = int(producers["bog_sedges"] * (0.3 + wet_bonus * 0.7))
        cell = Cell(
            producers=producers,
            water=water,
            fertility=fertility,
            temperature=temperature,
        )
        cell.clamp_layers()
        cells.append(cell)
    state = GridState(
        day=0,
        grid_width=width,
        grid_height=height,
        cells=cells,
        migration_version=EXPECTED_MIGRATION_VERSION,
    )
    total_cells = width * height
    for _ in range(max(0, total_rabbits)):
        idx = rng.randrange(total_cells)
        x = idx % width
        y = idx // width
        state.spawn_entity("rabbit", x, y)
    for _ in range(max(0, total_foxes)):
        idx = rng.randrange(total_cells)
        x = idx % width
        y = idx // width
        state.spawn_entity("fox", x, y)
    save_world(world_name, state)
    ensure_history_file(world_name)
    return state


def create_world(world_name: str, from_world: str | None = None) -> None:
    dest = get_paths(world_name)
    ensure_directory(dest.directory)
    if from_world:
        src = get_paths(from_world)
        if not src.state.exists():
            raise FileNotFoundError(f"Source world '{from_world}' not found at {src.directory}")
        ensure_directory(src.directory)
        for filename in ("state.json", "history.csv", "snapshot.md"):
            source_path = src.directory / filename
            if source_path.exists():
                shutil.copy2(source_path, dest.directory / filename)
    else:
        init_grid_world(world_name)


def snapshot_path(world_name: str) -> Path:
    paths = get_paths(world_name)
    ensure_directory(paths.directory)
    return paths.snapshot


def format_summary(world_name: str, state: GridState) -> str:
    water = state.water_stats()
    dry_text = f"{int(water['dry_cells'])} dry" if water["dry_cells"] else "no dry cells"
    producer_totals = state.producer_totals()
    producer_bits = " ".join(
        f"{PRODUCER_PROFILES[name].emoji}{producer_totals.get(name, 0):.0f}" for name in PRODUCER_TYPES
    )
    return (
        f"[{world_name}] Day {state.day}: "
        f"{producer_bits} | 🐇{state.total_rabbits():.0f} 🦊{state.total_foxes():.0f} "
        f"| 💧mean {water['mean']:.2f} ({dry_text})"
    )
