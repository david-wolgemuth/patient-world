"""World state management."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict

DEFAULT_STATE = {"day": 0, "grass": 500, "rabbits": 50, "foxes": 10}
HISTORY_HEADER = "date,day,grass,rabbits,foxes"
WORLDS_DIR = Path("worlds")


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


def load_world(world_name: str) -> Dict[str, float]:
    paths = get_paths(world_name)
    ensure_directory(paths.directory)
    if paths.state.exists():
        with paths.state.open() as fh:
            return json.load(fh)
    return DEFAULT_STATE.copy()


def save_world(world_name: str, state: Dict[str, float]) -> None:
    paths = get_paths(world_name)
    ensure_directory(paths.directory)
    with paths.state.open("w") as fh:
        json.dump(state, fh, indent=2)


def ensure_history_file(world_name: str) -> Path:
    paths = get_paths(world_name)
    ensure_directory(paths.directory)
    if not paths.history.exists():
        paths.history.write_text(HISTORY_HEADER + "\n")
    return paths.history


def log_history(world_name: str, state: Dict[str, float]) -> None:
    history_file = ensure_history_file(world_name)
    line = f"{datetime.now().date()},{state['day']},{state['grass']:.0f},{state['rabbits']:.0f},{state['foxes']:.0f}\n"
    with history_file.open("a") as fh:
        fh.write(line)


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
        if not dest.state.exists():
            with dest.state.open("w") as fh:
                json.dump(DEFAULT_STATE, fh, indent=2)
        ensure_history_file(world_name)


def snapshot_path(world_name: str) -> Path:
    paths = get_paths(world_name)
    ensure_directory(paths.directory)
    return paths.snapshot


def format_summary(world_name: str, state: Dict[str, float]) -> str:
    return (
        f"[{world_name}] Day {state['day']}: "
        f"Grass={state['grass']:.0f}, Rabbits={state['rabbits']:.0f}, Foxes={state['foxes']:.0f}"
    )
