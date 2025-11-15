"""World state management."""
from __future__ import annotations

import json
import random
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from core.grid import Cell, GridState

HISTORY_HEADER = "date,day,grass,rabbits,foxes"
WORLDS_DIR = Path("worlds")
DEFAULT_CELL_GRASS = 50
EXPECTED_MIGRATION_VERSION = 1


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
            f"Run: python migrations/0001_grid_state.py {world_name}"
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
    return paths.history


def log_history(world_name: str, state: GridState) -> None:
    history_file = ensure_history_file(world_name)
    line = (
        f"{datetime.now().date()},{state.day},{state.total_grass():.0f},"
        f"{state.total_rabbits():.0f},{state.total_foxes():.0f}\n"
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
    cells = [Cell(grass=base_grass, rabbits=0, foxes=0) for _ in range(width * height)]
    rng = random.Random()
    for _ in range(max(0, total_rabbits)):
        idx = rng.randrange(len(cells))
        cells[idx].rabbits += 1
    for _ in range(max(0, total_foxes)):
        idx = rng.randrange(len(cells))
        cells[idx].foxes += 1
    state = GridState(day=0, grid_width=width, grid_height=height, cells=cells, migration_version=EXPECTED_MIGRATION_VERSION)
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
    return (
        f"[{world_name}] Day {state.day}: "
        f"🌱{state.total_grass():.0f} 🐇{state.total_rabbits():.0f} 🦊{state.total_foxes():.0f}"
    )
