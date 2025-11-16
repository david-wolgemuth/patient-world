---
title: GridState Rollout
type: changelog
permalink: changelog/2025-11-15-grid-state-rollout
---

# GridState Rollout (2025-11-15)

- All worlds now store `GridState` objects (`grid_width`, `grid_height`, 100 `cells`) instead of scalar grass/rabbit/fox totals.
- Simulation logic now lives under dedicated modules (`core/environment/cell.py`, `core/model/state.py`, `core/rules.py`, `core/environment/spatial.py`, `core/visualization.py`) and the aggregate-only `core/simulation.py` was removed.
- `sim.py` gained explicit `init-grid` (bootstrap deterministic grids) alongside the existing `tick`/`forecast` subcommands, all operating directly on `GridState`.
- Snapshot rendering now draws the emoji grid and total counts via `core/visualization.py`, and README markers embed the new layout automatically.
- Added `migrations/0001_grid_state.py` helper to convert legacy `state.json` files once per world; backups land beside the migrated file as `state.json.backup`, and every state now carries `_migration_version` metadata enforced by `core/repository.py`.
- README sections cover the grid schema, new CLI usage, and instructions for migration/interventions.
