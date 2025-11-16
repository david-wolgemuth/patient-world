---
title: Core & CLI Basic Memory
type: note
permalink: architecture/core-cli-basic-memory
---

# Core & CLI Basic Memory
This note captures the architectural facts that routinely come up during onboarding and when reasoning about simulations. It answers the high-level “what do I need to know?” questions for Patient World.

## Module Map (`core/`)
- `core/__init__.py`: exposes top-level helpers (currently thin).
- `core/world.py`: world I/O (load/save state JSON, initialize worlds, append history, format summaries).
- `core/snapshot.py`: transforms a `GridState` into `snapshot.md` content and wires README updates.
- `core/analysis.py`: read-only forecasting utilities used by the `forecast` CLI command.
- `core/grid/` (grid simulation stack):
  - `state.py`: `GridState` aggregate (dimensions, per-cell array, entity lookup, spawning/movement helpers).
  - `tick.py`: main tick logic (`tick_grid`) that mutates a cloned `GridState`.
  - `viz.py`: visualization helpers for debugging/world snapshots.
- `core/environment/` (spatial substrate):
  - `cell.py`: `Cell` dataclass for per-tile biomass + entity references.
  - `spatial.py`: diffusion helpers used each tick (`apply_entity_diffusion`).

## Data Models
### `Cell` (`core/environment/cell.py`)
- Fields: `grass: int`, `entity_ids: List[int]`.
- Constructors/serialization: `from_dict`, `to_dict`, `copy`.
- Mutation helpers: `add_entity`, `remove_entity`.
- Query helpers: `count_type`, `rabbits`, `foxes`, `iter_entities` (yields resolved `Entity` instances).

### `GridState` (`core/grid/state.py`)
- Core fields: `day`, `grid_width`, `grid_height`, `cells: List[Cell]`, `entities: Dict[int, Entity]`, `next_entity_id`, `migration_version`.
- Lifecycle helpers: `from_dict`, `to_dict`, `clone`, `spawn_entity`, `remove_entity`, `move_entity`.
- Convenience queries: getters/setters for single cells; `neighbors`, totals (`total_grass`, `total_rabbits`, `total_foxes`), iteration over coordinates, and `entities_in_cell` / `entities_by_type`.
- Integrity: validates cell count in `__post_init__`, enforces bounds via `_index`.

## Entity System Status
The entity-based grid described in the vision docs is **already active**. Each grid cell only tracks IDs, while `GridState.entities` stores actual `Entity` objects with coordinates. `core/grid/tick.py` iterates over each individual rabbit/fox, updates per-entity hunger/age, handles reproduction, predation, movement (via `core.environment.apply_entity_diffusion`), and removes starving entities. There is no longer an aggregate population-per-cell model in the live simulation.

## CLI Surface (`sim.py`)
- `tick [world] [--count N] [--snapshot] [--log] [--update-readme]`: default command. Runs migrations, loads `worlds/<name>`, advances `GridState` N ticks via `core.grid.tick_grid`, persists state, and triggers optional side effects (snapshot file, history CSV append, README update for prod/staging).
- `forecast [world] [--days D] [--step S] [--seed N] [--format table|csv|json]`: read-only projections using `core.analysis.run`; outputs aggregated stats without mutating saved state.
- `init-grid <world> [--width W --height H --rabbits R --foxes F]`: bootstraps a brand-new grid world via `core.world.init_grid_world`, writes its snapshot, and prints dimensions.
- `migrate [world]`: runs pending migrations through `migrations/runner` against the specified world directory.
- Argument normalization allows `./sim.py --count 10` shorthand for `tick`.

## Repository Layout (root)
- Core simulation + CLI: `core/`, `sim.py`.
- Worlds & persistence: `worlds/<name>/` (`state.json`, `history.csv`, `snapshot.md` per world).
- Knowledge + process docs: `docs/` (agents, architecture, vision, changelog) and `AGENTS.md`.
- Automation/scripts: `commit_world.py` (staging helper), `qa_grid_sanity.py`, `migrations/` (state upgrade scripts).
- QA/experiments: `qa_grid_sanity.py`, `snapshot.md` (root-level default snapshot output).
- Tooling/infra: `.beads/` (task tracking), virtualenv in `venv/` when created; no dedicated `tests/` directory yet (QA scripts live at root).
- Config: README and doc tree describe workflows; no other dotfiles committed as of now.
