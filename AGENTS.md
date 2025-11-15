# Patient World – Agent Handbook

## Project Overview
Patient World is a minimal autonomous ecosystem sim. `sim.py` holds the entire loop: load JSON state, run `tick`, persist state, append history, and optionally emit a snapshot for README. Each world stores its data under `worlds/<name>/` (`state.json`, `history.csv`, `snapshot.md`). GitHub Actions ticks the `prod` world daily at 12:00 UTC and commits the updated world directory plus README.

## Knowledge Base (Basic Memory)
- Location: `docs/`
- Structure: folders such as `vision/` (project goals, constraints, architecture) and `agents/` (meta guides).
- Helpful entries:
  - `docs/vision/Preferred Development Approach.md`: iteration style, tooling, and guardrails.
  - `docs/vision/Architecture Principles (MVP-Level).md`: prod vs. dev guardrails.
  - `docs/agents/Basic Memory Usage.md`: CLI usage, project configuration, and observations.
  - `docs/agents/Beads Workflow Guide.md`: how to structure and size tasks in Beads.

Use `/Users/david/.local/bin/bm tool ... --project patient-world` to edit or read these notes. Snapshot markers in README reference `worlds/<world>/snapshot.md`, produced via `python sim.py <world> --snapshot`.

## CLI + Structure
- Core logic lives under `core/` (`simulation.py`, `world.py`, `snapshot.py`).
- `sim.py` handles load → tick → save with optional side effects:
  - `./sim.py` ticks `dev` once (no subcommand needed).
  - `./sim.py tick prod --snapshot --log --update-readme` mirrors the GitHub Action.
  - `./sim.py dev --count 1000` for fast-forwarding.
  - `./sim.py forecast dev --days 365 --step 30 [--format csv|json]` provides read-only projections for QA (use `--seed` for reproducible comparisons).
- Rare helpers:
  - `python commit_world.py prod` stages README + world artifacts via git.
  - Clone worlds via `cp -R worlds/prod worlds/staging-v2` when needed.

## Python Environment
- Recommended: `python3 -m venv venv && source venv/bin/activate`
- Install dependencies as they appear (`pip install -r requirements.txt` once the file exists)
- Install dependencies as needed (no pinned requirements yet)
- Run `deactivate` when finished so future shells stay clean

## Work Tracking (Beads)
- Example epic in-flight: `[L][worlds][refactor] Multi-world state management overhaul` (see `.beads/beads.base.jsonl`).
- Create tasks with `bd create --title "[size][tags] Name" --type task` and link dependencies via `--parent`.
- Use `--json` when listing ready/status items (e.g., `bd ready --json`) to make results easy to stash in notes.

## Quick Start for Agents
1. Read `README.md` for snapshot/testing commands and the worlds directory layout.
2. Review `docs/vision/` to understand constraints before proposing changes.
3. Check Beads (`bd list`) for open issues; size/tag new work accordingly.
4. Implement in `sim.py`, helper scripts, or automation, keeping world separation intact.
5. Update knowledge base entries if process rules change (e.g., new folders, tools).
