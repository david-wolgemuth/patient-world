---
title: 2025-11-16 ABM Refactor
type: changelog
permalink: changelog/2025-11-16-abm-refactor
---

# 2025-11-16 ABM Refactor

- Adopted the ABM-oriented directory layout: `core/agents`, `core/environment`, `core/model`, `core/rules`, `core/scheduler`, `core/visualization`, and `core/repository`.
- Split `tick_grid` orchestration (now `core/scheduler.py`) from the behavior rules (`core/rules.py`) so logic layering is explicit.
- Merged the old snapshot + viz helpers into `core/visualization.py`, which now renders emoji grids and drives README snapshot updates.
- Relocated helper scripts into `scripts/` and removed the legacy `core/grid/` namespace to reduce confusion.
- Updated AGENTS.md, README, and architecture notes to describe the new structure and helper commands.
