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
- Snapshot plumbing: `python sim.py ... --update-readme` refreshes README from `worlds/<world>/snapshot.md`, and `python scripts/commit_world.py <world>` stages README + world data for the workflow.
- Staging world can be cloned manually (e.g., `cp -R worlds/prod worlds/staging`) and README should generally display prod snapshots even if staging is exercised.
- Added `python sim.py forecast` for read-only QA runs (days/step/seed/format) so changes can be inspected without mutating worlds.

## Tags
- #changelog
- #worlds
- #process

## Observations
- [guardrail] Keep README tied to prod snapshots unless explicitly demoing another world.
- [practice] A single CLI with optional flags keeps daily development dead-simple while still allowing prod/staging side effects.
- [note] Manual workflow_dispatch runs can target staging via the `world` input, but prod remains the cron default.

## Relations
- relates_to [[Project Vision]]
- relates_to [[Preferred Development Approach]]
