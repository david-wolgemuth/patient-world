# Patient World

A self-running ecosystem simulation built around tiny rules that evolve over time. Each named world stores its own state/history/snapshot under `worlds/<name>/`, allowing prod, staging, and local sandboxes to coexist.

<!-- SNAPSHOT START -->
## 🌍 Patient World

**Day 59** • 2026-01-11

🐇🐇🌱🌱🌱🐇🐇🐇
🌼🌱🐇🌼🌼🌱🌱🌱
🌱🌱🌱🌱🌼🌱🌱🌱
🌱🌱🌱🌱🌸🌱🌱🌱
🌱🌱🌱🌱🌱🌱🌱🌱
🌱🌱🌱🌼🌼🌱🌼🌸
🌼🌱🍀🌱🌱🌱🌱🌱
🌱🌱🌱🌱🌼🌱🐇🐇

### Totals
🌱 6490  🐇 34  🦊 0

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
    {
      "producers": {
        "fast_grass": 52,
        "seasonal_annuals": 18,
        "forb_wildflowers": 11,
        "lichen_crust": 4,
        "slow_shrubs": 9,
        "deep_roots": 4,
        "moss_carpet": 7,
        "reed_beds": 3,
        "bog_sedges": 6,
        "fungal_mat": 5,
        "succulent_cluster": 2,
        "desert_bloomers": 0,
        "fruit_trees": 4,
        "needle_conifers": 2,
        "pioneer_brush": 2,
        "vine_canopy": 1,
        "palm_crowns": 0,
        "mangrove_canopy": 0
      },
      "entity_ids": [12, 19],
      "water": 0.64,
      "fertility": 0.47,
      "temperature": 0.58
    }
  ]
}
```

Cells are stored row-major (`y * width + x`). Each carries an environment profile (water/fertility/temperature) plus four producer guilds that can coexist in the same tile. Helpers under `core/environment/`, `core/model/`, and `core/rules.py` handle JSON (de)serialization, neighbor
computation, totals, and emoji visualization. Each state also carries a `_migration_version` metadata field so the CLI
can refuse to run until all migrations have been applied.

### Producer Guilds & Emojis
#### Ground Layer (cap ≈ 200 per cell)
| Emoji | Guild | Traits | Tradeoffs |
| --- | --- | --- | --- |
| 🌱 | Fast grass | Rapid regrowth immediately after rain or grazing. | Shallow roots; collapses quickly if shrubs/vines don't shelter soil. |
| 🌼 | Seasonal annuals | Explosive bursts inside a narrow growing window. | Drop to seed banks outside bloom season; first target for herbivores. |
| 🌺 | Forb wildflowers | Mid-season forbs that boost pollen/seed production once grass is stable. | Need a healthy fast-grass base and scorch easily in droughts. |
| 🪨 | Lichen crust | Colonizes barren, dry tiles and slowly stabilizes soil. | Extremely slow growth and low forage value. |
| 🍀 | Moss carpets | Keep soil moist and prevent erosion in shaded wetlands. | Suffocate if soils dry out or temperatures spike. |
| 🎋 | Reed beds | Tall marsh grasses that thrive on flooded shores. | Require consistently wet cells; offer little nutrition when dry. |
| 🪷 | Bog sedges | Thick freshwater mats that extend wetlands inland. | Collapse when water tables fall; slow to reestablish elsewhere. |
| 🍄 | Fungal mats | Recycle woody litter into nutrients while shading soil. | Depend on moss/shrub litter; heavy dormancy outside humid stretches. |
| 🌵 | Succulent clusters | Store water for drought years and stabilize barren tiles. | Spread slowly and lose ground to faster guilds in wet seasons. |
| 🌻 | Desert bloomers | Rare but dramatic blooms triggered by storms. | Spend most of the year dormant; need succulents nearby to reseed. |

#### Canopy Layer (cap ≈ 150 per cell)
| Emoji | Guild | Traits | Tradeoffs |
| --- | --- | --- | --- |
| 🌿 | Slow shrubs | Woody understory that shields grass and feeds browsers. | Need established ground cover; crowding limits expansion but protects soil. |
| 🌳 | Deep-rooted plants | Anchor the canopy and tap deep water tables. | Only arrive where shrubs already thrive; slow to recover after disturbance. |
| 🍎 | Fruit trees | Produce rich forage and shade once shrubs mature. | Sensitive to drought; require high fertility and shrub support. |
| 🌲 | Needle conifers | Tolerate poor soils and cold/dry slopes. | Slow growth and acidic litter hinder shrub regeneration. |
| 🍂 | Pioneer brush | Fire-following shrubs that recolonize disturbed cells. | Short-lived and easily outcompeted once taller guilds return. |
| 🌸 | Vine canopy | Opportunistic climbers that exploit shrub scaffolding. | Go dormant outside warm, wet seasons; can smother shrubs if unchecked. |
| 🌴 | Palm crowns | Humid floodplain specialists that provide fruit and shade. | Struggle in cold/dry cells and require high water tables. |
| 🍃 | Mangrove canopy | Salt-tolerant trees that bridge land and tidal wetlands. | Only thrive in saturated coastal cells; slow to expand inland. |

Tick summaries and forecast tables now list each emoji so you can see where biomass shifts between guilds. Rabbits graze annuals → grass → reeds/moss → shrubs, so keeping multiple guilds in a cell is the only way to avoid bare ground after a boom. Visualization uses the guild emojis whenever a cell is free of animals.

Use `python3 migrations/0001_grid_state.py <world>` once per world to convert older aggregate state files. The script creates
`state.json.backup` beside the new grid file for safekeeping.

### Migration Versioning
- Migrations live under `migrations/` with zero-padded filenames (e.g., `0001_grid_state.py`).
- Every state writes `_migration_version` (currently `1`). `core/repository.py` checks this and instructs you to run the latest migration if a world lags behind.
- Migrations are Python scripts you run manually (one world at a time). They are idempotent—safe to re-run if unsure.
- See `docs/vision/Migration Strategy.md` for the full template (naming, helper ideas, and workflow).

## Running Locally
- Default flow: `./sim.py` or `./sim.py tick` → ticks `dev` once and prints the new totals.
- The one-line summary now includes 💧water mean plus the number of "dry" cells (≤0.2 water) so you can tell when abiotic stress is building without cracking open snapshots.
- Examples:
  ```bash
  python3 sim.py --count 100            # fast-forward dev
  python3 sim.py prod --snapshot --log              # prod tick with side effects
  python3 sim.py staging --count 10                 # experiment in staging
  python3 sim.py dev --capacity-report --count 25   # show carrying-capacity hotspots
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
python3 sim.py tick dev --capacity-report    # print capacity stats after ticking
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
Initial state: Day 94, Biomass=944, Rabbits=127, Foxes=74

