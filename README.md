# Patient World

A self-running ecosystem simulation built around tiny rules that evolve over time. Each named world stores its own state/history/snapshot under `worlds/<name>/`, allowing prod, staging, and local sandboxes to coexist.

<!-- SNAPSHOT START -->
## 🌍 Patient World

**Day 7** • 2025-11-20

🐇🐇🐇🐇🐇🐇🐇🐇
🐇🐇🐇🐇🦊▫️🐇🦊
🐇🦊🦊🦊▫️🦊🐇🦊
🦊🦊🐇▫️🐇🐇🐇🦊
🦊🦊🦊🐇🦊🐇🐇🦊
▫️🦊▫️🐇▫️🐇🐇🦊
🐇🦊🦊🦊🐇🐇🦊🐇
▫️▫️🦊🐇🐇🦊🐇🐇

### Totals
🌱 171  🐇 92  🦊 30

<!-- SNAPSHOT END -->

## Worlds Layout
```
worlds/
├── prod/           # committed, long-running
│   ├── state.json
│   ├── history.csv
│   └── snapshot.md
├── staging/        # optional committed worlds (created via helper)
└── dev/            # gitignored sandbox created on demand
    ├── state.json
    ├── history.csv
    └── snapshot.md
```

## Grid State Format
All worlds now share a single grid schema (no legacy scalar fields):

```json
{
  "day": 47,
  "grid_width": 10,
  "grid_height": 10,
  "cells": [
    {"grass": 52, "rabbits": 3, "foxes": 0},
    {"grass": 48, "rabbits": 2, "foxes": 1},
    {"grass": 61, "rabbits": 0, "foxes": 0}
  ]
}
```

Cells are stored row-major (`y * width + x`). Helpers under `core/environment/`, `core/model/`, and `core/rules.py` handle JSON (de)serialization, neighbor
computation, totals, and emoji visualization. Each state also carries a `_migration_version` metadata field so the CLI
can refuse to run until all migrations have been applied.

Use `python3 migrations/0001_grid_state.py <world>` once per world to convert older aggregate state files. The script creates
`state.json.backup` beside the new grid file for safekeeping.

### Migration Versioning
- Migrations live under `migrations/` with zero-padded filenames (e.g., `0001_grid_state.py`).
- Every state writes `_migration_version` (currently `1`). `core/repository.py` checks this and instructs you to run the latest migration if a world lags behind.
- Migrations are Python scripts you run manually (one world at a time). They are idempotent—safe to re-run if unsure.
- See `docs/vision/Migration Strategy.md` for the full template (naming, helper ideas, and workflow).

## Running Locally
- Default flow: `./sim.py` or `./sim.py tick` → ticks `dev` once and prints the new totals.
- Examples:
  ```bash
  python3 sim.py --count 100            # fast-forward dev
  python3 sim.py prod --snapshot --log  # prod tick with side effects
  python3 sim.py staging --count 10     # experiment in staging
  python3 sim.py tick prod --snapshot --log --update-readme  # explicit subcommand
  ```
- Initialize new worlds with the grid-aware helper:
  ```bash
  python3 sim.py init-grid sandbox --width 20 --height 10 --rabbits 50 --foxes 12
  ```
- Worlds remain directory-based; `init-grid` fills in state/history/snapshot from scratch.

## Optional Side Effects
Add flags to the main command (or `tick` subcommand):

```bash
python3 sim.py prod --snapshot --log --update-readme
python3 sim.py dev --count 0 --snapshot      # regenerate snapshot without ticking
python3 sim.py staging --snapshot --update-readme
```

## Forecast (Read-only)
Project future states without mutating the world using `forecast`:

```bash
python3 sim.py forecast dev --days 365 --step 30
python3 sim.py forecast prod --days 1000 --seed 42
python3 sim.py forecast staging --days 365 --format csv > year.csv
```

`--days` defaults to 365 and `--step` defaults to 30, so `python3 sim.py forecast dev` is a quick smoke test when you don't need custom horizons.

Sample output:

```
Forecasting 'dev' world for 365 days (sampling every 30 days)
Initial state: Day 94, Grass=944, Rabbits=127, Foxes=74

Day    Grass   Rabbits  Foxes
  94     944      127      74
 124     811       96      58
 154     705       73      46
 ...

Summary (365 days):
  Grass    start=944  end=712  min=412  max=1000
  Rabbits  start=127  end=53   min=18   max=145
  Foxes    start=74   end=21   min=6    max=84
```

Use `--seed` for reproducible before/after comparisons and `--format csv|json` to feed spreadsheets or QA scripts.

To stage and commit a particular world's files manually (used by CI):
```bash
python scripts/commit_world.py prod
git push
```

## Creating or Cloning Worlds
For quick clones, copy directories directly:
```bash
cp -R worlds/prod worlds/staging-v2
```
Or bootstrap a blank world by deleting `state.json` and running `./sim.py staging-v2` once.

## Grid Sanity Check
Run `python3 scripts/qa_grid_sanity.py` before shipping risky changes to guarantee per-cell ticks stay stable (checks for negative counts, runaway populations, and verifies that diffusion spreads populations away from hotspots).

## Automation
- `.github/workflows/daily.yml` ticks `prod` every day at 12:00 UTC by running `python3 sim.py prod --snapshot --log --update-readme`, then commits via `python scripts/commit_world.py prod`.
- Manual `workflow_dispatch` runs accept a `world` input (default `staging`) so you can tick staging without touching cron schedules.

`snapshot.md` files inside `worlds/dev/` remain untracked via `.gitignore`, keeping experiments clean while prod/staging snapshots are committed automatically by the workflow.

## Staging World (Not Canonical)

Staging exists for experiments and may be reset at any time & have unrealistic number of days.

<details><summary>current snapshot</summary>

<!-- STAGING SNAPSHOT START -->
## 🌍 Patient World

**Day 62** • 2025-11-20

▫️▫️▫️▫️▫️▫️▫️▫️
▫️▫️▫️▫️▫️▫️▫️▫️
▫️▫️▫️▫️▫️▫️▫️▫️
▫️▫️▫️▫️▫️▫️▫️▫️
▫️▫️▫️▫️▫️▫️▫️▫️
▫️▫️▫️▫️▫️▫️▫️▫️
▫️▫️▫️▫️▫️▫️▫️▫️
▫️▫️▫️▫️▫️▫️▫️▫️

### Totals
🌱 111  🐇 0  🦊 0

<!-- STAGING SNAPSHOT END -->

</details>

## Environment Setup
Create an isolated virtualenv so Python dependencies stay contained:

```bash
python3 -m venv venv
source venv/bin/activate
# pip install -r requirements.txt  # once we start pinning deps
```
