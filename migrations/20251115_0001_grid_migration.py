#!/usr/bin/env python3
"""ONE-TIME migration from legacy aggregate format to GridState."""
from __future__ import annotations

import json
import random
import shutil
import sys
from pathlib import Path

# Ensure repo root is importable when running from migrations/ directory
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core import world
from core.grid import Cell, GridState

DEFAULT_GRID_SIZE = 10


def migrate_world(world_name: str, grid_size: int = DEFAULT_GRID_SIZE) -> None:
    paths = world.get_paths(world_name)
    state_path = paths.state
    if not state_path.exists():
        raise SystemExit(f"State file not found for '{world_name}' at {state_path}")

    legacy = json.loads(state_path.read_text())
    if "grid_width" in legacy:
        print(f"{world_name} already uses grid format. Skipping.")
        return

    cell_count = grid_size * grid_size
    grass_total = int(legacy.get("grass", 0))
    grass_base = grass_total // cell_count
    grass_remainder = grass_total % cell_count

    cells = []
    for idx in range(cell_count):
        grass = grass_base + (1 if idx < grass_remainder else 0)
        cells.append(Cell(grass=grass, rabbits=0, foxes=0))

    rng = random.Random()
    for _ in range(int(legacy.get("rabbits", 0))):
        cells[rng.randrange(cell_count)].rabbits += 1
    for _ in range(int(legacy.get("foxes", 0))):
        cells[rng.randrange(cell_count)].foxes += 1

    new_state = GridState(day=int(legacy.get("day", 0)), grid_width=grid_size, grid_height=grid_size, cells=cells)

    backup_path = state_path.with_suffix(state_path.suffix + ".backup")
    shutil.copy2(state_path, backup_path)
    world.save_world(world_name, new_state)

    print(f"Migrated {world_name} to {grid_size}x{grid_size} grid.")
    print(f"Backup created at {backup_path}")


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit("Usage: python migrations/20251115_0001_grid_migration.py <world> [grid_size]")
    world_name = argv[0]
    grid_size = DEFAULT_GRID_SIZE
    if len(argv) > 1:
        grid_size = int(argv[1])
        if grid_size <= 0:
            raise SystemExit("grid_size must be positive")
    migrate_world(world_name, grid_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
