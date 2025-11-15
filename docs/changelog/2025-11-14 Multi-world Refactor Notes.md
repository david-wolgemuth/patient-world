---
title: 2025-11-14 Multi-world Refactor Notes
type: note
permalink: changelog/2025-11-14-multi-world-refactor-notes
---

# 2025-11-14 Multi-world Refactor Notes

## Summary
Captured lessons from implementing the multi-world state overhaul: directory layout, CLI expectations, snapshot handling, and staging world guidance.

## Details
- Worlds now live under `worlds/<name>/` with committed prod/staging directories and gitignored dev sandboxes.
- `sim.py` requires a positional world argument plus optional `--snapshot`; future CLI work should build on this argparse flow.
- Snapshot plumbing: `update_readme.py` reads from `worlds/<world>/snapshot.md` (default prod), and `commit_world.py` stages README + world data for the workflow.
- Staging world is created via `python create_world.py staging`; README should generally display prod snapshots even if staging is exercised.

## Tags
- #changelog
- #worlds
- #process

## Observations
- [guardrail] Keep README tied to prod snapshots unless explicitly demoing another world.
- [practice] Helper scripts (`create_world.py`, `commit_world.py`) keep automation clean and reusable.
- [note] Manual workflow_dispatch runs can target staging via the `world` input, but prod remains the cron default.

## Relations
- relates_to [[Project Vision]]
- relates_to [[Preferred Development Approach]]