Day    Biomass Rabbits  Foxes   Water  Dry
  94     944      127      74   0.57     0
  124     811       96      58   0.55     2
  154     705       73      46   0.53     4
 ...

Summary (365 days):
  Biomass  start=944  end=712  min=412  max=1000
  Rabbits  start=127  end=53   min=18   max=145
  Foxes    start=74   end=21   min=6    max=84
  Water    mean start=0.57 end=0.54 range=0.52-0.59 cell range=0.18-0.94
    Dry cells max=7 on day 210 (<=0.2 water)

Capacity-limited events: 82 across 19 cells (active on 12 days)
  Hotspots: (4,3)×10, (5,3)×8, (6,3)×7
```

The `Biomass` column represents the total live producer biomass across every guild (fast grass, shrubs, mosses, vines, etc.), so the quick-look metric no longer clashes with the dedicated `fast_grass` guild that appears in the per-guild columns.

Use `--seed` for reproducible before/after comparisons and `--format csv|json` to feed spreadsheets or QA scripts. CSV/JSON formats include the same water fields as the table view so downstream tooling can read abiotic trends directly.
Add `--capacity-report` to either `tick` or `forecast` to include per-run carrying-capacity stats and layer totals; the summaries also show up automatically in table output and can be appended to CSV exports via `--capacity-report`.
Every forecast row now includes per-guild columns (one per emoji), and the summary block lists start/end/min/max/extinction stats for each producer so you can trace biomass shifts over long horizons.

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

**Day 419** • 2026-01-10

🌱🌱🌱🌱🌱🌱🌱🌱
🌱🌱🌱🌱🌱🌱🌱🌱
🌱🌱🌱🌱🍃🌱🌱🌱
🌱🌱🌱🌱🌱🌱🌱🌱
🍃🌱🌱🌱🌱🌱🌱🌱
🌱🌱🌿🌱🌱🌱🌱🌱
🌱🌱🍃🌱🌱🌱🌱🌱
🌱🌱🌱🌱🌱🌱🌱🌱

### Totals
🌱 8255  🐇 0  🦊 0

<!-- STAGING SNAPSHOT END -->

</details>

## Environment Setup
Create an isolated virtualenv so Python dependencies stay contained:

```bash
python3 -m venv venv
source venv/bin/activate
# pip install -r requirements.txt  # once we start pinning deps
```
