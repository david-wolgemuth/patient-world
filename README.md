# Patient World

A self-running ecosystem simulation built around tiny rules that evolve over time. Each named world stores its own state/history/snapshot under `worlds/<name>/`, allowing prod, staging, and local sandboxes to coexist.

<!-- SNAPSHOT START -->
## 🌍 Patient World

**Day 3** • 2025-11-14

### Population
```
🌱 Grass    ███████████             571
🐇 Rabbits  █                        74
🦊 Foxes                             15
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
- `python sim.py <world> [--snapshot]`
- Example (dev sandbox):
  ```bash
  python sim.py dev --snapshot
  cat worlds/dev/snapshot.md
  ```
- Worlds are created automatically on first run (directories + default state/history).

## Updating README Manually
```bash
python update_readme.py prod      # or staging-v2, etc.
# Staging section uses --staging to update the separate snapshot block
python update_readme.py staging --staging
git diff README.md                # inspect snapshot change
```

To stage and commit a particular world's files manually:
```bash
python commit_world.py prod
git push
```

## Creating or Cloning Worlds
Use the helper script to bootstrap directories:
```bash
python create_world.py staging-v2          # fresh world with default state
python create_world.py staging --from=prod # clone current prod state/history
```

## Automation
- `.github/workflows/daily.yml` ticks `prod` every day at 12:00 UTC and runs `commit_world.py` to store the updated world data plus README.
- Manual `workflow_dispatch` runs accept a `world` input (default `staging`) so you can tick staging without touching cron schedules.

`snapshot.md` files inside `worlds/dev/` remain untracked via `.gitignore`, keeping experiments clean while prod/staging snapshots are committed automatically by the workflow.

## Staging World (Not Canonical)
Staging exists for experiments and may be reset at any time. Day counts below are illustrative only.

<!-- STAGING SNAPSHOT START -->
## 🌍 Patient World

**Day 11** • 2025-11-14

### Population
```
🌱 Grass    ███████████             576
🐇 Rabbits  ████                    205
🦊 Foxes                             47
```

<!-- STAGING SNAPSHOT END -->

## Environment Setup
Create an isolated virtualenv so Python dependencies stay contained:

```bash
python3 -m venv .venv
source .venv/bin/activate
```
