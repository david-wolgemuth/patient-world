---
title: Migration Strategy
permalink: vision/migration-strategy
---

# Minimal Migration System

Git already tracks history, so migrations just need to be small, numbered Python scripts plus a version flag in
`state.json`. This keeps the workflow explicit without dragging in frameworks.

## Directory Layout

```
migrations/
├── __init__.py
├── 20251115_0001_grid_migration.py
└── YYYYMMDD_0002_whatever.py  # future migrations follow the same pattern
```

- Filenames follow `{timestamp}_{sequence}_{description}.py`.
- Scripts run independently (`python migrations/2025...py prod`).
- Use zero-padded counters so lexicographical order matches execution order.

## Version Metadata

Every `GridState` writes `_migration_version` inside `state.json`. Rules:

- Default to `0` for legacy worlds (handled automatically when loading raw JSON).
- Each migration script sets `_migration_version` to its `TARGET_VERSION`.
- `core/world.py` enforces `EXPECTED_MIGRATION_VERSION`, raising with the exact command to run if a world lags behind.

Example snippet (already applied in codebase):

```python
# GridState.to_dict()
return {
    "day": self.day,
    "grid_width": self.grid_width,
    "grid_height": self.grid_height,
    "cells": [...],
    "_migration_version": self.migration_version,
}
```

## Migration Script Template

```python
#!/usr/bin/env python3
"""Migration 0001: Convert aggregate state to grid."""

TARGET_VERSION = 1

def migrate_world(world_name: str):
    paths = world.get_paths(world_name)
    data = json.loads(paths.state.read_text())
    if data.get("_migration_version", 0) >= TARGET_VERSION:
        print("Already up to date"); return

    transformed = transform(data)          # pure dict→dict logic
    transformed["_migration_version"] = TARGET_VERSION
    backup = paths.state.with_suffix(".backup")
    shutil.copy2(paths.state, backup)
    paths.state.write_text(json.dumps(transformed, indent=2))
```

Key points:

- **Pure functions**: treat migrations as dict→dict transformations.
- **No rollbacks**: rely on Git if you need to revert.
- **Idempotent**: scripts should be safe to re-run (skip once `_migration_version >= TARGET_VERSION`).

## Running Migrations

```bash
python migrations/20251115_0001_grid_migration.py prod
python migrations/20251115_0001_grid_migration.py staging
python migrations/20251115_0001_grid_migration.py dev
```

- Run newest scripts last (numerical order).
- Worlds that already hit the target version just print “Already at migration vX”.
- Optional helper: add a `run_all(world)` function in `migrations/__init__.py` that shells out to each script in order if you want automation later.

## Workflow Checklist

1. Copy the latest script, bump `TARGET_VERSION`, and implement `transform()` logic.
2. Bump `EXPECTED_MIGRATION_VERSION` in `core/world.py`.
3. Add docs (README + changelog snippet as needed).
4. Run the migration script against every tracked world (prod, staging, dev).
5. Regenerate snapshots if state changed.
6. Commit scripts plus updated worlds.

That’s it—no frameworks, no databases, just readable Python files and one metadata integer.***