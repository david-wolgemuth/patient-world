---
title: GridState Rollout
type: changelog
permalink: changelog/2025-11-15-grid-state-rollout
---

# GridState Rollout (2025-11-15)

- All worlds now store `GridState` objects (`grid_width`, `grid_height`, 100 `cells`) instead of scalar grass/rabbit/fox totals.
- Simulation logic moved under `core/grid/` (`cell.py`, `state.py`, `tick.py`, `diffusion.py`, `viz.py`) and the aggregate-only `core/simulation.py` was removed.
- `sim.py` gained explicit `init-grid` (bootstrap deterministic grids) alongside the existing `tick`/`forecast` subcommands, all operating directly on `GridState`.
- Snapshot rendering now draws the emoji grid and total counts via `core/grid/viz.py`, and README markers embed the new layout automatically.
- Added `migrate.py` helper to convert legacy `state.json` files once per world; backups land beside the migrated file as `state.json.backup`.
- README sections cover the grid schema, new CLI usage, and instructions for migration/interventions.
