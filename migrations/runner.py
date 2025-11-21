#!/usr/bin/env python3
"""Minimal migration runner used by sim.py."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Iterable

MIGRATIONS_DIR = Path(__file__).resolve().parent
MIGRATION_MODULES = ["migrations.0001_grid_state", "migrations.0002_entities", "migrations.0003_producers_and_water"]


def run_pending(world_name: str, silent: bool = False) -> bool:
    """Run all pending migrations for a world. Returns True if state changed."""
    changed = False
    for module_name in MIGRATION_MODULES:
        module = importlib.import_module(module_name)
        if hasattr(module, "migrate_world"):
            before = _current_version(world_name)
            module.migrate_world(world_name)
            after = _current_version(world_name)
            if after > before:
                changed = True
                if not silent:
                    print(f"{world_name}: migration {before} -> {after}")
    return changed


def _current_version(world_name: str) -> int:
    state_path = Path("worlds") / world_name / "state.json"
    if not state_path.exists():
        return 0
    try:
        data = json.loads(state_path.read_text())
    except json.JSONDecodeError:
        return 0
    return int(data.get("_migration_version", 0))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m migrations.runner <world>")
    run_pending(sys.argv[1])
