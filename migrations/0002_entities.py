#!/usr/bin/env python3
"""Migration 0002: convert cell aggregates into entity registry."""
from __future__ import annotations

import json
import random
import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core import world

TARGET_VERSION = 2


def migrate_world(world_name: str) -> None:
    paths = world.get_paths(world_name)
    state_path = paths.state
    if not state_path.exists():
        raise SystemExit(f"State file not found for '{world_name}'. Run init-grid first.")

    data = json.loads(state_path.read_text())
    current_version = int(data.get("_migration_version", 0))
    if current_version >= TARGET_VERSION:
        return

    migrated = migrate_state(data)

    backup_path = state_path.with_suffix(state_path.suffix + ".v1.backup")
    shutil.copy2(state_path, backup_path)
    state_path.write_text(json.dumps(migrated, indent=2))
    print(f"✓ Migrated {world_name} to entity registry (backup at {backup_path})")


def migrate_state(data: dict) -> dict:
    width = int(data.get("grid_width", 0))
    height = int(data.get("grid_height", 0))
    cells = data.get("cells", [])
    if not width or not height or not cells:
        raise SystemExit("Grid dimensions missing; run 0001_grid_state first.")

    rng = random.Random(42)
    entities: dict[int, dict] = {}
    next_id = 1
    for idx, cell in enumerate(cells):
        entity_ids: list[int] = []
        x = idx % width
        y = idx // width

        rabbits = int(cell.get("rabbits", 0))
        for _ in range(rabbits):
            entities[next_id] = _build_entity(next_id, "rabbit", x, y, rng.randint(0, 5), rng.randint(0, 20))
            entity_ids.append(next_id)
            next_id += 1

        foxes = int(cell.get("foxes", 0))
        for _ in range(foxes):
            entities[next_id] = _build_entity(next_id, "fox", x, y, rng.randint(0, 7), rng.randint(0, 30))
            entity_ids.append(next_id)
            next_id += 1

        cell["entity_ids"] = entity_ids
        cell.pop("rabbits", None)
        cell.pop("foxes", None)

    data["entities"] = entities
    data["next_entity_id"] = next_id
    data["_migration_version"] = TARGET_VERSION
    return data


def _build_entity(entity_id: int, entity_type: str, x: int, y: int, hunger: int, age: int) -> dict:
    return {
        "id": entity_id,
        "type": entity_type,
        "x": x,
        "y": y,
        "hunger": hunger,
        "age": age,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python migrations/0002_entities.py <world>")
    migrate_world(sys.argv[1])
