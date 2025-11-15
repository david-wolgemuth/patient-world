# Patient World

A self-running ecosystem simulation built around tiny rules that evolve over time. Each named world stores its own state/history/snapshot under `worlds/<name>/`, allowing prod, staging, and local sandboxes to coexist.

<!-- SNAPSHOT START -->
## 🌍 Patient World

**Day 4** • 2025-11-14

### Population
```
🌱 Grass    ███████████             592
🐇 Rabbits  █                        92
🦊 Foxes                             17
```

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

## Running Locally
- Default flow: `./sim.py` or `./sim.py tick` → ticks `dev` once and prints the new totals.
- Examples:
  ```bash
  python sim.py --count 100            # fast-forward dev
  python sim.py prod --snapshot --log  # prod tick with side effects
  python sim.py staging --count 10     # experiment in staging
  python sim.py tick prod --snapshot --log --update-readme  # explicit subcommand
  ```
- Worlds are created automatically on first run (directories + default state/history).

## Optional Side Effects
Add flags to the main command (or `tick` subcommand):

```bash
python sim.py prod --snapshot --log --update-readme
python sim.py dev --count 0 --snapshot      # regenerate snapshot without ticking
python sim.py staging --snapshot --update-readme
```

## Forecast (Read-only)
Project future states without mutating the world using `forecast`:

```bash
python sim.py forecast dev --days 365 --step 30
python sim.py forecast prod --days 1000 --seed 42
python sim.py forecast staging --days 365 --format csv > year.csv
```

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
python commit_world.py prod
git push
```

## Creating or Cloning Worlds
For quick clones, copy directories directly:
```bash
cp -R worlds/prod worlds/staging-v2
```
Or bootstrap a blank world by deleting `state.json` and running `./sim.py staging-v2` once.

## Automation
- `.github/workflows/daily.yml` ticks `prod` every day at 12:00 UTC by running `python sim.py prod --snapshot --log --update-readme`, then commits via `python commit_world.py prod`.
- Manual `workflow_dispatch` runs accept a `world` input (default `staging`) so you can tick staging without touching cron schedules.

`snapshot.md` files inside `worlds/dev/` remain untracked via `.gitignore`, keeping experiments clean while prod/staging snapshots are committed automatically by the workflow.

## Staging World (Not Canonical)

Staging exists for experiments and may be reset at any time & have unrealistic number of days.

<details><summary>current snapshot</summary>

<!-- STAGING SNAPSHOT START -->
## 🌍 Patient World

**Day 15** • 2025-11-15

### Population
```
🌱 Grass    ████████                445
🐇 Rabbits  ██                      131
🦊 Foxes    █                        81
```

<!-- STAGING SNAPSHOT END -->

</details>

## Environment Setup
Create an isolated virtualenv so Python dependencies stay contained:

```bash
python3 -m venv venv
source venv/bin/activate
# pip install -r requirements.txt  # once we start pinning deps
```
