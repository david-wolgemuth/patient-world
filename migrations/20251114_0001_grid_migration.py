#!/usr/bin/env python3
"""One-time migration: convert scalar world state to 10x10 grid format.

Usage:
    python migrations/20251114_0001_grid_migration.py worlds/prod/state.json

Creates a backup of the original file (<path>.bak) and writes the new grid-based
state in place. Distribution is intentionally simple: totals are split evenly
across cells (with remainder sprinkled into the first few cells).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

GRID_WIDTH = 10
GRID_HEIGHT = 10


def even_split(total: float, cells: int) -> list[int]:
    base = int(total // cells)
    remainder = int(total % cells)
    values = [base] * cells
    for i in range(remainder):
        values[i] += 1
    return values


def migrate(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"State file not found: {path}")

    original = json.loads(path.read_text())
    width = GRID_WIDTH
    height = GRID_HEIGHT
    cell_count = width * height

    grass_values = even_split(original.get("grass", 0), cell_count)
    rabbit_values = even_split(original.get("rabbits", 0), cell_count)
    fox_values = even_split(original.get("foxes", 0), cell_count)

    cells = []
    for i in range(cell_count):
        cells.append(
            {
                "grass": grass_values[i],
                "rabbits": rabbit_values[i],
                "foxes": fox_values[i],
            }
        )

    migrated = {
        "day": original.get("day", 0),
        "grid_width": width,
        "grid_height": height,
        "cells": cells,
    }

    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_text(json.dumps(original, indent=2))
    path.write_text(json.dumps(migrated, indent=2))
    print(f"Migrated {path} -> grid {width}x{height}. Backup at {backup}.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python migrations/20251114_0001_grid_migration.py <state.json>")
    migrate(Path(sys.argv[1]))
