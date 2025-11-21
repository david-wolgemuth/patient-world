#!/usr/bin/env python3
"""Migration 0003: convert grass → producers + add environment fields."""
from __future__ import annotations

import json
import random
import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import core.repository as repository
from core.environment.producers import empty_producer_map

TARGET_VERSION = 3


def migrate_world(world_name: str) -> None:
    paths = repository.get_paths(world_name)
    state_path = paths.state
    if not state_path.exists():
        raise SystemExit(f"State file not found for '{world_name}'. Run init-grid first.")

    data = json.loads(state_path.read_text())
    current_version = int(data.get("_migration_version", 0))
    if current_version >= TARGET_VERSION:
        return

    migrated = migrate_state(data)

    backup_path = state_path.with_suffix(state_path.suffix + ".v2.backup")
    shutil.copy2(state_path, backup_path)
    state_path.write_text(json.dumps(migrated, indent=2))
    print(f"✓ Migrated {world_name} to producer system (backup at {backup_path})")


def migrate_state(data: dict) -> dict:
    """Convert legacy grass field to producers map and add environment fields."""
    cells = data.get("cells", [])
    if not cells:
        raise SystemExit("No cells found; run previous migrations first.")

    rng = random.Random(42)
    
    for cell in cells:
        # Skip if already migrated
        if "producers" in cell:
            continue
            
        # Convert grass → producers
        legacy_grass = int(cell.get("grass", 0))
        producers = empty_producer_map()
        producers["fast_grass"] = legacy_grass
        # All other producers start at 0
        cell["producers"] = producers
        
        # Remove legacy grass field
        cell.pop("grass", None)
        
        # Add environment fields if missing
        if "water" not in cell:
            cell["water"] = rng.uniform(0.4, 0.8)
        if "fertility" not in cell:
            cell["fertility"] = rng.uniform(0.4, 0.7)
        if "temperature" not in cell:
            cell["temperature"] = rng.uniform(0.3, 0.7)
        if "water_history" not in cell:
            cell["water_history"] = [cell["water"]]
        if "limiting_factor" not in cell:
            cell["limiting_factor"] = None
        if "limiting_value" not in cell:
            cell["limiting_value"] = 1.0

    data["_migration_version"] = TARGET_VERSION
    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python migrations/0003_producers_and_water.py <world>")
    migrate_world(sys.argv[1])