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

import core.repository as repository

DEFAULT_GRID_SIZE = 10
TARGET_VERSION = 1


def migrate_world(world_name: str, grid_size: int = DEFAULT_GRID_SIZE) -> None:
    paths = repository.get_paths(world_name)
    state_path = paths.state
    if not state_path.exists():
        raise SystemExit(f"State file not found for '{world_name}' at {state_path}")

    legacy = json.loads(state_path.read_text())
    current_version = int(legacy.get("_migration_version", 0))
    if current_version >= TARGET_VERSION:
        print(f"{world_name} already at migration v{current_version}. Skipping.")
        return

    if "grid_width" in legacy and "cells" in legacy:
        if int(legacy.get("grid_width", grid_size)) == grid_size and int(legacy.get("grid_height", grid_size)) == grid_size:
            migrated = legacy
        else:
            migrated = _regrid(legacy, grid_size)
    else:
        migrated = _convert_scalar_to_grid(legacy, grid_size)

    migrated["_migration_version"] = TARGET_VERSION

    backup_path = state_path.with_suffix(state_path.suffix + ".backup")
    shutil.copy2(state_path, backup_path)
    state_path.write_text(json.dumps(migrated, indent=2))

    print(f"✓ Migrated {world_name} to v{TARGET_VERSION} (grid {grid_size}x{grid_size}).")
    print(f"Backup created at {backup_path}")


def _convert_scalar_to_grid(legacy: dict, grid_size: int) -> dict:
    cell_count = grid_size * grid_size
    grass_total = int(legacy.get("grass", 0))
    grass_base = grass_total // cell_count
    grass_remainder = grass_total % cell_count

    # NOTE: keep migrations focused on raw dicts so changes to runtime classes
    # (e.g., GridState/Cell) cannot break legacy scripts after the fact.
    cells = []
    for idx in range(cell_count):
        grass = grass_base + (1 if idx < grass_remainder else 0)
        cells.append({"grass": grass, "rabbits": 0, "foxes": 0})

    rng = random.Random()
    for _ in range(int(legacy.get("rabbits", 0))):
        cells[rng.randrange(cell_count)]["rabbits"] += 1
    for _ in range(int(legacy.get("foxes", 0))):
        cells[rng.randrange(cell_count)]["foxes"] += 1

    return _grid_state_dict(legacy.get("day", 0), grid_size, cells)


def _regrid(existing: dict, grid_size: int) -> dict:
    totals = {"grass": 0, "rabbits": 0, "foxes": 0}
    for cell in existing.get("cells", []):
        for key in totals:
            totals[key] += int(cell.get(key, 0))
    scalar = {
        "day": existing.get("day", 0),
        "grass": totals["grass"],
        "rabbits": totals["rabbits"],
        "foxes": totals["foxes"],
    }
    return _convert_scalar_to_grid(scalar, grid_size)


def _grid_state_dict(day: int, grid_size: int, cells: list[dict]) -> dict:
    return {
        "day": int(day),
        "grid_width": int(grid_size),
        "grid_height": int(grid_size),
        "cells": [
            {
                "grass": int(cell.get("grass", 0)),
                "rabbits": int(cell.get("rabbits", 0)),
                "foxes": int(cell.get("foxes", 0)),
            }
            for cell in cells
        ],
        "_migration_version": TARGET_VERSION,
    }


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
